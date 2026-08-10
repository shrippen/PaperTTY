#!/usr/bin/env bash
# Full Lite installer — papertty-init cli.sh functionality, adapted for this
# vibe-coded PaperTTY fork on Raspberry Pi OS Lite (Bookworm/Trixie).
#
# From a clone:
#   bash install/cli.sh
#
# From a Pi (no clone), like papertty-init:
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/shrippen/PaperTTY/main/install/cli.sh)"

set -euo pipefail

# --- remote one-liner bootstrap (curl | bash / bash -c "$(curl …)") -----------
_PAPERTTTY_SELF="${BASH_SOURCE[0]:-}"
if [[ ! -n "${_PAPERTTTY_SELF}" || ! -f "${_PAPERTTTY_SELF}" || ! -f "$(dirname "${_PAPERTTTY_SELF}")/common.sh" ]]; then
  REPO_URL="${PAPERTTTY_REPO_URL:-https://github.com/shrippen/PaperTTY.git}"
  REF="${PAPERTTTY_REF:-main}"
  DEST="${PAPERTTTY_SRC:-${HOME}/.local/share/papertty/src}"
  echo "PaperTTY installer: fetching ${REPO_URL} (${REF}) → ${DEST}"
  if ! command -v git >/dev/null 2>&1; then
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git
  fi
  if [[ -d "${DEST}/.git" ]]; then
    git -C "${DEST}" fetch --depth 1 origin "${REF}"
    git -C "${DEST}" checkout -qf FETCH_HEAD 2>/dev/null || git -C "${DEST}" checkout -qf "${REF}"
  else
    rm -rf "${DEST}"
    mkdir -p "$(dirname "${DEST}")"
    git clone --depth 1 --branch "${REF}" "${REPO_URL}" "${DEST}"
  fi
  exec bash "${DEST}/install/cli.sh" "$@"
fi
# ------------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${_PAPERTTTY_SELF}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FONTDIR="${HOME}/.local/share/fonts/papertty-init"
BINDIR="${HOME}/.local/bin/papertty-init"
INSTALL_ROOT="${HOME}/.local/share/papertty"
VENV_DIR="${INSTALL_ROOT}/venv"
SERVICE_NAME="papertty.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}"

require_not_root
command -v sudo >/dev/null 2>&1 || die "sudo is required."

echo ""
echo "*********************"
echo "* PaperTTY CLI Init *"
echo "*********************"
echo ""
echo "This script will set up a Raspberry Pi to automatically run PaperTTY on boot."
echo "It is intended for a text-only environment (Raspberry Pi OS Lite)."
echo ""
echo "You can run it from a GUI image if you want, but the Pi will then boot"
echo "straight to the console. For a desktop setup, use: bash install/gui.sh"
echo ""
echo "This installs PaperTTY from:"
echo "  ${REPO_ROOT}"
echo ""
echo "Intended for Raspberry Pi OS Lite (Bookworm or Trixie) on a Raspberry Pi."
echo ""

detect_pi5
if [ -f /etc/os-release ]; then
  # shellcheck disable=SC1091
  . /etc/os-release
  echo "OS: ${PRETTY_NAME:-unknown} (${VERSION_CODENAME:-unknown})"
fi

echo ""
yes_or_no "Do you want to continue?" || die "Aborting installation"

echo ""
echo "You will now be asked a few questions about your desired setup."

# --- #1 GPIO library (papertty-init) ---
echo ""
echo ""
echo "#1 GPIO library"
echo "Which GPIO library do you want to use?"
echo "There are 2 options: gpiozero and RPi.GPIO"
echo ""
echo "RPi.GPIO has been used with PaperTTY for longer and is well-tested."
echo "It does not work on Raspberry Pi 5 or newer."
echo ""
echo "gpiozero is regularly updated and works on newer devices (with lgpio)."
echo "On current Raspberry Pi OS, gpiozero + spidev is the recommended default."
echo ""
USE_GPIOZERO=1
if [ "${PI5}" -eq 1 ]; then
  echo "Raspberry Pi 5 detected: gpiozero will be used."
else
  if yes_or_no "Use gpiozero?"; then
    USE_GPIOZERO=1
  else
    USE_GPIOZERO=0
  fi
fi

# --- #2 Automatic login (papertty-init) ---
echo ""
echo ""
echo "#2 Automatic login"
AUTOLOGIN=0
if yes_or_no "Enable automatic login?"; then
  AUTOLOGIN=1
fi

# --- #3 Panel driver (papertty-init list) ---
echo ""
echo ""
echo "#3 Panel driver"
choose_panel
ask_vcom_if_needed

# --- #4 Orientation / font size (papertty-init used --portrait --size 30) ---
echo ""
echo ""
echo "#4 Display options"
echo "papertty-init defaulted to portrait mode with font size 30."
echo "Choose whatever fits your panel mounting."
PORTRAIT=1
if yes_or_no "Use portrait orientation?"; then
  PORTRAIT=1
else
  PORTRAIT=0
fi

FONT_SIZE=30
echo ""
read -r -p "Font size [${FONT_SIZE}]: " size_in || true
if [ -n "${size_in}" ]; then
  FONT_SIZE="${size_in}"
fi

# --- #5 Boot mechanism (systemd recommended; crontab kept for papertty-init parity) ---
echo ""
echo ""
echo "#5 Start PaperTTY on boot via"
echo "  1) systemd unit (recommended)"
echo "  2) crontab @reboot (papertty-init style)"
BOOT_MODE="systemd"
while true; do
  read -r -p "Choose 1 or 2 [1]: " boot_in || true
  boot_in="${boot_in:-1}"
  case "${boot_in}" in
    1) BOOT_MODE="systemd"; break ;;
    2) BOOT_MODE="crontab"; break ;;
  esac
done

EXTRA_ARGS="--autofit --size ${FONT_SIZE}"
if [ "${PORTRAIT}" -eq 1 ]; then
  EXTRA_ARGS="--autofit --portrait --size ${FONT_SIZE}"
fi

echo ""
echo "Your settings are as follows:"
echo "  PaperTTY source:  ${REPO_ROOT}"
if [ "${USE_GPIOZERO}" -eq 1 ]; then
  echo "  Library:          gpiozero"
else
  echo "  Library:          RPi.GPIO"
fi
if [ "${AUTOLOGIN}" -eq 1 ]; then
  echo "  Automatic login:  enabled"
else
  echo "  Automatic login:  disabled"
fi
echo "  Panel/driver:     ${PANEL}"
echo "  VCOM:             ${VCOM:-n/a}"
echo "  Orientation:      $( [ "${PORTRAIT}" -eq 1 ] && echo portrait || echo landscape )"
echo "  Font size:        ${FONT_SIZE}"
echo "  Boot mechanism:   ${BOOT_MODE}"
echo ""
echo "Is this all correct?"
echo "Installation will start immediately if you say yes."
yes_or_no "Proceed?" || die "Aborting installation"

echo ""
echo "Creating setup directories"
mkdir -p "${FONTDIR}" "${BINDIR}" "${INSTALL_ROOT}"

echo "Updating apt cache / installing dependencies"
apt_common_deps

echo "Creating python virtual environment - this might take a minute"
create_venv_and_install_papertty "${VENV_DIR}" "${REPO_ROOT}" "${USE_GPIOZERO}"

install_ubuntu_fonts "${FONTDIR}"
FONT="${FONTDIR}/UbuntuMono-R.ttf"
if [ ! -f "${FONT}" ]; then
  echo "Warning: UbuntuMono-R.ttf missing; falling back to DejaVu Sans Mono"
  FONT="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
fi

echo "Creating papertty startup script: ${BINDIR}/startpapertty.sh"
write_startpapertty_sh "${BINDIR}/startpapertty.sh" "${VENV_DIR}" "${PANEL}" "${FONT}" "${EXTRA_ARGS}" "${VCOM}"

echo "Enabling SPI"
if command -v raspi-config >/dev/null 2>&1; then
  sudo raspi-config nonint do_spi 0
  echo "Updating login preference"
  if [ "${AUTOLOGIN}" -eq 1 ]; then
    # B2 = console boot, autologin
    sudo raspi-config nonint do_boot_behaviour B2
  else
    # B1 = console boot, requiring login
    sudo raspi-config nonint do_boot_behaviour B1
  fi
  echo "Disabling splash screen"
  sudo raspi-config nonint do_boot_splash 1 || true
else
  echo "Warning: raspi-config not found; enable SPI / login behaviour manually."
fi

if [ "${BOOT_MODE}" = "systemd" ]; then
  echo "Installing systemd unit ${SERVICE_PATH}"
  # Disable leftover crontab entry from a previous papertty-init install if present
  if crontab -l 2>/dev/null | grep -q 'startpapertty.sh'; then
    echo "Removing previous startpapertty.sh crontab entries"
    crontab -l 2>/dev/null | grep -v 'startpapertty.sh' | crontab - || true
  fi
  TMP_UNIT="$(mktemp)"
  {
    cat <<EOF
[Unit]
Description=PaperTTY e-ink console mirror
After=multi-user.target
Wants=multi-user.target

[Service]
Type=simple
ExecStart=${BINDIR}/startpapertty.sh
KillSignal=SIGINT
TimeoutStopSec=15
Restart=on-failure
RestartSec=3
RuntimeDirectory=papertty
WorkingDirectory=/run/papertty

[Install]
WantedBy=multi-user.target
EOF
  } > "${TMP_UNIT}"
  sudo install -m 0644 "${TMP_UNIT}" "${SERVICE_PATH}"
  rm -f "${TMP_UNIT}"
  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}"
else
  echo "Checking crontab"
  if crontab -l >"${HOME}/old-crontab.txt" 2>/dev/null; then
    if [ -s "${HOME}/old-crontab.txt" ]; then
      echo "Backing up crontab to: ${HOME}/old-crontab.txt"
      cp "${HOME}/old-crontab.txt" "${HOME}/new-crontab.txt"
    else
      rm -f "${HOME}/old-crontab.txt"
      : >"${HOME}/new-crontab.txt"
      echo "Old crontab was empty - not backing up"
    fi
  else
    : >"${HOME}/new-crontab.txt"
    echo "Old crontab was empty - not backing up"
  fi
  # Drop previous papertty start lines, then append ours (papertty-init style)
  grep -v 'startpapertty.sh' "${HOME}/new-crontab.txt" >"${HOME}/new-crontab.filtered.txt" || true
  mv "${HOME}/new-crontab.filtered.txt" "${HOME}/new-crontab.txt"
  echo "@reboot ${BINDIR}/startpapertty.sh" >>"${HOME}/new-crontab.txt"
  crontab "${HOME}/new-crontab.txt"
  rm -f "${HOME}/new-crontab.txt"
  # Avoid double-start if a previous systemd unit exists
  if [ -f "${SERVICE_PATH}" ]; then
    sudo systemctl disable --now "${SERVICE_NAME}" 2>/dev/null || true
  fi
fi

echo ""
echo ""
echo "Installation has finished."
echo "You will need to reboot before the changes take effect."
echo ""
echo "Note that you may still need to edit the papertty startup script to suit your preferences."
echo "e.g. To change the font, font size, screen orientation, VCOM, etc."
echo "The startup script can be found at: ${BINDIR}/startpapertty.sh"
echo ""
if [ "${PANEL}" = "IT8951" ]; then
  echo "IT8951 checklist:"
  echo "  - Interface mode set to SPI (or use USB if that is how you connected)"
  echo "  - Adequate 5V supply (larger panels draw more current)"
  echo ""
  echo "Quick test:"
  echo "  sudo ${VENV_DIR}/bin/papertty --driver ${PANEL} --vcom ${VCOM} scrub"
else
  echo "Quick test:"
  echo "  sudo ${VENV_DIR}/bin/papertty --driver ${PANEL} scrub"
fi
echo "  ${BINDIR}/startpapertty.sh"
if [ "${BOOT_MODE}" = "systemd" ]; then
  echo ""
  echo "Service control: sudo systemctl status|restart|stop ${SERVICE_NAME}"
fi
