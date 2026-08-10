# EPD7in5b_HD

**7.5inch HD e-Paper (B)**

Waveshare 7.5" HD B - black / white / red (drawn as black and white)

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD7in5b_HD` |
| Resolution | 880×528 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD7in5b_HD terminal --autofit
```

Installer panel list entry: `EPD7in5b_HD`.

Scrub / clear:

```bash
sudo papertty --driver EPD7in5b_HD scrub
```



## Hardware notes

880×528 B/W/R HD.

[Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_HD_e-Paper_HAT_(B))

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
