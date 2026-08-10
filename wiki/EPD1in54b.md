# EPD1in54b

**1.54inch e-Paper (B)**

Waveshare 1.54" B - black / white / red

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD1in54b` |
| Resolution | 200×200 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD1in54b terminal --autofit
```

Installer panel list entry: `EPD1in54b`.

Scrub / clear:

```bash
sudo papertty --driver EPD1in54b scrub
```



## Hardware notes

Black/white/red. PaperTTY renders mono only.

[Waveshare wiki](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_(B))

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
