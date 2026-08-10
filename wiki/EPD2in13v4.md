# EPD2in13v4

**2.13inch e-Paper HAT V4 / HAT+**

Waveshare 2.13" BW V4 - monochrome

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD2in13v4` |
| Resolution | 128×250 |
| Partial refresh | Yes |
| Color channels | 2 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD2in13v4 terminal --autofit
```

Installer panel list entry: `EPD2in13v4`.

Scrub / clear:

```bash
sudo papertty --driver EPD2in13v4 scrub
```



## Hardware notes

Current V4 and HAT+ stock (incl. many Pwnagotchi kits). Prefer this for new 2.13" purchases.

[Waveshare wiki](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT+)

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
