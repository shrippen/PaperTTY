#!/usr/bin/env bash
# Desktop installer — papertty-init gui.sh functionality, adapted for this
# maintained fork (XFCE autologin, tty1 or tmux, PaperTTY on login).
#
# Usage (from a clone of this repository, on Raspberry Pi OS with desktop):
#   bash install/gui.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "${SCRIPT_DIR}/common.sh"

REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FONTDIR="${HOME}/.local/share/fonts/papertty-init"
BINDIR="${HOME}/.local/bin/papertty-init"
AUTODIR="${HOME}/.config/autostart"
INSTALL_ROOT="${HOME}/.local/share/papertty"
VENV_DIR="${INSTALL_ROOT}/venv"

require_not_root
command -v sudo >/dev/null 2>&1 || die "sudo is required."

echo ""
echo "*********************"
echo "* PaperTTY GUI Init *"
echo "*********************"
echo ""
echo "This script will set up a Raspberry Pi to automatically run PaperTTY on boot."
echo "It will automatically log you in as ${USER} with a desktop environment,"
echo "then either switch to tty1 or run tmux so keyboard input reaches the e-ink panel."
echo ""
echo "This script should ONLY be run on a Raspberry Pi with the full Raspberry Pi OS"
echo "desktop image (not Lite). For Lite, use: bash install/cli.sh"
echo ""
echo "This installs PaperTTY from:"
echo "  ${REPO_ROOT}"
echo ""
echo "Intended for Raspberry Pi OS with desktop (Bookworm or Trixie)."
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

# --- #1 GPIO library ---
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

# --- #2 Desktop mode (papertty-init) ---
echo ""
echo ""
echo "#2 Desktop mode"
echo "How do you want your Raspberry Pi to behave when an HDMI monitor is plugged in?"
echo ""
echo "Option 1 is to show tty1 (a text-only interface) by default."
echo "Everything you type will show on both the monitor and the e-ink panel."
echo "Press Ctrl+Alt+F7 for the desktop, Ctrl+Alt+F1 to return to tty1."
echo ""
echo "Option 2 is to send text to the e-ink panel through tmux."
echo "You get a desktop by default over HDMI, but tmux must stay focused."
echo "Popup windows and shortcuts can interrupt typing; sizing needs manual tuning."
echo ""
read -r -p "Press Enter to continue"
echo ""
echo "Option 2 is only safe if you will usually have HDMI connected."
echo "For e-ink-only use, Option 1 is strongly recommended."
echo ""
echo "You can change later via Startup Applications:"
echo "  PaperttyInitStartTmux (option 2) or PaperttyInitSwitchTty (option 1)."
echo "Enable only one of them."
echo ""
USE_TTY=1
if yes_or_no "Go with Option 1 (tty1)?"; then
  USE_TTY=1
else
  USE_TTY=0
fi

# --- #3 Panel ---
echo ""
echo ""
echo "#3 Panel driver"
choose_panel
ask_vcom_if_needed

# --- #4 Display options ---
echo ""
echo ""
echo "#4 Display options"
PORTRAIT=1
if yes_or_no "Use portrait orientation? (papertty-init default: y)"; then
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

EXTRA_ARGS="--autofit --size ${FONT_SIZE}"
if [ "${PORTRAIT}" -eq 1 ]; then
  EXTRA_ARGS="--autofit --portrait --size ${FONT_SIZE}"
fi

echo ""
echo "Your settings are as follows:"
echo "  PaperTTY source: ${REPO_ROOT}"
if [ "${USE_GPIOZERO}" -eq 1 ]; then
  echo "  Library:         gpiozero"
else
  echo "  Library:         RPi.GPIO"
fi
if [ "${USE_TTY}" -eq 1 ]; then
  echo "  Desktop mode:    tty"
else
  echo "  Desktop mode:    tmux"
fi
echo "  Panel/driver:    ${PANEL}"
echo "  VCOM:            ${VCOM:-n/a}"
echo "  Orientation:     $( [ "${PORTRAIT}" -eq 1 ] && echo portrait || echo landscape )"
echo "  Font size:       ${FONT_SIZE}"
echo ""
echo "Is this all correct?"
yes_or_no "Proceed?" || die "Aborting installation"

echo ""
echo "Creating setup directories"
mkdir -p "${FONTDIR}" "${BINDIR}" "${AUTODIR}" "${INSTALL_ROOT}"

echo "Updating apt cache / installing dependencies"
apt_common_deps
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y tmux tasksel || true

echo "Creating python virtual environment - this might take a minute"
create_venv_and_install_papertty "${VENV_DIR}" "${REPO_ROOT}" "${USE_GPIOZERO}"

install_ubuntu_fonts "${FONTDIR}"
FONT="${FONTDIR}/UbuntuMono-R.ttf"
if [ ! -f "${FONT}" ]; then
  echo "Warning: UbuntuMono-R.ttf missing; falling back to DejaVu Sans Mono"
  FONT="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
fi

echo "Creating tmux startup script: ${BINDIR}/starttmux.sh"
cat > "${BINDIR}/starttmux.sh" <<EOF
#!/bin/bash
sudo openvt -fc 1 -- sudo -u ${USER} tmux new -s main
sleep 2s
#tmux send-keys -t "main" "insert command here" ENTER
tmux set -t "main" status off
tmux attach -t "main"
EOF
chmod 0755 "${BINDIR}/starttmux.sh"

echo "Creating papertty startup script: ${BINDIR}/startpapertty.sh"
write_startpapertty_sh "${BINDIR}/startpapertty.sh" "${VENV_DIR}" "${PANEL}" "${FONT}" "${EXTRA_ARGS}" "${VCOM}"

echo "Creating power management script: ${BINDIR}/disablepm.sh"
cat > "${BINDIR}/disablepm.sh" <<'EOF'
#!/bin/bash
sleep 1s
xset -dpms
sleep 1s
xset s off
sleep 1s
xset s noblank
sleep 1s
xfce4-power-manager -q 2>/dev/null || true
EOF
chmod 0755 "${BINDIR}/disablepm.sh"

echo "Installing XFCE"
sudo tasksel install xfce-desktop || \
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y xfce4 xfce4-terminal || \
  die "Failed to install XFCE"

if [ -f /etc/lightdm/lightdm.conf ]; then
  echo "Backing up lightdm config to: /etc/lightdm/lightdm.conf.bak"
  sudo cp /etc/lightdm/lightdm.conf /etc/lightdm/lightdm.conf.bak
  echo "Enabling autologin for XFCE"
  # Match papertty-init: set autologin-session=xfce
  if grep -q '^autologin-session' /etc/lightdm/lightdm.conf; then
    sudo sed -i 's/^autologin-session.*/autologin-session=xfce/' /etc/lightdm/lightdm.conf
  else
    echo "autologin-session=xfce" | sudo tee -a /etc/lightdm/lightdm.conf >/dev/null
  fi
  if ! grep -q "^autologin-user=${USER}" /etc/lightdm/lightdm.conf; then
    echo "autologin-user=${USER}" | sudo tee -a /etc/lightdm/lightdm.conf >/dev/null
  fi
else
  echo "Warning: /etc/lightdm/lightdm.conf not found; configure desktop autologin manually."
fi

echo "Enabling SPI"
if command -v raspi-config >/dev/null 2>&1; then
  sudo raspi-config nonint do_spi 0
  echo "Disabling screen blanking"
  sudo raspi-config nonint do_blanking 1 || true
fi

if [ "${USE_TTY}" -eq 1 ]; then
  HIDETMUX=true
  HIDETTY=false
else
  HIDETMUX=false
  HIDETTY=true
fi

echo "Creating autostart applications in ${AUTODIR}"

cat > "${AUTODIR}/PaperttyInitStartTmux.desktop" <<EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=PaperttyInitStartTmux
Comment=Starts a tmux session on login
Exec=xfce4-terminal --maximize -e ${BINDIR}/starttmux.sh
RunHook=0
StartupNotify=false
Terminal=false
Hidden=${HIDETMUX}
EOF

cat > "${AUTODIR}/PaperttyInitSwitchTty.desktop" <<EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=PaperttyInitSwitchTty
Comment=Switch to tty1 on login
Exec=sudo chvt 1
RunHook=0
StartupNotify=false
Terminal=false
Hidden=${HIDETTY}
EOF

cat > "${AUTODIR}/PaperttyInitStartPaperTTY.desktop" <<EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=PaperttyInitStartPaperTTY
Comment=Starts papertty on login
Exec=${BINDIR}/startpapertty.sh
RunHook=0
StartupNotify=false
Terminal=false
Hidden=false
EOF

cat > "${AUTODIR}/PaperttyInitDisablePowerManager.desktop" <<EOF
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=PaperttyInitDisablePowerManager
Comment=Disables power manager to keep screen awake
Exec=${BINDIR}/disablepm.sh
RunHook=0
StartupNotify=false
Terminal=false
Hidden=false
EOF

if [ -f /etc/xdg/autostart/light-locker.desktop ]; then
  echo "Disabling screen locker"
  if ! grep -q '^Hidden=true' /etc/xdg/autostart/light-locker.desktop; then
    echo "Hidden=true" | sudo tee -a /etc/xdg/autostart/light-locker.desktop >/dev/null
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
