#!/usr/bin/env python3
"""Standalone diagnostic helper to inspect audio routing inside the dev container."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from shutil import which
from typing import Iterable

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtMultimedia import QMediaDevices


def main(argv: Iterable[str]) -> int:
    print("Puddle 2 – Audio diagnostics\n")
    app = QCoreApplication(list(argv))

    _print_env_snapshot()
    _check_socket("PULSE_CONTAINER_SOCKET")
    _check_socket("PULSE_SERVER")
    _check_socket("PIPEWIRE_SOCKET")

    print("\n--- Qt Multimedia audio outputs ---")
    devices = QMediaDevices.audioOutputs()
    default_output = QMediaDevices.defaultAudioOutput()
    if default_output.isNull() and devices:
        default_output = devices[0]
    if not devices:
        print("No audio outputs detected by Qt.")
    for device in devices:
        _print_device(device, default_output)

    print("\n--- pactl info ---")
    _run_command(["pactl", "info"])
    print("\n--- pw-cli ls Client ---")
    _run_command(["pw-cli", "ls", "Client"])
    print("\n--- pw-cli ls Node ---")
    _run_command(["pw-cli", "ls", "Node"])

    # Avoid starting the Qt event loop – diagnostics only.
    return 0


def _print_env_snapshot() -> None:
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
    print("--- Environment snapshot ---")
    for key in keys:
        value = os.getenv(key, "<unset>")
        print(f"{key}={value}")


def _check_socket(key: str) -> None:
    value = os.getenv(key)
    if not value:
        print(f"{key}: not set")
        return
    path = value[5:] if value.startswith("unix:") else value
    socket_path = Path(path)
    exists = socket_path.exists()
    perms: str
    try:
        perms = oct(socket_path.stat().st_mode) if exists else "n/a"
    except OSError as exc:
        perms = f"<stat failed: {exc}>"
    print(f"{key}: {socket_path} (exists={exists}, perms={perms})")


def _print_device(device, default_output) -> None:
    description = getattr(device, "description", lambda: "")()
    device_id = bytes(device.id()).hex()
    is_default = device == default_output
    is_null = device.isNull()
    label = description or "<no description>"
    try:
        channels = device.maximumChannelCount()
    except AttributeError:
        channels = "n/a"
    try:
        preferred_format = str(device.preferredFormat())
    except AttributeError:
        preferred_format = "n/a"
    print(
        f"• id={device_id} label='{label}' "
        f"default={is_default} null={is_null} channels={channels} "
        f"preferred_format={preferred_format}"
    )


def _run_command(args: Iterable[str]) -> None:
    args = tuple(args)
    if not args:
        return
    cmd = args[0]
    if which(cmd) is None:
        print(f"{cmd} not found in PATH.")
        return
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=6,
        )
    except Exception as exc:  # pragma: no cover - diagnostics only
        print(f"{cmd}: failed to execute ({exc})")
        return
    print(f"{cmd}: exit code {result.returncode}")
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout:
        print(stdout)
    if stderr:
        print("--- stderr ---")
        print(stderr)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
