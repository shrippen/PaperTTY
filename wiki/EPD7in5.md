# EPD7in5

**7.5inch e-Paper**

Waveshare 7.5" - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD7in5` |
| Resolution | 640×384 |
| Partial refresh | No (full refresh) |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD7in5 terminal --autofit
```

Installer panel list entry: `EPD7in5`.

Scrub / clear:

```bash
sudo papertty --driver EPD7in5 scrub
```



## Hardware notes

Legacy 640×384 mono.

[Waveshare wiki](https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT)

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
