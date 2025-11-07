#!/usr/bin/env bash
set -euo pipefail

cd /workspace

export PYTHONPATH="${PYTHONPATH:-/workspace/src}"

exec watchmedo auto-restart \
  --patterns="*.py;*.ui;*.qss;*.scss;*.json" \
  --recursive \
  --signal=SIGTERM \
  -- \
  python main.py
