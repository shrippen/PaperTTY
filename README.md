# PaperTTY

Maintained fork of [joukos/PaperTTY](https://github.com/joukos/PaperTTY): render a Linux virtual console (or VNC / framebuffer / image) on affordable SPI e-ink displays, typically driven from a Raspberry Pi.

Upstream development has slowed, and the old dependency stack no longer installs cleanly on current Raspberry Pi OS. This fork keeps the same drivers and CLI, with packaging and GPIO/SPI updates for modern Pi OS, plus installers based on [papertty-init](https://github.com/mcarr823/papertty-init).

## Why this fork

- Python **3.11+** (including Raspberry Pi OS **Trixie** / Python 3.13)
- Modern **Pillow** and **click 8** (replaces pinned Pillow 7 / click 7)
- SPI via **spidev**; GPIO via **gpiozero** (lgpio on current Pi OS), with optional **RPi.GPIO** fallback
- **vncdotool** is optional (`pip install 'papertty[vnc]'`)
- Top-level **`--vcom`** for IT8951 panels (including `scrub`)
- Installers for Lite, desktop, and venv-only setups

## Supported displays

Most Waveshare SPI panels from upstream remain available, plus newer V2/V3/V4 and HD revisions. List them with:

```bash
papertty --driver EPD2in13 list
```

Per-panel notes live in the [`wiki/`](wiki/) directory (GitHub Wiki–compatible pages): start at [`wiki/Home.md`](wiki/Home.md).

Common choices:

| Driver | Panels (examples) |
|--------|-------------------|
| `EPD2in13v4` | Current 2.13″ V4 / HAT+ (prefer for new 2.13″ kits) |
| `EPD2in13`, `EPD2in13v2`, `EPD2in13v3` | Older 2.13″ revisions |
| `EPD2in9` / `EPD2in9v2` / `EPD2in66` | Mid-size mono modules |
| `EPD7in5v2`, `EPD7in5_HD` | 7.5″ (standard V2 vs HD — different drivers) |
| `IT8951` | HD boards (6″, 7.8″, 9.7″, 10.3″, …) — size/LUT auto-detected |

See [`papertty/drivers/README.md`](papertty/drivers/README.md) for the driver tree. For IT8951, set **`--vcom`** from the value printed on the panel FPC (e.g. `-1.45V` → `--vcom 1450`).

Typical HAT wiring (BCM): RST 17, DC 25, CS 8, BUSY 24, SPI0. Enable SPI (`raspi-config`). HD IT8951 boards also need the onboard interface switch set to **SPI** (or use USB where supported).

## Installers

| Script | When to use |
|--------|-------------|
| [`install/cli.sh`](install/cli.sh) | **Raspberry Pi OS Lite** — SPI, optional console autologin, Ubuntu Mono, panel/GPIO prompts, systemd **or** crontab `@reboot` |
| [`install/gui.sh`](install/gui.sh) | **Raspberry Pi OS desktop** — XFCE autologin, tty1 or tmux, same panel/GPIO prompts |
| [`install/simple.sh`](install/simple.sh) | Venv only (Pi or PC) — no boot/SPI changes; optional VNC extras |

Paths (papertty-init compatible):

- Startup script: `~/.local/bin/papertty-init/startpapertty.sh`
- Fonts: `~/.local/share/fonts/papertty-init/`
- Venv: `~/.local/share/papertty/venv`

### Lite (recommended for console-on-e-ink)

```bash
git clone https://github.com/shrippen/PaperTTY.git PaperTTY
cd PaperTTY
bash install/cli.sh
```

You will be asked for GPIO backend, autologin, panel driver, display options, and boot method. IT8951 installs also prompt for VCOM.

After install, reboot (or run the generated `startpapertty.sh`). With systemd:

```bash
sudo systemctl status papertty
sudo systemctl restart papertty
```

### Desktop

```bash
bash install/gui.sh
```

### Venv only

```bash
bash install/simple.sh
sudo ~/.local/share/papertty/venv/bin/papertty --driver EPD2in13 terminal --autofit
```

## Manual usage

```bash
# List drivers
papertty --driver EPD2in13 list

# Small Waveshare panel (example)
sudo papertty --driver EPD2in13 terminal --autofit

# IT8951 HD panel (VCOM from FPC label)
sudo papertty --driver IT8951 --vcom 1450 terminal --autofit \
  --font /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf

# Clear / scrub
sudo papertty --driver EPD2in13 scrub
sudo papertty --driver IT8951 --vcom 1450 scrub
```

VNC (optional extra):

```bash
pip install 'papertty[vnc]'
sudo papertty --driver EPD2in13 vnc --host localhost --display 0
```

## Development install

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
pip install -e '.[vnc,lgpio,usb]'   # optional extras
```

## How it works

```text
tty / VNC / fb / image  ->  PaperTTY (Pillow)  ->  dirty regions
                                              ->  display driver
                                              ->  SPI + GPIO
                                              ->  e-ink panel
```

Partial updates are used when the selected driver supports them. IT8951 can use faster 1bpp / A2 paths when the panel LUT allows it.

## Requirements

- Raspberry Pi (or compatible) with SPI, for real hardware
- Raspberry Pi OS **Bookworm** or **Trixie** recommended; older images may work with more effort
- Solid power supply for larger panels (undervoltage often looks like SPI failures)

## Upstream / license

- Application code: originally CC0 (Jouko Strömmer et al.)
- Display drivers under `papertty/drivers/`: GPL-3.0 (Waveshare-derived)
- This fork keeps those terms; see [`papertty/drivers/LICENSE`](papertty/drivers/LICENSE)

Issues and PRs welcome — especially for untested panel revisions and packaging on current Pi OS.
