# EPD7in5v2

**7.5inch e-Paper V2 (GDEW075T7)**

WaveShare 7.5" GDEW075T7 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD7in5v2` |
| Resolution | 800×480 |
| Partial refresh | No (full refresh) |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD7in5v2 terminal --autofit
```

Installer panel list entry: `EPD7in5v2`.

Scrub / clear:

```bash
sudo papertty --driver EPD7in5v2 scrub
```



## Hardware notes

800×480 V2 mono; common modern 7.5" HAT.

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
