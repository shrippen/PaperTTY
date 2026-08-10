# EPD2in9b

**2.9inch e-Paper (B)/(C)**

Waveshare 2.9" B - black / white / red

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in9b` |
| Resolution | 128×296 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in9b terminal --autofit
```

Installer panel list entry: `EPD2in9b`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in9b scrub
```



## Hardware notes

B and C color variants often share this driver for mono use.

[Waveshare wiki](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module_(B))

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
