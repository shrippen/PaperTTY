# EPD2in7b_V2

> **EXPERIMENTAL** — vibe-coded / untested on hardware.

**2.7inch e-Paper (B) V2**

Waveshare 2.7" B V2 - black / white / red (drawn as black and white)

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in7b_V2` |
| Resolution | 176×264 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in7b_V2 terminal --autofit
```

Installer panel list entry: `EPD2in7b_V2`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in7b_V2 scrub
```



## Hardware notes

V2 B/W/R revision.

[Waveshare wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_(B))

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
