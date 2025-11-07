#!/usr/bin/env bash
# Helper script to grant Docker containers access to the host X11 display.
set -euo pipefail

DEFAULT_DISPLAY=":0"
DISPLAY_ENV="${DISPLAY:-$DEFAULT_DISPLAY}"
WRITE_ENV_FILE=""

usage() {
  cat <<'EOF'
Usage: scripts/setup-x11.sh [--write-env [/path/to/.env]]

Without arguments the script prints the required export commands. Pass
--write-env (optionally with a path) to also write a Compose-compatible .env
file so you can run `sudo docker compose --env-file <file> up --build` without
having to preserve every environment variable manually.
EOF
}

while (($#)); do
  case "$1" in
    --write-env)
      if (($# < 2)); then
        WRITE_ENV_FILE=".env"
        shift 1
      else
        WRITE_ENV_FILE="$2"
        shift 2
      fi
      ;;
    --write-env=*)
      WRITE_ENV_FILE="${1#*=}"
      shift 1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 1
      ;;
  esac
done

log() {
  printf '[setup-x11] %s\n' "$*" >&2
}

ensure_xauthority() {
  local auth_file
  auth_file=$(xauth info 2>/dev/null | awk '/Authority file/ {print $3}')

  if [[ -z "${auth_file:-}" ]]; then
    auth_file="$HOME/.Xauthority"
  fi

  # Remove stale lock if present.
  rm -f "${auth_file}-c" 2>/dev/null || true

  if [[ ! -f "$auth_file" ]]; then
    log "Creating Xauthority file at $auth_file"
    touch "$auth_file"
    chmod 600 "$auth_file"
  fi

  if ! xauth list "$DISPLAY_ENV" >/dev/null 2>&1; then
    log "Generating MIT-MAGIC-COOKIE for display $DISPLAY_ENV"
    local generate_cmd=(xauth generate "$DISPLAY_ENV" . trusted)
    if command -v timeout >/dev/null 2>&1; then
      if ! timeout 5 "${generate_cmd[@]}" >/dev/null 2>&1; then
        cookie=$(python - <<'PY'
import secrets
print(secrets.token_hex(16))
PY
)
        xauth add "$DISPLAY_ENV" . "$cookie" >/dev/null 2>&1
      fi
    else
      if ! "${generate_cmd[@]}" >/dev/null 2>&1; then
        cookie=$(python - <<'PY'
import secrets
print(secrets.token_hex(16))
PY
)
        xauth add "$DISPLAY_ENV" . "$cookie" >/dev/null 2>&1
      fi
    fi
  fi

  printf '%s' "$auth_file"
}

grant_xhost() {
  log "Granting local root access to X server"
  if ! xhost +SI:localuser:root >/dev/null 2>&1; then
    log "Warning: unable to contact X server; continuing without adjusting xhost."
  fi
}

detect_xdg_runtime_dir() {
  local uid="$1"

  if [[ -n "${XDG_RUNTIME_DIR:-}" && -d "${XDG_RUNTIME_DIR:-}" ]]; then
    printf '%s\n' "${XDG_RUNTIME_DIR}"
    return 0
  fi

  if command -v loginctl >/dev/null 2>&1; then
    local runtime_path
    if command -v timeout >/dev/null 2>&1; then
      runtime_path=$(timeout 3 loginctl show-user "${uid}" -p RuntimePath 2>/dev/null | awk -F= '/RuntimePath=/ {print $2}')
    else
      runtime_path=$(loginctl show-user "${uid}" -p RuntimePath 2>/dev/null | awk -F= '/RuntimePath=/ {print $2}')
    fi
    if [[ -n "${runtime_path:-}" && -d "${runtime_path:-}" ]]; then
      printf '%s\n' "${runtime_path}"
      return 0
    fi
  fi

  local fallback="/run/user/${uid}"
  if [[ -d "${fallback}" ]]; then
    printf '%s\n' "${fallback}"
    return 0
  fi

  return 1
}

main() {
  log "Using display ${DISPLAY_ENV}"

  grant_xhost
  AUTH_FILE=$(ensure_xauthority)

  local host_uid host_gid
  host_uid=$(id -u)
  host_gid=$(id -g)

  local resolved_runtime_dir=""
  if resolved_runtime_dir=$(detect_xdg_runtime_dir "${host_uid}"); then
    log "Detected XDG_RUNTIME_DIR at ${resolved_runtime_dir}"
  fi

  local default_runtime_dir="/tmp/puddle2-runtime"
  local default_pulse_socket="${default_runtime_dir}/pulse/native"
  local container_pulse_socket_default="/tmp/pulseaudio-bridge/native"
  local container_cookie_default="/tmp/pulseaudio-bridge/cookie"
  local pulse_socket="${PULSE_SOCKET:-}"
  local container_pulse_socket="${PULSE_CONTAINER_SOCKET:-$container_pulse_socket_default}"
  local pulse_server="${PULSE_SERVER:-}"
  local pulse_cookie="${PULSE_COOKIE:-}"
  local pulse_version=""
  local pulse_major=""
  local pulse_clientconfig="${PULSE_CLIENTCONFIG:-}"
  local detected_server=""
  local detected_socket=""
  local pulse_ready=0

  local pipewire_runtime_dir="${PIPEWIRE_RUNTIME_DIR:-${resolved_runtime_dir:-}}"
  local container_pipewire_runtime="/tmp/pipewire-bridge"
  local pipewire_socket=""
  local pipewire_remote_default="unix:/tmp/pipewire-bridge/pipewire-0"
  local pipewire_remote_value=""
  local gst_pipewire_remote="${GST_PIPEWIRE_REMOTE:-}"
  local gst_plugin_feature_rank="${GST_PLUGIN_FEATURE_RANK:-}"
  local gst_audio_sink="${GST_AUDIO_SINK:-}"

  detect_pipewire_socket() {
    local runtime_dir="$1"
    if [[ -n "$runtime_dir" && -S "$runtime_dir/pipewire-0" ]]; then
      pipewire_runtime_dir="$runtime_dir"
      pipewire_socket="$runtime_dir/pipewire-0"
      log "Detected PipeWire socket at $pipewire_socket"
      return 0
    fi
    return 1
  }

  if [[ -z "$pipewire_runtime_dir" ]]; then
    if [[ -n "${resolved_runtime_dir:-}" ]]; then
      detect_pipewire_socket "$resolved_runtime_dir" || true
    elif [[ -n "${XDG_RUNTIME_DIR:-}" ]]; then
      detect_pipewire_socket "$XDG_RUNTIME_DIR" || true
    fi
  else
    detect_pipewire_socket "$pipewire_runtime_dir" || true
  fi

  if [[ -z "$pipewire_socket" ]]; then
    local user_runtime=""
    # Fall back to the current user's runtime dir if accessible.
    if command -v loginctl >/dev/null 2>&1; then
      if command -v timeout >/dev/null 2>&1; then
        user_runtime=$(timeout 3 loginctl show-user "$(id -u)" -p RuntimePath 2>/dev/null | awk -F= '/RuntimePath=/ {print $2}')
      else
        user_runtime=$(loginctl show-user "$(id -u)" -p RuntimePath 2>/dev/null | awk -F= '/RuntimePath=/ {print $2}')
      fi
      if [[ -n "$user_runtime" ]]; then
        detect_pipewire_socket "$user_runtime" || true
      fi
    fi
  fi

  if [[ -z "$pipewire_socket" ]]; then
    log "PipeWire socket not detected; audio fallback via PipeWire will be unavailable. Use 'docker compose -f docker-compose.yml -f docker-compose.alsa.yml up' to pass /dev/snd directly."
    pipewire_runtime_dir=""
  fi
  if [[ -n "$pipewire_socket" ]]; then
    pipewire_remote_value="$pipewire_remote_default"
    if [[ -z "$gst_pipewire_remote" ]]; then
      gst_pipewire_remote="$pipewire_remote_value"
    fi
    if [[ -z "$gst_plugin_feature_rank" ]]; then
      gst_plugin_feature_rank="pipewiresink:33000,pulsesink:0"
    fi
    if [[ -z "$gst_audio_sink" ]]; then
      gst_audio_sink="pipewiresink"
    fi
  fi

  if command -v pactl >/dev/null 2>&1; then
    if pulse_info=$(pactl info 2>/dev/null); then
      pulse_ready=1
      detected_server=$(printf '%s\n' "$pulse_info" | awk -F': ' '/^Server String:/ {print $2; exit}')
      case "$detected_server" in
        unix:* )
          detected_socket="${detected_server#unix:}"
          ;;
        /* )
          detected_socket="$detected_server"
          detected_server="unix:$detected_server"
          ;;
      esac

      if [[ -z "${PULSE_SOCKET:-}" && -n "$detected_socket" && -S "$detected_socket" ]]; then
        pulse_socket="$detected_socket"
        log "Using host PulseAudio socket at $pulse_socket"
      fi
    else
      log "PulseAudio not running; audio forwarding disabled."
      log "Tip: restart pipewire's PulseAudio shim with 'systemctl --user restart pipewire pipewire-pulse wireplumber'."
    fi
  else
    log "pactl not found; skipping PulseAudio socket setup."
  fi

  if command -v pulseaudio >/dev/null 2>&1; then
    pulse_version=$(pulseaudio --version 2>/dev/null | awk '{print $NF}')
    pulse_major=$(printf '%s' "$pulse_version" | awk -F. '{print $1}')
    if [[ "$pulse_major" =~ ^[0-9]+$ ]]; then
      if [[ "$pulse_major" -ge 7 && "$pulse_major" -le 9 ]]; then
        pulse_clientconfig="/etc/pulse/client-noshm.conf"
        log "PulseAudio ${pulse_version} detected; exporting PULSE_CLIENTCONFIG=${pulse_clientconfig} to disable shared memory."
      fi
    fi
  fi

  if [[ -z "$pulse_socket" && -n "${resolved_runtime_dir:-}" && -S "${resolved_runtime_dir}/pulse/native" ]]; then
    pulse_socket="${resolved_runtime_dir}/pulse/native"
  fi

  if [[ -z "$pulse_socket" ]]; then
    pulse_socket="$default_pulse_socket"
  fi

  if [[ "$pulse_socket" == "$default_pulse_socket" ]]; then
    mkdir -p "$(dirname "$pulse_socket")"
    if [[ -S "$pulse_socket" ]]; then
      log "PulseAudio socket already present at $pulse_socket"
    elif [[ $pulse_ready -eq 1 ]]; then
      log "Creating PulseAudio socket at $pulse_socket"
      if pactl load-module module-native-protocol-unix \
        auth-anonymous=1 socket="$pulse_socket" >/dev/null 2>&1; then
        if [[ -S "$pulse_socket" ]]; then
          log "PulseAudio socket ready at $pulse_socket"
        else
          log "PulseAudio module loaded but socket $pulse_socket not detected."
        fi
      else
        log "Failed to load PulseAudio native protocol; audio forwarding may be unavailable."
      fi
    else
      log "PulseAudio service unavailable; cannot create socket at $pulse_socket."
    fi
  fi

  if [[ -z "${resolved_runtime_dir:-}" && "$pulse_socket" == "$default_pulse_socket" ]]; then
    resolved_runtime_dir="$default_runtime_dir"
    log "Falling back to runtime directory ${resolved_runtime_dir}"
  fi

  local container_pulse_dir
  container_pulse_dir=$(dirname "$container_pulse_socket")
  local container_cookie_path="${PULSE_COOKIE_CONTAINER:-$container_cookie_default}"

  if [[ -z "$pulse_server" ]]; then
    pulse_server="unix:${container_pulse_socket}"
  fi

  if [[ -z "$pulse_cookie" ]]; then
    if [[ -n "${resolved_runtime_dir:-}" && -f "${resolved_runtime_dir}/pulse/cookie" ]]; then
      pulse_cookie="${resolved_runtime_dir}/pulse/cookie"
    else
      local socket_dir
      socket_dir=$(dirname "$pulse_socket" 2>/dev/null || printf '')
      if [[ -n "$socket_dir" && -f "$socket_dir/cookie" ]]; then
        pulse_cookie="$socket_dir/cookie"
      else
        pulse_cookie="$HOME/.config/pulse/cookie"
      fi
    fi
  fi

  local env_file_lines
  env_file_lines=$(cat <<EOF
DISPLAY=${DISPLAY_ENV}
XAUTHORITY=${AUTH_FILE}
HOME=${HOME}
PULSE_SOCKET=${pulse_socket}
PULSE_CONTAINER_SOCKET=${container_pulse_socket}
PULSE_SERVER=${pulse_server}
PULSE_COOKIE=${pulse_cookie}
PULSE_COOKIE_CONTAINER=${container_cookie_path}
XDG_RUNTIME_DIR=${resolved_runtime_dir:-}
PIPEWIRE_RUNTIME_DIR=${pipewire_runtime_dir}
PIPEWIRE_SOCKET=${pipewire_socket}
PIPEWIRE_REMOTE=${pipewire_remote_value}
GST_PIPEWIRE_REMOTE=${gst_pipewire_remote}
GST_PLUGIN_FEATURE_RANK=${gst_plugin_feature_rank}
GST_AUDIO_SINK=${gst_audio_sink}
PULSE_CLIENTCONFIG=${pulse_clientconfig}
PIPEWIRE_RUNTIME_DIR_CONTAINER=${container_pipewire_runtime}
DEV_UID=${host_uid}
DEV_GID=${host_gid}
EOF
)

  cat <<EOF
# Run these exports in your shell before starting Docker:
export DISPLAY=${DISPLAY_ENV}
export XAUTHORITY=${AUTH_FILE}
export PULSE_SOCKET=${pulse_socket}
export PULSE_CONTAINER_SOCKET=${container_pulse_socket}
export PULSE_SERVER=${pulse_server}
export PULSE_COOKIE=${pulse_cookie}
export PULSE_COOKIE_CONTAINER=${container_cookie_path}
${resolved_runtime_dir:+export XDG_RUNTIME_DIR=${resolved_runtime_dir}}
export PIPEWIRE_RUNTIME_DIR=${pipewire_runtime_dir}
export PIPEWIRE_SOCKET=${pipewire_socket}
export PIPEWIRE_REMOTE=${pipewire_remote_value}
export GST_PIPEWIRE_REMOTE=${gst_pipewire_remote}
export GST_PLUGIN_FEATURE_RANK=${gst_plugin_feature_rank}
export GST_AUDIO_SINK=${gst_audio_sink}
${pulse_clientconfig:+export PULSE_CLIENTCONFIG=${pulse_clientconfig}}
export PIPEWIRE_RUNTIME_DIR_CONTAINER=${container_pipewire_runtime}
export DEV_UID=${host_uid}
export DEV_GID=${host_gid}
EOF

  log "X11 permissions ready. Remember to run the exported commands in your shell."

  if [[ -n "$WRITE_ENV_FILE" ]]; then
    write_env_file "$WRITE_ENV_FILE" "$env_file_lines"
  fi
}

write_env_file() {
  local env_file="$1"
  local contents="$2"
  if [[ -z "$env_file" ]]; then
    env_file=".env"
  fi
  mkdir -p "$(dirname "$env_file")"
  local tmp_file
  tmp_file=$(mktemp)
  printf '%s\n' "$contents" >"$tmp_file"
  mv "$tmp_file" "$env_file"
  chmod 600 "$env_file"
  log "Wrote docker compose env file to ${env_file}"
  log "Run: sudo docker compose --env-file ${env_file} up --build"
}

main "$@"
