# EPD2in7

**2.7inch e-Paper**

Waveshare 2.7" - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in7` |
| Resolution | 176×264 |
| Partial refresh | No (full refresh) |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in7 terminal --autofit
```

Installer panel list entry: `EPD2in7`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in7 scrub
```



## Hardware notes

Classic 2.7" mono.

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
