# EPD7in5_HD

> **EXPERIMENTAL** — vibe-coded / untested on hardware.

**7.5inch HD e-Paper**

Waveshare 7.5" HD - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD7in5_HD` |
| Resolution | 880×528 |
| Partial refresh | No (full refresh) |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD7in5_HD terminal --autofit
```

Installer panel list entry: `EPD7in5_HD`.

Scrub / clear:

```bash
sudo papertty --driver EPD7in5_HD scrub
```



## Hardware notes

880×528 mono SSD1677 — not the same as EPD7in5v2.

[Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_HD_e-Paper_HAT)

## Pinout (typical Waveshare HAT, BCM)

| Signal | BCM |
|--------|-----|
| RST | 17 |
| DC | 25 |
| CS | 8 |
| BUSY | 24 |
| MOSI / SCLK | SPI0 |

Always enable SPI and use a power supply that can handle the panel's peak current.

## Status

**EXPERIMENTAL.** This driver was added with AI assistance (“vibe coded”) and has **not** been tested on real hardware. It may damage nothing but can easily mis-refresh or hang SPI. Prefer a non-experimental driver when one matches your panel sticker. Reports and fixes are welcome.
