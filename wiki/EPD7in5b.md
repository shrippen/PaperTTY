# EPD7in5b

**7.5inch e-Paper (B)/(C)**

Waveshare 7.5" B - black / white / red

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD7in5b` |
| Resolution | 640×384 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD7in5b terminal --autofit
```

Installer panel list entry: `EPD7in5b`.

Scrub / clear:

```bash
sudo papertty --driver EPD7in5b scrub
```



## Hardware notes

Color variants of the legacy 7.5".

[Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT_(B))

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
