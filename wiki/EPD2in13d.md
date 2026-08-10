# EPD2in13d

**2.13inch e-Paper (D) flexible**

Waveshare 2.13" D - monochrome (flexible)

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in13d` |
| Resolution | 104×212 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in13d terminal --autofit
```

Installer panel list entry: `EPD2in13d`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in13d scrub
```



## Hardware notes

Flexible panel; handle carefully.

[Waveshare wiki](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(D))

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
