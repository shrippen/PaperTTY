# PaperTTY

Maintained fork of [joukos/PaperTTY](https://github.com/joukos/PaperTTY) for **Raspberry Pi OS Lite (Debian Trixie)** and Waveshare SPI e-ink panels.

This tree is aimed at a **Raspberry Pi Zero 2 W** with the **[Waveshare 7.8inch e-Paper HAT](https://www.waveshare.com/wiki/7.8inch_e-Paper_HAT)** (IT8951, 1872×1404): mirror the Linux console onto the panel and autostart after console autologin.

Installer UX is inspired by [mcarr823/papertty-init](https://github.com/mcarr823/papertty-init).

## Why this fork

Upstream PaperTTY still pins Pillow 7 / click 7 and prefers RPi.GPIO-era assumptions. On Trixie (Python 3.13) that stack does not install cleanly. This fork:

- Targets Python **3.11+** (Trixie ships 3.13)
- Uses modern **Pillow** and **click 8**
- Drives SPI with **spidev** and GPIO with **gpiozero** (lgpio on Pi OS), with optional RPi.GPIO fallback
- Makes **vncdotool** optional (`pip install 'papertty[vnc]'`)
- Ships **papertty-init–compatible installers** (`install/cli.sh`, `install/gui.sh`, `install/simple.sh`) updated for Trixie, plus IT8951 VCOM handling and optional systemd boot

## Hardware

| Item | Notes |
|------|--------|
| Pi Zero 2 W | 64-bit Pi OS Lite recommended |
| Waveshare 7.8″ e-Paper HAT | IT8951 controller board + panel |
| Interface | **SPI** (set the HAT DIP switch to SPI) |
| Power | Use a solid **5V** supply; the 7.8″ panel is hungry and brownouts look like SPI hangs |

Pinout (BCM): MISO 9, MOSI 10, SCK 11, CS 8, RST 17, HRDY/BUSY 24, 5V, GND.

Read **VCOM** from the sticker on the panel FPC cable (e.g. `-1.45V`). PaperTTY wants the absolute millivolt form: `1450`.

## Installers (papertty-init compatible)

Installers live under [`install/`](install/) and keep the interactive choices from [papertty-init](https://github.com/mcarr823/papertty-init), adapted to this repo and Trixie.

| Script | When to use |
|--------|-------------|
| [`install/cli.sh`](install/cli.sh) | **Pi OS Lite** — SPI, console login options, Ubuntu Mono font, full panel list, gpiozero/RPi.GPIO choice, systemd **or** crontab `@reboot` |
| [`install/gui.sh`](install/gui.sh) | **Pi OS desktop** — XFCE autologin, tty1 **or** tmux, power-management disable, same panel/GPIO prompts |
| [`install/simple.sh`](install/simple.sh) | Venv only (Pi or PC) — no boot/SPI changes; optional vncdotool; also installs pyusb / pigpio like papertty-init |

Paths match papertty-init where useful:

- Startup script: `~/.local/bin/papertty-init/startpapertty.sh`
- Fonts: `~/.local/share/fonts/papertty-init/` (Ubuntu Mono)
- Venv: `~/.local/share/papertty/venv`

### Quick start (Pi OS Lite / Trixie)

1. Flash **Raspberry Pi OS Lite (64-bit, Trixie)** with Imager; enable SSH and set a user.
2. Attach the HAT, set DIP to **SPI**, power the Pi.
3. Clone this repo on the Pi and run:

```bash
git clone <this-repo-url> PaperTTY
cd PaperTTY
bash install/cli.sh
```

`cli.sh` prompts for:

- GPIO library (gpiozero vs RPi.GPIO; Pi 5 forces gpiozero)
- Automatic login
- Panel/driver (full Waveshare list; default **IT8951**)
- VCOM when using IT8951
- Portrait/landscape and font size (papertty-init defaults were portrait + size 30)
- Boot via **systemd** (recommended) or **crontab @reboot**

4. Optional smoke test before reboot:

```bash
sudo ~/.local/share/papertty/venv/bin/papertty --driver IT8951 --vcom 1450 scrub
~/.local/bin/papertty-init/startpapertty.sh
```

5. Reboot. After login on tty1, the e-ink should follow the console.

```bash
sudo systemctl status papertty   # if you chose systemd
sudo systemctl restart papertty
```

Edit options in `~/.local/bin/papertty-init/startpapertty.sh`.

### Desktop (gui.sh)

```bash
bash install/gui.sh
```

### Debug-only install (no boot changes)

```bash
bash install/simple.sh
sudo ~/.local/share/papertty/venv/bin/papertty --driver IT8951 --vcom 1450 terminal --autofit
```

## Manual usage

```bash
# List drivers
papertty --driver IT8951 list

# Console mirror
sudo papertty --driver IT8951 --vcom 1450 terminal --autofit \
  --font /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf

# Full clear
sudo papertty --driver IT8951 --vcom 1450 scrub
```

Smaller Waveshare SPI panels still work via drivers such as `EPD2in13` and `EPD7in5v2`.

For VNC mode:

```bash
pip install 'papertty[vnc]'
sudo papertty --driver IT8951 --vcom 1450 vnc --host localhost --display 0
```

## Development install

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
# optional
pip install -e '.[vnc,lgpio]'
```

## Design notes

```text
tty1 (/dev/vcsa1) -> PaperTTY (Pillow) -> dirty regions
                                      -> IT8951 driver
                                      -> spidev + gpiozero/lgpio
                                      -> 7.8" panel
```

- Partial updates and A2/1bpp paths remain available for IT8951 panels whose LUT is recognized (including 7.8″ `M841_TFA2812`).
- Systemd uses `RuntimeDirectory=papertty` so lgpio can create its notification sockets.

## Upstream / license

- Application code: originally CC0 (Jouko Strömmer et al.)
- Display drivers under `papertty/drivers/`: GPL-3.0 (Waveshare-derived)
- This fork keeps those terms; see `papertty/drivers/LICENSE`

Feedback and PRs welcome — especially device-tested VCOM defaults and Trixie packaging fixes.
