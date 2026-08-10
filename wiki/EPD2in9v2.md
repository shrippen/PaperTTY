# EPD2in9v2

**2.9inch e-Paper V2**

Waveshare 2.9" BW V2 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in9v2` |
| Resolution | 128×296 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in9v2 terminal --autofit
```

Installer panel list entry: `EPD2in9v2`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in9v2 scrub
```



## Hardware notes

SSD1680 V2 revision.

[Waveshare wiki](https://www.waveshare.com/wiki/2.9inch_e-Paper_Module)

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
