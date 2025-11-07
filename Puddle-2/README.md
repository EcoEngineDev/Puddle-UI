### Built With

- PyQt6 & Qt Multimedia
- `ytmusicapi` + `yt-dlp`
- `QT-PyQt-PySide-Custom-Widgets`
- Docker & Docker Compose v2
- `watchdog` / `watchmedo` hot reload
- GStreamer (base/good/bad/libav, ALSA, PipeWire plugins)

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting Started

### Requirements

- Docker Engine and Docker Compose v2
- Host X11 server exposed to Docker (native on most Linux desktops)
- `QT-PyQt-PySide-Custom-Widgets` (installed automatically inside the container via `requirements.txt`)
- System GStreamer libraries (the Docker image already installs everything Qt Multimedia needs)
- Outbound network access (Compose pins DNS to `1.1.1.1` and `8.8.8.8`; tweak in `docker-compose.yml` if necessary)
- YouTube Music OAuth file generated via `ytmusicapi oauth` (place it at `Puddle-2/.secrets/ytmusic_oauth.json` or update `YTMUSIC_AUTH_FILE`)

### Quick Start

1. Generate the OAuth file (see [Configuring YouTube Music Access](#configuring-youtube-music-access)).
2. Launch the dev stack:
   ```bash
   cd Puddle-2
   ./scripts/setup-x11.sh
   eval "$(./scripts/setup-x11.sh)"   # optional convenience
   docker compose up --build
   docker compose up                  # for subsequent runs
   ```

Compose mounts the repo into the container, installs dependencies (including Custom Widgets), and spawns `watchmedo auto-restart`. Saving any Python, `.ui`, QSS/SCSS, or palette JSON file forces an automatic restart so you keep a tight feedback loop.

### Running Docker With `sudo`

If your Docker daemon requires root, let the helper write a Compose-friendly `.env` file so `sudo` inherits the same PulseAudio/PipeWire/X11 paths:

1. Generate the file (repeat after every reboot or whenever your display/audio targets change):
   ```bash
   ./scripts/setup-x11.sh --write-env .env.puddle
   ```
2. Use it for every Compose command:
   ```bash
   sudo docker compose --env-file .env.puddle up --build
   sudo docker compose --env-file .env.puddle exec puddle2 python scripts/diagnose-audio.py
   ```

`.gitignore` already excludes `.env*`, so the file stays local and out of version control.

### X11 Access (Linux)

- Grant access once per reboot: `xhost +SI:localuser:root` (revoke later with `xhost -local:` if you tightened permissions using `+local:`).
- Export the correct Xauthority cookie: `export XAUTHORITY=$(xauth info | awk '/Authority file/ {print $3}')`, then start Compose from the same shell.
- Prefer running `scripts/setup-x11.sh` in every terminal—it wraps the steps above, generates a cookie when missing, and prints all required exports.

### macOS / Windows

Use an external X server (XQuartz on macOS, VcXsrv on Windows) and update the `DISPLAY` environment variable inside `docker-compose.yml` if your server listens on something other than `:0` (e.g., `host.docker.internal:0`).

<p align="right">(<a href="#top">back to top</a>)</p>

## Audio Pipeline

Qt Multimedia runs entirely inside the container, so you must forward either PulseAudio/PipeWire sockets or raw ALSA devices.

### PulseAudio / PipeWire Forwarding

1. Run the helper and eval the generated exports:
   ```bash
   eval "$(./scripts/setup-x11.sh)"
   ```
   - Classic PulseAudio setups keep working as before.
   - PipeWire-based systems get `PIPEWIRE_SOCKET`, `PIPEWIRE_RUNTIME_DIR`, `PIPEWIRE_REMOTE`, and GStreamer hints (`GST_PIPEWIRE_REMOTE`, `GST_PLUGIN_FEATURE_RANK`, `GST_AUDIO_SINK`) so the container can target the host PipeWire graph.
2. Restart the stack so Compose picks up the new env vars and bind mounts:
   ```bash
   docker compose down
   docker compose up --build
   ```

If Qt cannot see an audio output, playback buttons emit a descriptive warning. As soon as PulseAudio/PipeWire becomes reachable the backend re-checks devices without requiring a full restart.

### Diagnostics

- Set `PUDDLE_AUDIO_DEBUG=1` before `docker compose up` to log every detected Qt audio device, socket mount, and `pactl/pw-cli` status.
- Run `docker compose exec puddle2 python scripts/diagnose-audio.py` for a one-off environment snapshot (it prints the relevant env vars, checks socket permissions, and dumps Qt’s view of available outputs).

<p align="right">(<a href="#top">back to top</a>)</p>

## Project Layout

```
Puddle-2/
├── README.md
├── requirements.txt
├── main.py
├── ui/
│   └── main_window.ui
├── src/
│   ├── app.py
│   ├── helper_functions.py
│   ├── mini_player.py
│   ├── puddle_tube.py
│   ├── ui_main_window.py
│   └── utils.py
├── qss/
│   ├── style.qss
│   ├── scss/style.scss
│   └── icons/.gitkeep
├── json_styles/style.json
├── logs/custom_widgets.log
├── generated-files/new_files/.gitkeep
└── scripts/
    ├── setup-x11.sh
    ├── start-dev.sh
    └── diagnose-audio.py
```

- `main.py` – Entrypoint consumed by the hot-reload loop.
- `ui/main_window.ui` – The only Qt Designer surface; regenerate bindings via the Custom Widgets CLI.
- `src/` – Runtime code plus the generated `ui_main_window.py`, helpers, theming tools, and app bootstrap.
- `qss/scss/style.scss` – The sole human-edited stylesheet source; icons live under `qss/icons/`.
- `json_styles/style.json` – Palette definition written by the colour dialog. Keep it as the single source of truth instead of hand-editing QSS.
- `logs/custom_widgets.log` – Captures CLI output when regenerating stubs.
- `generated-files/new_files/` – Landing zone for assets produced by Custom Widgets; commit only the artifacts you actually need.
- `Dockerfile`, `docker-compose*.yml`, and `scripts/start-dev.sh` – Container workflow that installs dependencies and launches `watchmedo`.

> **Secrets:** keep OAuth files (and every other credential) in `Puddle-2/.secrets/`.
