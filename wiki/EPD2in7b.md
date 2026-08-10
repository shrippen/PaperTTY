# EPD2in7b

**2.7inch e-Paper (B)**

Waveshare 2.7" B - black / white / red

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in7b` |
| Resolution | 176×264 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in7b terminal --autofit
```

Installer panel list entry: `EPD2in7b`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in7b scrub
```



## Hardware notes

Black/white/red.

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

Untested hardware may need LUT or init tweaks. Please open an issue if your revision misbehaves with this driver name.
