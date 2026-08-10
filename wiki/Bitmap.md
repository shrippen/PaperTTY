# Bitmap

**Bitmap frame dump**

Output a bitmap for each frame - overwrite old ones

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `Bitmap` |
| Resolution | 640×384 |
| Partial refresh | No (full refresh) |
| Color channels | see notes (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
papertty --driver Bitmap terminal --autofit
```

Installer panel list entry: `Bitmap`.

Scrub / clear:

```bash
sudo papertty --driver Bitmap scrub
```



## Hardware notes

Writes PNG frames to the working directory for debugging.

_No official wiki link recorded._

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
