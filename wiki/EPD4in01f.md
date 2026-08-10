# EPD4in01f

**4.01inch e-Paper (F) 7-color**

Waveshare 4.01" F - 7 colors (drawn as black and white)

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `EPD4in01f` |
| Resolution | 640×400 |
| Partial refresh | No (full refresh) |
| Color channels | 7 (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
sudo papertty --driver EPD4in01f terminal --autofit
```

Installer panel list entry: `EPD4in01f`.

Scrub / clear:

```bash
sudo papertty --driver EPD4in01f scrub
```



## Hardware notes

7-color panel; PaperTTY dithers to black/white only.

[Waveshare wiki](https://www.waveshare.com/wiki/4.01inch_e-Paper_Module_(F))

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
