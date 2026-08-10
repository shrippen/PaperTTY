#!/usr/bin/env bash
# Minimal installer — papertty-init simple.sh functionality, adapted for this
# maintained fork. Installs into a venv only (no SPI / boot / fonts changes).
#
# Usage (from a clone of this repository):
#   bash install/simple.sh
#
# Works on Raspberry Pi OS (Lite or desktop) and on Debian/Ubuntu desktops.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
INSTALL_ROOT="${HOME}/.local/share/papertty"
VENV_DIR="${INSTALL_ROOT}/venv"

require_not_root

echo ""
echo "*********************"
echo "* PaperTTY Init     *"
echo "*********************"
echo ""
echo "This script will install PaperTTY inside a Python virtual environment."
echo "It will not run papertty on boot, change system settings, or download fonts."
echo ""
echo "It can be run from a Raspberry Pi (Lite or full) or from a PC running"
echo "Debian/Ubuntu (or a derivative)."
echo ""
echo "Source tree: ${REPO_ROOT}"
echo "Venv path:   ${VENV_DIR}"
echo ""
yes_or_no "Do you want to continue?" || die "Aborting installation"

if [ -d "${VENV_DIR}" ]; then
  echo ""
  echo "${VENV_DIR} already exists."
  yes_or_no "Do you want to replace the existing venv?" || die "Aborting installation"
  echo "Deleting existing venv..."
  rm -rf "${VENV_DIR}"
fi

echo ""
echo "Creating setup directory"
mkdir -p "${INSTALL_ROOT}"

if command -v sudo >/dev/null 2>&1; then
  echo "Updating apt cache"
  sudo apt-get update || true
  echo "Installing dependencies"
  apt_common_deps || true
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3-gpiozero python3-lgpio || true
fi

echo "Creating python virtual environment"
python3 -m venv --system-site-packages "${VENV_DIR}"

echo "Installing PaperTTY and dependencies - this may take a few minutes"
"${VENV_DIR}/bin/pip" install --upgrade pip setuptools wheel
"${VENV_DIR}/bin/pip" install -e "${REPO_ROOT}"

# Mirror papertty-init simple.sh extras (modern versions)
"${VENV_DIR}/bin/pip" install \
  "spidev>=3.6" \
  "pyusb>=1.2.1" \
  "gpiozero>=2.0" \
  "lgpio>=0.2.2.0" \
  "pigpio>=1.78" \
  || true

# Optional VNC stack (was always installed by papertty-init simple.sh)
if yes_or_no "Also install VNC support (vncdotool)?"; then
  "${VENV_DIR}/bin/pip" install -e "${REPO_ROOT}[vnc]" || \
    "${VENV_DIR}/bin/pip" install "vncdotool>=1.2.0" || true
fi

echo ""
echo ""
echo "Installation has finished."
echo ""
echo "You can now run papertty from:"
echo "  ${VENV_DIR}/bin/papertty"
echo ""
echo "Example for Waveshare 7.8\" IT8951 (replace VCOM from the FPC label):"
echo "  sudo ${VENV_DIR}/bin/papertty --driver IT8951 --vcom 1450 terminal --autofit"
echo ""
echo "For boot automation on Pi OS Lite:  bash install/cli.sh"
echo "For desktop / XFCE automation:       bash install/gui.sh"
