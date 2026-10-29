# Changelog

The release notes of this fork, newest first. Each section is the text of the release on Gitea and
GitHub and of its entry in `#changes` on the landing page (`docs/index.html`).

Release steps, in this order:
1. Version `X.Y.Z` in `pyproject.toml` (branch `release/X.Y.Z`).
2. Section here, before the tag: `## [X.Y.Z] — YYYY-MM-DD`, `### English` and `### Deutsch`, each with
   a lead, the groups New, Improved, Fixed and Note as `####` (Neu, Verbessert, Behoben, Hinweis), and
   the compare link. Check with `scripts/release-notes.sh --check`, read with `scripts/release-notes.sh X.Y.Z`.
3. Landing page `docs/index.html`: the same text as the newest entry in `#changes` (from the fourth
   entry on, older ones go into `details.changelog-more`), footer version; screenshots of visible
   changes from the demo world, only now (`demo/shots.json`, `../shrippen.github.io/demo/tools/screenshots.py
   papertty`, saved as `docs/shots/release-X.Y.Z-<name>-<lang>.png`).
4. PR, reviewed by a new Claude agent (no PR-Agent here), the owner confirms the release; merge on Gitea.
5. Tag the merge commit, push to Gitea only: `git tag -a vX.Y.Z -m X.Y.Z <commit> && git push origin vX.Y.Z`.
6. Gitea release, notes only: `scripts/release-notes.sh X.Y.Z > notes.md && tea releases create --login
   git.arianw.de --repo shrippen/papertty --tag vX.Y.Z --title "PaperTTY X.Y.Z" --note-file notes.md`.
7. GitHub, by hand (no release workflow, no files: the installers run from `main`): `gh release create
   vX.Y.Z -R shrippen/PaperTTY --title "PaperTTY X.Y.Z" --notes-file notes.md --verify-tag`.
8. `python3 ../shrippen.github.io/overview/tools/build-versions.py`, commit `docs/versions.json` there via PR.
9. Done when https://shrippen.github.io/PaperTTY/ and https://shrippen.github.io/versions.json show it.

The script is a copy of Kante's `tools/release-notes.sh`: change it only there, sync with
`../Kante/tools/sync-release-notes.sh "$PWD"`.

## [1.0.0] — 2026-09-10

### English

The first release of this fork: PaperTTY runs on current Raspberry Pi OS, drives more Waveshare panels and is verified on real hardware, an IT8951 panel (1872×1404) on a Pi Zero 2 W.

#### New
- Installers in the style of papertty-init (`install/cli.sh`, `install/gui.sh`, `install/simple.sh`), also as curl one-liners: start at boot through systemd or crontab, prompts for panel and GPIO, Ubuntu fonts and VCOM for IT8951.
- More Waveshare drivers (2.13 V3/V4, 1.54/2.7/2.9/4.2/5.83 V2, 2.66, 2.9d, 7.5 HD, 4.01f and others), each with a wiki page and marked experimental.
- `--no-rotate` is the main name of `--portrait`, which stays as an alias: the flag draws text along the panel's native axes, it does not turn the output to portrait.

#### Improved
- Runs on Python 3.11+ and current Raspberry Pi OS (Pillow 10+, click 8). SPI goes through spidev, GPIO through gpiozero/lgpio. VNC is an optional extra (`papertty[vnc]`), and `--vcom` is a top-level option (IT8951 `scrub` needs it).
- IT8951 is much faster: `--mhz` sets the real SPI speed (12 MHz stable, 16 MHz not) and 1bpp packing is quicker. On 1872×1404 a full A2 refresh takes 0.6 s instead of 3.4 s, a partial line update 0.03 s instead of 1.5 s.
- Generated start scripts keep the output unbuffered under sudo, so start-up messages reach journald at once.

#### Fixed
- `GPIO busy` on the SPI chip-select pins: the kernel claimed them while PaperTTY switched them by hand. The error message, installers and docs now point to `dtoverlay=spi0-0cs`.
- Text rendering with Pillow 10+: the removed `ImageFont.getsize` is replaced.
- A stuck IT8951 controller no longer hangs the service: BUSY and LUT waits time out, and the service restarts.

#### Note
- The fork and its extended drivers are vibe-coded and built for personal use; verified on hardware is the IT8951 setup above.

All changes: https://github.com/shrippen/PaperTTY/compare/c9bb44a...v1.0.0

### Deutsch

Die erste Version dieses Forks: PaperTTY läuft auf aktuellem Raspberry Pi OS, treibt mehr Waveshare-Panels an und ist auf echter Hardware geprüft, mit einem IT8951-Panel (1872×1404) an einem Pi Zero 2 W.

#### Neu
- Installer im Stil von papertty-init (`install/cli.sh`, `install/gui.sh`, `install/simple.sh`), auch als curl-Einzeiler: Start beim Booten über systemd oder crontab, Abfrage von Panel und GPIO, Ubuntu-Schriften und VCOM für IT8951.
- Weitere Waveshare-Treiber (2.13 V3/V4, 1.54/2.7/2.9/4.2/5.83 V2, 2.66, 2.9d, 7.5 HD, 4.01f und andere), jeder mit einer Wiki-Seite und als experimentell markiert.
- `--no-rotate` ist der Hauptname von `--portrait`, das als Alias bleibt: Der Schalter zeichnet Text entlang der nativen Achsen des Panels, er dreht die Ausgabe nicht ins Hochformat.

#### Verbessert
- Läuft mit Python 3.11+ und aktuellem Raspberry Pi OS (Pillow 10+, click 8). SPI geht über spidev, GPIO über gpiozero/lgpio. VNC ist ein optionales Extra (`papertty[vnc]`), und `--vcom` ist eine Option auf oberster Ebene (`scrub` bei IT8951 braucht sie).
- IT8951 ist viel schneller: `--mhz` setzt die echte SPI-Geschwindigkeit (12 MHz stabil, 16 MHz nicht), und das Packen mit 1 bpp geht schneller. Bei 1872×1404 dauert ein voller A2-Refresh 0,6 s statt 3,4 s, das Teil-Update einer Zeile 0,03 s statt 1,5 s.
- Erzeugte Startskripte geben unter sudo ungepuffert aus, Startmeldungen landen sofort im journald.

#### Behoben
- `GPIO busy` an den SPI-Chip-Select-Pins: Der Kernel belegte sie, während PaperTTY sie selbst schaltete. Fehlermeldung, Installer und Doku verweisen jetzt auf `dtoverlay=spi0-0cs`.
- Textausgabe mit Pillow 10+: Das entfernte `ImageFont.getsize` ist ersetzt.
- Ein hängender IT8951-Controller legt den Dienst nicht mehr still: Das Warten auf BUSY und LUT hat eine Zeitgrenze, und der Dienst startet neu.

#### Hinweis
- Fork und erweiterte Treiber sind vibe-coded und für den eigenen Gebrauch gebaut; auf Hardware geprüft ist das IT8951-Setup oben.

Alle Änderungen: https://github.com/shrippen/PaperTTY/compare/c9bb44a...v1.0.0

## Upstream history (joukos/PaperTTY, before the fork)

The tags v0.01 to v0.04_prepypi are releases of the upstream project, not of this fork.

- **2020-03-01**
  - Added partial refresh support for 4.2".
- **2020-02-18**
  - Added interactive mode.
- **2020-01-25**
  - Added support for more cursors.
- **2020-01-22**
  - Added Unicode support for systems providing /dev/vcsu
- **2019-12-07**
  - Added basic support for EPD7in5v2 (GDEW075T7)
- **2019-11-03**
  - Added IT8951 support
- **2019-07-07**
  - Added VNC / GUI support
- **2018-08-31**
  - Installation instructions had an issue: running with `sudo` didn't respect the virtualenv - fixed
- **2018-08-26**
  - Added [nanofont](https://github.com/Michaelangel007/nanofont3x4) in PIL format
- **2018-08-25**
  - Now **all** the SPI models listed in Waveshare's Wiki have a driver implemented - all it needs now is some testing to see if any of it works
  - Fixed little issue with `--nopartial`: the screen was updated twice instead of once when enabled
  - Added support for:
    - **EPD 2.13" D (monochrome, flexible)**
      - Note: the original driver for this model seemed to have been written by someone who didn't write the rest of the drivers - it appeared to be essentially broken and written while drunk, I tried to fix it but who knows if it'll work
  - Added support for:
    - **EPD 5.83" (monochrome)**
    - **EPD 5.83" B (black/white/red)**
    - **EPD 5.83" C (black/white/yellow)**
  - Just one still missing:
    - **~~EPD 2.13" D (monochrome, flexible)~~**
- **2018-08-24**
  - **Major** overhaul
    - **Please create an issue (or pull request) if things don't work**
    - Converted code to Python 3 only
    - Install by default into a virtualenv
      - Can co-exist with the previous version
    - Replace old PIL with Pillow
    - **Bundled reorganized/modified display drivers to (*hopefully*) support more displays**
      - Created class structure to reduce code duplication in the drivers (got rid of ~60%)
        - Perhaps overkill and more complicated, but meh, I just couldn't bear the repetition and accommodating all the models would have been messy otherwise
      - **Supported models (SPI)**
        - **EPD 1.54" (monochrome) - [probably works, with partial refresh]**
        - **EPD 1.54" B (black/white/red)**
        - **EPD 1.54" C (black/white/yellow)**
        - **EPD 2.13" (monochrome) - [TESTED, with partial refresh]** 
        - **EPD 2.13" B (black/white/red)**
        - **EPD 2.13" C (black/white/yellow)** - should work with `EPD2in13b`
        - **EPD 2.7" (monochrome)**
        - **EPD 2.7" B (black/white/red)**
        - **EPD 2.9" (monochrome) - [probably works, with partial refresh]**
        - **EPD 2.9" B (black/white/red)**
        - **EPD 2.9" C (black/white/yellow)** - should work with `EPD2in9b`
        - **EPD 4.2" (monochrome)**
        - **EPD 4.2" B (black/white/red)**
        - **EPD 4.2" C (black/white/yellow)** - should work with `EPD4in2b`
        - **EPD 7.5" (monochrome)**
        - **EPD 7.5" B (black/white/red)**
        - **EPD 7.5" C (black/white/yellow)** - should work with `EPD7in5b`
      - **Missing models**
        - **EPD 2.13" D (monochrome, flexible)**
        - **~~EPD 5.83" (monochrome)~~**
        - **~~EPD 5.83" B (black/white/red)~~**
        - **~~EPD 5.83" C (black/white/yellow)~~**
      - **Special drivers**
        - **Dummy - no-op driver**
        - **Bitmap - output frames as bitmap files (for debugging)**
      - *Note: PaperTTY doesn't use the red/yellow colors ... yet*
      - See `drivers/README.md`
    - Some CLI changes related to driver selection
    - I learned that my particular unit has some flaw that means it doesn't do full refreshes properly (never has)

      - ***Doh!***
      - **I'll just assume it works as expected with other people's units**
    - Added new video
    - Heard that a partial refresh LUT for the 7.5" is nontrivial to do if at all possible, so best not to get your hopes up too much regarding those - there will probably be better panels available eventually
- **2018-08-16**
  - Included a very tiny bitmap font, "Tom Thumb", to use as default
- **2018-08-14**
  - Added support for PIL bitmap fonts (autodetected)
- **2018-08-13**
  - After browsing the Waveshare Wiki a bit, it seems that the smaller models support partial refresh out of the box but the bigger ones need some (hopefully minor) modification, if I ever get one I'll look into it
    - My guess is that this code should work as-is on the **Black/White 1.54", 2.13" and 2.9"** models - no guarantees though
    - The **2.7", 4.2", 5.83", 7.5"** models have slightly different code and need LUT modification or some hacking to achieve partial refresh, and I'm not sure if it's feasible to get it to work with the color models at all
    - ~~Modifying the code to work with full refreshes should be pretty easy if you happen to own one of the bigger monochrome displays~~
      - *This is now done, and may work with color ones as well (2018-08-24)*
