"""YouTube Music backend providing search and playback for the mini player."""

from __future__ import annotations

import inspect
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import List, Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaDevices, QMediaPlayer
from ytmusicapi import OAuthCredentials, YTMusic
from yt_dlp import YoutubeDL

LOG = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUTH_PATH = PROJECT_ROOT / ".secrets" / "ytmusic_oauth.json"


@dataclass
class Track:
    """Lightweight representation of a YouTube Music track."""

    name: str
    artist: str
    album: str
    duration_ms: int
    image_url: Optional[str]
    uri: str  # videoId


@dataclass
class PlaybackState:
    """Current playback snapshot reported by the backend."""

    track: Track
    progress_ms: int
    is_playing: bool


class YTMusicBackend:
    """High-level integration that wraps YTMusic search and QMediaPlayer playback."""

    STREAM_URL_TEMPLATE = "https://music.youtube.com/watch?v={video_id}"

    def __init__(self) -> None:
        auth_file = Path(os.getenv("YTMUSIC_AUTH_FILE", DEFAULT_AUTH_PATH))
        self.auth_file = auth_file
        self.ytmusic = self._build_client(auth_file)

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self._media_devices = QMediaDevices()
        self._media_devices.audioOutputsChanged.connect(self._on_audio_outputs_changed)
        self._audio_available = False
        self._audio_warning_logged = False
        self._active_audio_device: Optional[bytes] = None
        self._audio_debug_enabled = bool(os.getenv("PUDDLE_AUDIO_DEBUG"))
        self._diagnostics_emitted = False
        if self._audio_debug_enabled:
            self._log_audio_debug("Audio debugging enabled via PUDDLE_AUDIO_DEBUG.")
            self._log_env_snapshot()
        self._refresh_audio_outputs(initial=True)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.75)

        self.current_track: Optional[Track] = None
        self._duration_hint_ms: int = 0

        # Reusable youtube-dl options for fetching stream URLs.
        self._ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "nocheckcertificate": True,
            "skip_download": True,
            "restrictfilenames": True,
            "no_warnings": True,
            # Avoid inheriting host-level yt-dlp config that might reference cookie files.
            "ignoreconfig": True,
            "cookiefile": None,
        }

    # ------------------------------------------------------------------ Search
    def search_tracks(self, query: str, limit: int = 8) -> List[Track]:
        results = self.ytmusic.search(query, filter="songs", limit=limit)
        tracks: List[Track] = []
        for item in results:
            video_id = item.get("videoId")
            if not video_id:
                continue

            title = item.get("title") or "Unknown Title"
            artists = item.get("artists") or []
            artist_names = ", ".join(artist.get("name", "") for artist in artists if artist.get("name"))
            album = ""
            album_obj = item.get("album")
            if isinstance(album_obj, dict):
                album = album_obj.get("name") or ""

            duration_ms = self._parse_duration_ms(item)
            thumbnails = item.get("thumbnails") or []
            image_url = thumbnails[-1]["url"] if thumbnails else None

            tracks.append(
                Track(
                    name=title,
                    artist=artist_names or "Unknown Artist",
                    album=album,
                    duration_ms=duration_ms,
                    image_url=image_url,
                    uri=video_id,
                )
            )
        return tracks

    # ------------------------------------------------------------------ Playback control
    def play_track(self, track: Track) -> None:
        # Ensure the latest audio routing is picked up before attempting playback.
        self._refresh_audio_outputs(initial=False)
        if not self._audio_available:
            raise RuntimeError(
                "No audio output device detected. Enable PulseAudio/PipeWire forwarding, "
                "attach a sound device to the container, or start Docker with the ALSA override."
            )
        stream_url = self._resolve_stream(track.uri)
        if not stream_url:
            raise RuntimeError("Unable to resolve an audio stream for the requested track.")

        self.player.setSource(QUrl(stream_url))
        self.player.play()

        self.current_track = track
        if self._duration_hint_ms and self.current_track.duration_ms <= 0:
            self.current_track.duration_ms = self._duration_hint_ms

    def resume(self) -> None:
        self.player.play()

    def pause(self) -> None:
        self.player.pause()

    def stop(self) -> None:
        self.player.stop()
        self.current_track = None

    def seek(self, position_ms: int) -> None:
        self.player.setPosition(max(0, position_ms))

    def set_volume(self, percent: int) -> None:
        level = max(0.0, min(1.0, percent / 100.0))
        self.audio_output.setVolume(level)

    # ------------------------------------------------------------------ Playback state
    def current_playback(self) -> Optional[PlaybackState]:
        if not self.current_track:
            return None

        state = self.player.playbackState()
        if state == QMediaPlayer.PlaybackState.StoppedState:
            return None

        progress = int(self.player.position())
        return PlaybackState(
            track=self.current_track,
            progress_ms=progress,
            is_playing=state == QMediaPlayer.PlaybackState.PlayingState,
        )

    # ------------------------------------------------------------------ Utilities
    def shutdown(self) -> None:
        self.stop()

    def _on_audio_outputs_changed(self) -> None:
        self._refresh_audio_outputs(initial=False)

    def _refresh_audio_outputs(self, *, initial: bool) -> None:
        self._log_audio_debug("Refreshing audio outputs (initial=%s)", initial)
        audio_devices = QMediaDevices.audioOutputs()
        self._log_audio_debug("Found %d audio output device(s).", len(audio_devices))
        if audio_devices:
            default_device = QMediaDevices.defaultAudioOutput()
            if default_device.isNull():
                default_device = audio_devices[0]

            device_id = bytes(default_device.id())
            if device_id != self._active_audio_device:
                try:
                    description = default_device.description()
                except AttributeError:
                    description = ""
                pretty_name = description or device_id.hex()
                LOG.info("Audio output device ready: %s", pretty_name)
                channel_count = "n/a"
                try:
                    channel_count = default_device.maximumChannelCount()
                except AttributeError:
                    pass
                preferred_repr = "n/a"
                try:
                    preferred = default_device.preferredFormat()
                    preferred_repr = str(preferred)
                except AttributeError:
                    pass
                self._log_audio_debug(
                    "Selecting device '%s' (id=%s, channels=%s, preferred format=%s)",
                    pretty_name,
                    device_id.hex(),
                    channel_count,
                    preferred_repr,
                )
                self._active_audio_device = device_id
            for device in audio_devices:
                device_id = bytes(device.id()).hex()
                try:
                    label = device.description()
                except AttributeError:
                    label = ""
                device_channels = "n/a"
                try:
                    device_channels = device.maximumChannelCount()
                except AttributeError:
                    pass
                self._log_audio_debug(
                    "Available device: id=%s label='%s' null=%s default=%s channels=%s",
                    device_id,
                    label or "<no description>",
                    device.isNull(),
                    device == default_device,
                    device_channels,
                )
            self.audio_output.setDevice(default_device)
            self._audio_available = True
            self._audio_warning_logged = False
            return

        self._active_audio_device = None
        self._audio_available = False
        if initial or not self._audio_warning_logged:
            LOG.warning(
                "No audio output devices detected. Configure host audio forwarding, "
                "mount the PipeWire socket, or run with the ALSA override to expose /dev/snd."
            )
            self._audio_warning_logged = True
        self._emit_audio_diagnostics()

    def _resolve_stream(self, video_id: str) -> Optional[str]:
        url = self.STREAM_URL_TEMPLATE.format(video_id=video_id)
        try:
            with YoutubeDL(self._ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as exc:  # pragma: no cover - depends on remote service
            LOG.error("yt-dlp failed to resolve stream for %s: %s", video_id, exc)
            return None

        self._duration_hint_ms = int(info.get("duration", 0) * 1000)

        stream_url = info.get("url")
        if not stream_url:
            formats = info.get("formats") or []
            if formats:
                stream_url = formats[-1].get("url")
        return stream_url

    # ------------------------------------------------------------------ Diagnostics
    def _log_audio_debug(self, message: str, *args: object) -> None:
        if not self._audio_debug_enabled:
            return
        LOG.debug("[audio-debug] " + message, *args)

    def _emit_audio_diagnostics(self) -> None:
        if not self._audio_debug_enabled or self._diagnostics_emitted:
            return
        self._diagnostics_emitted = True
        self._log_audio_debug("Capturing extended audio diagnostics.")
        self._log_env_snapshot()
        self._check_socket("PULSE_CONTAINER_SOCKET")
        self._check_socket("PULSE_SERVER")
        self._check_socket("PIPEWIRE_SOCKET")
        self._maybe_run_command(["pactl", "info"])
        self._maybe_run_command(["pw-cli", "ls", "Client"])
        self._maybe_run_command(["pw-cli", "ls", "Node"])

    def _log_env_snapshot(self) -> None:
        keys = [
            "PULSE_SERVER",
            "PULSE_CONTAINER_SOCKET",
            "PULSE_COOKIE_CONTAINER",
            "PULSE_CLIENTCONFIG",
            "PIPEWIRE_REMOTE",
            "PIPEWIRE_SOCKET",
            "PIPEWIRE_RUNTIME_DIR",
            "GST_PIPEWIRE_REMOTE",
            "GST_AUDIO_SINK",
            "QT_NO_PULSEAUDIO",
            "QT_QPA_PLATFORM",
            "XDG_RUNTIME_DIR",
        ]
        for key in keys:
            value = os.getenv(key)
            self._log_audio_debug("env %s=%s", key, value if value is not None else "<unset>")

    def _check_socket(self, key: str) -> None:
        value = os.getenv(key)
        if not value:
            self._log_audio_debug("%s not set; skipping socket check.", key)
            return
        path = value
        if path.startswith("unix:"):
            path = path[5:]
        socket_path = Path(path)
        exists = socket_path.exists()
        perms = "n/a"
        if exists:
            try:
                perms = oct(socket_path.stat().st_mode)
            except OSError as exc:  # pragma: no cover - diagnostics only
                perms = f"<stat failed: {exc}>"
        self._log_audio_debug(
            "Socket check for %s -> %s (exists=%s, perms=%s)",
            key,
            socket_path,
            exists,
            perms,
        )

    def _maybe_run_command(self, args: List[str]) -> None:
        if not args:
            return
        cmd = args[0]
        if which(cmd) is None:
            self._log_audio_debug("Skipping '%s' diagnostics; command not found.", cmd)
            return
        try:
            proc = subprocess.run(
                args,
                check=False,
                capture_output=True,
                text=True,
                timeout=6,
            )
        except Exception as exc:  # pragma: no cover - diagnostics only
            self._log_audio_debug("Command '%s' failed: %s", " ".join(args), exc)
            return
        self._log_audio_debug("Command '%s' exited %s", " ".join(args), proc.returncode)
        if proc.stdout:
            for line in proc.stdout.splitlines():
                self._log_audio_debug("%s stdout: %s", cmd, line)
        if proc.stderr:
            for line in proc.stderr.splitlines():
                self._log_audio_debug("%s stderr: %s", cmd, line)

    def _build_client(self, auth_file: Path) -> YTMusic:
        if auth_file.exists():
            try:
                return YTMusic(str(auth_file))
            except Exception as exc:  # pragma: no cover - depends on external lib
                LOG.warning(
                    "YTMusic client initialisation with auth file failed (%s); attempting manual OAuth credential fallback.",
                    exc,
                )
                try:
                    contents = auth_file.read_text(encoding="utf-8")
                    oauth_data: Optional[dict] = json.loads(contents)
                except (OSError, json.JSONDecodeError) as read_exc:
                    LOG.warning(
                        "Failed to read YTMusic OAuth credentials (%s). Continuing without authentication.",
                        read_exc,
                    )
                else:
                    if isinstance(oauth_data, dict):
                        try:
                            params = inspect.signature(OAuthCredentials).parameters
                        except (TypeError, ValueError):
                            params = {}

                        kwargs = {}
                        missing_required = []
                        for name, param in params.items():
                            if name == "self":
                                continue
                            value = oauth_data.get(name)
                            if value is None:
                                if param.default is inspect._empty:
                                    missing_required.append(name)
                                continue
                            kwargs[name] = value

                        if missing_required:
                            LOG.warning(
                                "OAuth credential file %s missing required fields: %s",
                                auth_file,
                                ", ".join(missing_required),
                            )
                        elif kwargs:
                            try:
                                credentials = OAuthCredentials(**kwargs)
                                return YTMusic(str(auth_file), oauth_credentials=credentials)
                            except Exception as cred_exc:  # pragma: no cover - depends on external lib
                                LOG.warning(
                                    "OAuth credential load failed (%s); continuing without authentication.",
                                    cred_exc,
                                )
                        else:
                            LOG.warning(
                                "OAuth credential signature mismatch; continuing without authentication."
                            )
        else:
            LOG.info("YouTube Music credentials file %s not found; using anonymous client.", auth_file)

        return YTMusic()

    @staticmethod
    def _parse_duration_ms(item: dict) -> int:
        duration_seconds = item.get("duration_seconds")
        if duration_seconds is not None:
            return int(duration_seconds) * 1000

        duration_str = item.get("duration")
        if not duration_str:
            return 0

        try:
            seconds = 0
            for part in duration_str.split(":"):
                seconds = seconds * 60 + int(part)
            return seconds * 1000
        except ValueError:
            return 0
