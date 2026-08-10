# EPD1in54v2

> **EXPERIMENTAL** — vibe-coded / untested on hardware.

**1.54inch e-Paper V2**

Waveshare 1.54" V2 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD1in54v2` |
| Resolution | 200×200 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD1in54v2 terminal --autofit
```

Installer panel list entry: `EPD1in54v2`.

Scrub / clear:

```bash
sudo papertty --driver EPD1in54v2 scrub
```



## Hardware notes

SSD1680 revision; use this for panels labeled V2.

[Waveshare wiki](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module)

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
