# PaperTTY Wiki

Maintained fork of [joukos/PaperTTY](https://github.com/joukos/PaperTTY).

This wiki documents every display driver shipped in the tree.

## Getting started

- [README](https://github.com/shrippen/PaperTTY/blob/main/README.md) — installers and CLI
- Enable SPI on the Pi (`raspi-config`)
- Pick a driver name below and run e.g. `sudo papertty --driver EPD2in13v4 terminal --autofit`

## Supported drivers

| Driver | Product | Resolution | Partial | Page |
|--------|---------|------------|---------|------|
| `Bitmap` | Bitmap frame dump | 640×384 | no | [[Bitmap]] |
| `Dummy` | Dummy (no hardware) | 640×384 | no | [[Dummy]] |
| `EPD1in54` | 1.54inch e-Paper | 200×200 | yes | [[EPD1in54]] |
| `EPD1in54b` | 1.54inch e-Paper (B) | 200×200 | no | [[EPD1in54b]] |
| `EPD1in54c` | 1.54inch e-Paper (C) | 152×152 | no | [[EPD1in54c]] |
| `EPD1in54v2` | 1.54inch e-Paper V2 | 200×200 | yes | [[EPD1in54v2]] |
| `EPD2in13` | 2.13inch e-Paper HAT (legacy) | 128×250 | yes | [[EPD2in13]] |
| `EPD2in13b` | 2.13inch e-Paper (B) | 104×212 | no | [[EPD2in13b]] |
| `EPD2in13d` | 2.13inch e-Paper (D) flexible | 104×212 | yes | [[EPD2in13d]] |
| `EPD2in13v2` | 2.13inch e-Paper HAT V2 | 128×250 | yes | [[EPD2in13v2]] |
| `EPD2in13v3` | 2.13inch e-Paper HAT V3 | 128×250 | yes | [[EPD2in13v3]] |
| `EPD2in13v4` | 2.13inch e-Paper HAT V4 / HAT+ | 128×250 | yes | [[EPD2in13v4]] |
| `EPD2in66` | 2.66inch e-Paper | 152×296 | yes | [[EPD2in66]] |
| `EPD2in66b` | 2.66inch e-Paper (B) | 152×296 | no | [[EPD2in66b]] |
| `EPD2in7` | 2.7inch e-Paper | 176×264 | no | [[EPD2in7]] |
| `EPD2in7b` | 2.7inch e-Paper (B) | 176×264 | no | [[EPD2in7b]] |
| `EPD2in7b_V2` | 2.7inch e-Paper (B) V2 | 176×264 | no | [[EPD2in7b_V2]] |
| `EPD2in7v2` | 2.7inch e-Paper V2 | 176×264 | yes | [[EPD2in7v2]] |
| `EPD2in9` | 2.9inch e-Paper | 128×296 | yes | [[EPD2in9]] |
| `EPD2in9b` | 2.9inch e-Paper (B)/(C) | 128×296 | no | [[EPD2in9b]] |
| `EPD2in9d` | 2.9inch e-Paper (D) flexible | 128×296 | yes | [[EPD2in9d]] |
| `EPD2in9v2` | 2.9inch e-Paper V2 | 128×296 | yes | [[EPD2in9v2]] |
| `EPD3in7` | 3.7inch e-Paper | 280×480 | no | [[EPD3in7]] |
| `EPD4in01f` | 4.01inch e-Paper (F) 7-color | 640×400 | no | [[EPD4in01f]] |
| `EPD4in2` | 4.2inch e-Paper | 400×300 | yes | [[EPD4in2]] |
| `EPD4in2b` | 4.2inch e-Paper (B)/(C) | 400×300 | no | [[EPD4in2b]] |
| `EPD4in2b_V2` | 4.2inch e-Paper (B) V2 | 400×300 | no | [[EPD4in2b_V2]] |
| `EPD4in2v2` | 4.2inch e-Paper V2 | 400×300 | yes | [[EPD4in2v2]] |
| `EPD5in65f` | 5.65inch e-Paper (F) 7-color | 600×448 | no | [[EPD5in65f]] |
| `EPD5in83` | 5.83inch e-Paper | 600×448 | no | [[EPD5in83]] |
| `EPD5in83b` | 5.83inch e-Paper (B)/(C) | 600×448 | no | [[EPD5in83b]] |
| `EPD5in83b_V2` | 5.83inch e-Paper (B) V2 | 648×480 | no | [[EPD5in83b_V2]] |
| `EPD5in83v2` | 5.83inch e-Paper V2 | 648×480 | yes | [[EPD5in83v2]] |
| `EPD7in5` | 7.5inch e-Paper | 640×384 | no | [[EPD7in5]] |
| `EPD7in5_HD` | 7.5inch HD e-Paper | 880×528 | no | [[EPD7in5_HD]] |
| `EPD7in5b` | 7.5inch e-Paper (B)/(C) | 640×384 | no | [[EPD7in5b]] |
| `EPD7in5b_HD` | 7.5inch HD e-Paper (B) | 880×528 | no | [[EPD7in5b_HD]] |
| `EPD7in5b_V2` | 7.5inch e-Paper (B) V2 | 800×480 | no | [[EPD7in5b_V2]] |
| `EPD7in5v2` | 7.5inch e-Paper V2 (GDEW075T7) | 800×480 | no | [[EPD7in5v2]] |
| `IT8951` | IT8951 HD HAT (6" / 7.8" / 9.7" / 10.3" / …) | auto (from controller) | yes | [[IT8951]] |

## IT8951 HD panels

One driver (`IT8951`) covers Waveshare HD HATs that use the IT8951 controller (6", 7.8", 9.7", 10.3", and similar).
See [[IT8951]].

## Contributing

Driver ports live under `papertty/drivers/` (GPL-3.0, Waveshare-derived).
New panels usually start from [waveshare/e-Paper](https://github.com/waveshareteam/e-Paper) Python demos.

