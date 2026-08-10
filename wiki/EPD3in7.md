# EPD3in7

**3.7inch e-Paper**

Waveshare 3.7" - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD3in7` |
| Resolution | 280×480 |
| Partial refresh | No (full refresh) |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD3in7 terminal --autofit
```

Installer panel list entry: `EPD3in7`.

Scrub / clear:

```bash
sudo papertty --driver EPD3in7 scrub
```



## Hardware notes

Larger mono HAT; grayscale capable hardware, PaperTTY uses 1-bit.

[Waveshare wiki](https://www.waveshare.com/wiki/3.7inch_e-Paper_HAT)

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
