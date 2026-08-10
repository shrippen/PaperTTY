# EPD4in2b

**4.2inch e-Paper (B)/(C)**

Waveshare 4.2" B - black / white / red

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD4in2b` |
| Resolution | 400×300 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD4in2b terminal --autofit
```

Installer panel list entry: `EPD4in2b`.

Scrub / clear:

```bash
sudo papertty --driver EPD4in2b scrub
```



## Hardware notes

Color variants; mono rendering only.

[Waveshare wiki](https://www.waveshare.com/wiki/4.2inch_e-Paper_Module_(B))

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
