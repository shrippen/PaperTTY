# EPD5in83v2

> **EXPERIMENTAL** — vibe-coded / untested on hardware.

**5.83inch e-Paper V2**

Waveshare 5.83" V2 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD5in83v2` |
| Resolution | 648×480 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD5in83v2 terminal --autofit
```

Installer panel list entry: `EPD5in83v2`.

Scrub / clear:

```bash
sudo papertty --driver EPD5in83v2 scrub
```



## Hardware notes

UC8179 V2, 648×480.

[Waveshare wiki](https://www.waveshare.com/wiki/5.83inch_e-Paper_HAT)

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
