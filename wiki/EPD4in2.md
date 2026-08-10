# EPD4in2

**4.2inch e-Paper**

WaveShare 4.2"

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD4in2` |
| Resolution | 400×300 |
| Partial refresh | Yes |
| Color channels | see notes (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD4in2 terminal --autofit
```

Installer panel list entry: `EPD4in2`.

Scrub / clear:

```bash
sudo papertty --driver EPD4in2 scrub
```



## Hardware notes

Classic 4.2" with partial refresh support in PaperTTY.

[Waveshare wiki](https://www.waveshare.com/wiki/4.2inch_e-Paper_Module)

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
