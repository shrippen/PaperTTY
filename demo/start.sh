#!/usr/bin/env bash
# Shows the demo session (Studio Weber's studio-pi, the shrippen demo world) with PaperTTY.
#   demo/start.sh [de|en] [papertty options before "stdin", e.g. --driver EPD7in5]
# Default driver: Bitmap (writes bitmap_frame_0.png here, no display needed).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LANG_="${1:-de}"; shift || true
[ $# -gt 0 ] || set -- --driver Bitmap
python3 "${HERE}/render.py" session "${LANG_}" | PYTHONPATH="${HERE}/.." python3 -c "from papertty.papertty import cli; cli()" "$@" stdin
