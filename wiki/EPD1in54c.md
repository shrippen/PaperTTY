# EPD1in54c

**1.54inch e-Paper (C)**

Waveshare 1.54" C - black / white / yellow

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD1in54c` |
| Resolution | 152×152 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD1in54c terminal --autofit
```

Installer panel list entry: `EPD1in54c`.

Scrub / clear:

```bash
sudo papertty --driver EPD1in54c scrub
```



## Hardware notes

Black/white/yellow. Often interchangeable with the B driver for mono use.

[Waveshare wiki](https://www.waveshare.com/wiki/1.54inch_e-Paper_Module_(C))

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
