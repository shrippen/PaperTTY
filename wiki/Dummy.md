# Dummy

**Dummy (no hardware)**

Dummy display driver - does not do anything

## Specs (as used by PaperTTY)

| | |
|--|--|
| Driver name | `Dummy` |
| Resolution | 640×384 |
| Partial refresh | No (full refresh) |
| Color channels | see notes (PaperTTY output is 1-bit mono) |
| Interface | SPI (unless noted) |

## Usage

```bash
papertty --driver Dummy terminal --autofit
```

Installer panel list entry: `Dummy`.

Scrub / clear:

```bash
sudo papertty --driver Dummy scrub
```



## Hardware notes

No-op driver for dry-run / CI without a panel.

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
