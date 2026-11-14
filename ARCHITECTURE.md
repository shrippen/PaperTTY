# Architecture

How this repository is meant to be built. Where the code differs today is listed under
"Known deviations". Change this file in the PR that changes the structure.

## What it does

Shows a Linux terminal on an e-paper display connected to a Raspberry Pi: the text of a
virtual console, text from standard input, an image, a VNC desktop or the framebuffer. It
redraws only what changed, because e-paper is slow. A fork of joukos/PaperTTY; much of the
structure is inherited.

## Building blocks

| Path | Its one task |
|---|---|
| `papertty/papertty.py` | The program. Today one file; in the target these parts, each a file of its own: |
| – command line | The commands (`terminal`, `stdin`, `image`, `vnc`, `fb`, `scrub`, `list`) and their options. |
| – console reader | Reads the content and size of a virtual console from `/dev/vcsa`. |
| – text renderer | Turns text and cursor into an image and finds the smallest area that changed. Pure calculation. |
| – picture sources | VNC and framebuffer: deliver the next picture; one shared loop shows it. |
| – driver list | Which driver names exist. |
| `papertty/drivers/drivers_base.py` | The template every driver follows (`DisplayDriver`), the access to SPI and GPIO, and the two drivers without hardware (`Dummy`, `Bitmap`). |
| `papertty/drivers/drivers_extended.py` | The newest base (`WaveshareBuffered`) and the drivers by controller chip (SSD16xx, UC81xx). New drivers go here. |
| `papertty/drivers/` (other files) | The older driver families (partial, full, color, colordraw, 4in2) and the IT8951 driver. |
| `papertty/resources/` | Bitmap fonts; the start script and the systemd service. |
| `install/` | The installers for a Raspberry Pi (minimal, console, desktop) and what they share. |
| `demo/` | A made-up terminal session rendered with the `Bitmap` driver, for screenshots. Not in a release archive. |
| `wiki/`, `docs/`, `pics/` | One page per display; the landing page; photos. |
| `scripts/`, `tools/` | Release notes; the structure check (synced copy). |

## Layers

```
 console (/dev/vcsa)   stdin   image file   VNC   framebuffer
        │                │         │          │        │
        ▼                ▼         │          ▼        ▼
   console reader ─► text renderer │     picture sources
                         │         │          │
                         ▼         ▼          ▼
               command line: picks the driver, runs the loop
                                   │  DisplayDriver: size, draw, clear, partial or not
                                   ▼
                  drivers/ ─► SPI, GPIO ─► the display
                  (Dummy and Bitmap: no hardware)

 install/ ─► installs the package, start script and service        demo/ ─► the program
```

- The program knows a display only through `DisplayDriver`. It never touches SPI, GPIO
  or the bytes a display expects.
- Only `drivers/` talks to hardware, through the SPI and GPIO access in
  `drivers_base.py`. A driver knows nothing of terminals, fonts or commands.
- Every driver takes the same settings at start; the template defines them once.
- The text renderer is pure calculation: no hardware, no console, no waiting. It can be
  tested with the `Bitmap` driver.
- What all drivers share is written once in a base, not per driver: turning an image
  into display bytes, waiting until the display is ready, reset.
- A new driver builds on the newest base and is filed by its controller chip. An older
  driver moves there only when it is changed with its display at hand.
- An option exists in one place, with one check.
- Start script and service exist once, in `papertty/resources/`; the installers use them
  and fill in values.
- `demo/` uses the program from outside; the program does not know the demo.

## Where new things go

| Change | Touch |
|---|---|
| A new display | A driver in `drivers_extended.py` under its chip's base, the driver list, a page in `wiki/` |
| A new setting every driver gets at start | The template in `drivers_base.py` |
| A new thing to show (another source) | A picture source, its command in the command line |
| How text is drawn or which area is redrawn | The text renderer, with a test using the `Bitmap` driver |
| A new command or option | The command line, README |
| How PaperTTY starts on a Pi | `papertty/resources/`, then `install/` |
| A release | `CHANGELOG.md`, landing page (skill `release-changelog`) |

## Known deviations

- `papertty.py` holds all parts of the program in one file of 1557 lines; `terminal`
  alone checks options, handles signals, runs the menu, reads the console and redraws
  (`AUDIT.md`, findings 7 and 10).
- Two driver families do not take the common start settings; five drivers crash at start
  (`AUDIT.md`, finding 1; a bug).
- The loops for VNC and framebuffer are copies (`AUDIT.md`, finding 6).
- Turning an image into display bytes is built eight times (`AUDIT.md`, finding 8).
- The drivers stand in four families named after their history, each with its own base
  (`AUDIT.md`, finding 9).
- The VCOM voltage can be set in two places with different checks (`AUDIT.md`,
  finding 4).
- The installers write their own start script and service; the ones in the package are
  unused (`AUDIT.md`, finding 3).
- There are no tests (`AUDIT.md`, finding 5).
