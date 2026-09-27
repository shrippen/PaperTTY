# Demo (internal)

Internal tool for automated screenshots, not part of any release. Uses the shared demo world of all shrippen projects (shrippen.github.io/demo).

`demo/start.sh [de|en] [--driver <name>]` sends a demo terminal session to PaperTTY: the studio-pi
of Studio Weber, the demo world shared by all shrippen projects (`demo/world.json`, copied from
`shrippen.github.io/demo`). The default driver is `Bitmap`, which writes `bitmap_frame_0.png` and
needs no display. `demo/render.py shot OUT.png` renders the same session into a drawn e-ink panel for
the landing page (`demo/shots.json`, run by `shrippen.github.io/demo/tools/screenshots.py`).
