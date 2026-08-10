# PaperTTY

A personal, **vibe-coded** fork of [joukos/PaperTTY](https://github.com/joukos/PaperTTY): render a Linux virtual console (or VNC / framebuffer / image) on affordable SPI e-ink displays, typically from a Raspberry Pi.

## Intention of this repository

This is **not** a polished product or a promise of ongoing professional maintenance.

- **Primary goal:** make PaperTTY useful for my own setup on current Raspberry Pi OS.
- **Secondary goal:** share the result in case it helps someone else.
- **I am not a coder.** Large parts of this fork were produced with AI assistance (“vibe coding”). Treat the code as best-effort: read it, test it, and expect rough edges.
- Upstream PaperTTY and [papertty-init](https://github.com/mcarr823/papertty-init) remain the historical sources of truth for design; this repo is a practical update layer on top.

If something works for you, great. If it breaks, issues and PRs from people who know what they’re doing are welcome — please be patient and specific.

## Why this fork exists

Upstream development has slowed, and the old dependency stack no longer installs cleanly on current Raspberry Pi OS. This fork keeps the same CLI idea, with packaging and GPIO/SPI updates for modern Pi OS, plus installers based on papertty-init.

- Python **3.11+** (including Raspberry Pi OS **Trixie** / Python 3.13)
- Modern **Pillow** and **click 8**
- SPI via **spidev**; GPIO via **gpiozero** (lgpio on current Pi OS), with optional **RPi.GPIO** fallback
- **vncdotool** optional (`pip install 'papertty[vnc]'`)
- Top-level **`--vcom`** for IT8951 panels
- Installers for Lite, desktop, and venv-only setups

## Supported displays

Drivers fall into two buckets:

1. **Upstream / older ports** — the classic Waveshare SPI drivers that shipped with joukos/PaperTTY (still largely untested by me; some were tested by upstream authors years ago).
2. **Experimental (this fork)** — newer V2/V3/V4/HD/color ports in [`papertty/drivers/drivers_extended.py`](papertty/drivers/drivers_extended.py). These were vibe-coded from Waveshare demos and **have not been run on real panels**. They print a warning at init.

List everything with:

```bash
papertty --driver EPD2in13 list
```

Per-panel notes: [`wiki/Home.md`](wiki/Home.md) (⚠️ marks experimental drivers).

| Driver | Notes |
|--------|--------|
| `EPD2in13` / `v2` | Older 2.13″ revisions (upstream) |
| `EPD2in13v3` / `v4` ⚠️ | Newer 2.13″ / HAT+ — **experimental** |
| `EPD7in5v2` | Common 7.5″ V2 (upstream) |
| `EPD7in5_HD` ⚠️ | 7.5″ HD — **experimental**, not the same as V2 |
| `IT8951` | HD IT8951 boards (6″, 7.8″, 9.7″, 10.3″, …); needs `--vcom` |

For IT8951, set **`--vcom`** from the FPC sticker (e.g. `-1.45V` → `--vcom 1450`).

Typical HAT wiring (BCM): RST 17, DC 25, CS 8, BUSY 24, SPI0. Enable SPI (`raspi-config`).

## Installers

| Script | When to use |
|--------|-------------|
| [`install/cli.sh`](install/cli.sh) | **Raspberry Pi OS Lite** — SPI, optional console autologin, fonts, panel/GPIO prompts, systemd **or** crontab |
| [`install/gui.sh`](install/gui.sh) | **Raspberry Pi OS desktop** — XFCE autologin, tty1 or tmux |
| [`install/simple.sh`](install/simple.sh) | Venv only — no boot/SPI changes |

Paths (papertty-init compatible):

- Startup script: `~/.local/bin/papertty-init/startpapertty.sh`
- Fonts: `~/.local/share/fonts/papertty-init/`
- Venv: `~/.local/share/papertty/venv`

### Lite

```bash
git clone https://github.com/shrippen/PaperTTY.git PaperTTY
cd PaperTTY
bash install/cli.sh
```

### Desktop / venv-only

```bash
bash install/gui.sh      # desktop
bash install/simple.sh   # venv only
```

## Manual usage

```bash
papertty --driver EPD2in13 list

sudo papertty --driver EPD2in13 terminal --autofit

sudo papertty --driver IT8951 --vcom 1450 terminal --autofit \
  --font /usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf

sudo papertty --driver EPD2in13 scrub
sudo papertty --driver IT8951 --vcom 1450 scrub
```

VNC (optional):

```bash
pip install 'papertty[vnc]'
sudo papertty --driver EPD2in13 vnc --host localhost --display 0
```

## Development install

```bash
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -e .
pip install -e '.[vnc,lgpio,usb]'   # optional
```

## How it works

```text
tty / VNC / fb / image  ->  PaperTTY (Pillow)  ->  dirty regions
                                              ->  display driver
                                              ->  SPI + GPIO
                                              ->  e-ink panel
```

## Requirements

- Raspberry Pi (or compatible) with SPI for real hardware
- Raspberry Pi OS **Bookworm** or **Trixie** recommended
- Adequate 5V supply for larger panels

## Upstream / license

- Application code: originally CC0 (Jouko Strömmer et al.)
- Display drivers under `papertty/drivers/`: GPL-3.0 (Waveshare-derived)
- See [`papertty/drivers/LICENSE`](papertty/drivers/LICENSE)

## Disclaimer

Use at your own risk. E-ink panels and SPI HATs can misbehave; experimental drivers especially may do the wrong thing. I cannot support every board or OS image. Shared in the hope it is useful — not as a guarantee that it is.
