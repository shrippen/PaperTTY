# EPD5in65f

**5.65inch e-Paper (F) 7-color**

Waveshare 5.65" - 7 colors

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD5in65f` |
| Resolution | 600×448 |
| Partial refresh | No (full refresh) |
| Color channels | 3 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD5in65f terminal --autofit
```

Installer panel list entry: `EPD5in65f`.

Scrub / clear:

```bash
sudo papertty --driver EPD5in65f scrub
```



## Hardware notes

7-color; PaperTTY uses mono only.

[Waveshare wiki](https://www.waveshare.com/wiki/5.65inch_e-Paper_Module_(F))

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
