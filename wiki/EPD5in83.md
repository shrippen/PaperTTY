# EPD5in83

**5.83inch e-Paper**

Waveshare 5.83" - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD5in83` |
| Resolution | 600×448 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD5in83 terminal --autofit
```

Installer panel list entry: `EPD5in83`.

Scrub / clear:

```bash
sudo papertty --driver EPD5in83 scrub
```



## Hardware notes

Large mono panel (legacy).

[Waveshare wiki](https://www.waveshare.com/wiki/5.83inch_e-Paper_HAT)

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
