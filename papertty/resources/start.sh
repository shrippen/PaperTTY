#!/bin/sh
# PaperTTY startup wrapper. Prefer editing PAPERTTTY_* values here (or in the
# systemd unit Environment= lines) instead of changing the service ExecStart.
#
# For IT8951 panels, VCOM must match the FPC cable label (positive millivolts).
# Example: panel prints -1.45V -> PAPERTTTY_VCOM=1450

set -eu

INSTALL_ROOT="${PAPERTTTY_INSTALL_ROOT:-${HOME}/.local/share/papertty}"
PAPERTTTY_BIN="${INSTALL_ROOT}/venv/bin/papertty"
FONT="${PAPERTTTY_FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf}"
DRIVER="${PAPERTTTY_DRIVER:-EPD2in13}"
VCOM="${PAPERTTTY_VCOM:-}"
EXTRA_ARGS="${PAPERTTTY_EXTRA_ARGS:---autofit}"

if [ ! -x "${PAPERTTTY_BIN}" ]; then
  echo "PaperTTY binary not found at ${PAPERTTTY_BIN}" >&2
  exit 1
fi

if [ "${DRIVER}" = "IT8951" ] && [ -z "${VCOM}" ]; then
  echo "PAPERTTTY_VCOM is not set. Read VCOM from the panel FPC label" >&2
  echo "(e.g. -1.45V -> 1450) and set it in this script or the systemd unit." >&2
  exit 1
fi

if [ -n "${VCOM}" ]; then
  # shellcheck disable=SC2086
  exec "${PAPERTTTY_BIN}" --driver "${DRIVER}" --vcom "${VCOM}" terminal --font "${FONT}" ${EXTRA_ARGS}
fi

# shellcheck disable=SC2086
exec "${PAPERTTTY_BIN}" --driver "${DRIVER}" terminal --font "${FONT}" ${EXTRA_ARGS}
