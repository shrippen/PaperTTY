#!/usr/bin/env bash
# Landing-page screenshot for shrippen.github.io/tools/screenshots.py (demo/shots.json).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${SHOT_DIR:-${HERE}/../build/demo-shots}"
mkdir -p "${OUT}"
python3 "${HERE}/render.py" shot "${OUT}/terminal.png" "${DEMO_LANG:-de}"
