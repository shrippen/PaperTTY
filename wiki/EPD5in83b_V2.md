# EPD5in83b_V2

**5.83inch e-Paper (B) V2**

Waveshare 5.83" B V2 - black / white / red (drawn as black and white)

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD5in83b_V2` |
| Resolution | 648×480 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD5in83b_V2 terminal --autofit
```

Installer panel list entry: `EPD5in83b_V2`.

Scrub / clear:

```bash
sudo papertty --driver EPD5in83b_V2 scrub
```



## Hardware notes

V2 B/W/R.

[Waveshare wiki](https://www.waveshare.com/wiki/5.83inch_e-Paper_HAT_(B))

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
