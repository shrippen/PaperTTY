#!/bin/sh
# PaperTTY startup wrapper. Prefer editing PAPERTTTY_* values here (or in the
# systemd unit Environment= lines) instead of changing the service ExecStart.
#
# VCOM must match the FPC cable label on the panel (positive millivolts).
# Example: panel prints -1.45V -> PAPERTTTY_VCOM=1450

set -eu

INSTALL_ROOT="${PAPERTTTY_INSTALL_ROOT:-${HOME}/.local/share/papertty}"
PAPERTTTY_BIN="${INSTALL_ROOT}/venv/bin/papertty"
FONT="${PAPERTTTY_FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf}"
DRIVER="${PAPERTTTY_DRIVER:-IT8951}"
VCOM="${PAPERTTTY_VCOM:-}"
# Default: landscape autofit for the Waveshare 7.8" IT8951 (1872x1404).
# Add --portrait or --size N via PAPERTTTY_EXTRA_ARGS if needed.
EXTRA_ARGS="${PAPERTTTY_EXTRA_ARGS:---autofit}"

if [ ! -x "${PAPERTTTY_BIN}" ]; then
  echo "PaperTTY binary not found at ${PAPERTTTY_BIN}" >&2
  exit 1
fi

if [ -z "${VCOM}" ]; then
  echo "PAPERTTTY_VCOM is not set. Read VCOM from the panel FPC label" >&2
  echo "(e.g. -1.45V -> 1450) and set it in this script or the systemd unit." >&2
  exit 1
fi

# shellcheck disable=SC2086
exec "${PAPERTTTY_BIN}" --driver "${DRIVER}" terminal --vcom "${VCOM}" --font "${FONT}" ${EXTRA_ARGS}
