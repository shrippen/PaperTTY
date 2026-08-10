# EPD2in7v2

**2.7inch e-Paper V2**

Waveshare 2.7" BW V2 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in7v2` |
| Resolution | 176×264 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in7v2 terminal --autofit
```

Installer panel list entry: `EPD2in7v2`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in7v2 scrub
```



## Hardware notes

SSD1680 V2 revision with partial refresh.

[Waveshare wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT)

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
