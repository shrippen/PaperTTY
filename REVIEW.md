# Review guide

Every PR is reviewed before it is merged (`RULES.md`). The reviewer knows nothing of the
session that wrote the change: it gets the PR's intent, its diff, the repository and this
file. The owner does not read code; this review is the second reader. There is no CI and no
PR-Agent: the reviewer is the only automatic check besides `tools/structure-check.py`.

## What failure looks like here

PaperTTY shows a Linux console, stdin text, an image, VNC or the framebuffer on an e-paper
display of a Raspberry Pi. Most drivers have never run on a panel. A bug that matters is one
that damages the display or leaves the Pi without a screen:

- **Damaged panel:** a wrong init sequence, voltage (IT8951 `--vcom`), refresh mode or
  timing, a refresh that is too frequent, a display left powered instead of in sleep.
- **Wrong picture:** inverted, mirrored or rotated output, shifted or clipped areas, a
  partial update that skips a changed area or leaves ghosts, bytes packed in the wrong bit
  or row order, wrong size or colour mode for the panel.
- **Crash at start:** a driver that does not take the common start settings, an import of
  a library that is missing on the Pi (`RPi.GPIO`, `vncdotool`, `numpy`), Python below 3.11.
- **Stuck screen:** a busy-wait without timeout, an exit, Ctrl-C or the clear signal
  (`SIGUSR1`) that leaves the display half drawn or not cleared, a console that keeps the
  size `terminal` set.
- **Broken install:** an installer that writes a wrong service, driver name or option and
  leaves the Pi without a display after reboot; a start script that differs from the docs.
- **Lies:** README, `wiki/`, `papertty/drivers/README.md` or comments that the code
  contradicts, e.g. a driver marked tested that is not.

## What to check in particular

- Layers: as in `ARCHITECTURE.md`. Only `drivers/` touches SPI, GPIO or display bytes; the
  program knows a display only through `DisplayDriver`.
- A new display: every place `ARCHITECTURE.md` lists under "Where new things go" is
  touched (driver list, `install/common.sh`, `papertty/drivers/README.md`, `wiki/` page,
  `wiki/Home.md`, `wiki/_Sidebar.md`), and the driver matches its Waveshare reference.
- A driver that cannot be tried here says so: experimental drivers keep their warning
  and their mark in README and wiki; "tested" needs the owner's word.
- An option offered once, at one level, checked once; options several commands share are
  not copied again.
- A changed default (driver, update interval, VCOM, partial refresh) changes README, wiki
  and the installers together.
- Bug fixes: a test that failed before the fix, and the cause removed. Display and timing
  bugs: the script in `tests/` run on the Pi, its output in the PR; without the panel, a
  unit test (`agent.md`). Without that evidence, say so.
- Calculation that needs no hardware (text drawing, changed areas) comes with a unit test.

## What the owner confirms here

- A release or tag and the landing page `docs/`, in addition to `RULES.md`. The installers
  run from `main`: a change to `install/` goes live for every user at once.

## Skip

- `papertty/resources/` fonts, `pics/`, `docs/shots/`, images.
- `tools/structure-check.py` and `scripts/release-notes.sh` (synced copies).
- Waveshare's lookup tables and register values, unless the PR changes them.

## How to report

- Every finding names file and line and the concrete input or state that goes wrong.
  No guess without evidence; if unsure, say so.
- Each finding gets one label: **Wichtig** (must be fixed or answered before the merge),
  **Kleinigkeit** (optional, at most five) or **Bestand** (was there before this PR).
- The report starts with the count, e.g. "2 Wichtig, 1 Kleinigkeit".
- Findings in German, code names as they are.
