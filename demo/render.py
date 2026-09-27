#!/usr/bin/env python3
"""Demo session for PaperTTY: the terminal of Studio Weber's studio-pi (the shrippen demo world,
demo/world.json, copied from shrippen.github.io/demo; do not edit it here).

  demo/render.py session [de|en]         prints the demo session text
  demo/render.py shot OUT.png [de|en]    renders it with PaperTTY's Bitmap driver (the real
                                         renderer, no display needed) and puts the frame into a
                                         drawn e-ink panel, for the landing page
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FONTS = ["/usr/share/fonts/TTF/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
         "/usr/share/fonts/noto/NotoSansMono-Regular.ttf"]


def session(lang):
    world = json.loads((HERE / "world.json").read_text(encoding="utf-8"))
    term = world["terminal"]
    lines = [line if isinstance(line, str) else line.get(lang, line["en"]) for line in term["session"]]
    prompt = f"{term['user']}@{term['host']}:~"
    return "\n".join(prompt + line[1:] if line.startswith("$") else line for line in lines) + "\n"


def font():
    return next((f for f in FONTS if os.path.exists(f)), None)


def render(out, lang):
    from PIL import Image, ImageDraw, ImageFilter
    with tempfile.TemporaryDirectory() as tmp:
        args = [sys.executable, "-c", "from papertty.papertty import cli; cli()", "--driver", "Bitmap", "stdin",
                "--portrait"]              # the Bitmap frame is already landscape
        if font():
            args += ["--font", font(), "--size", "18"]
        args.append("--nofold")            # the demo lines are short enough
        subprocess.run(args, input=session(lang), text=True, cwd=tmp, check=True,
                       env=dict(os.environ, PYTHONPATH=str(ROOT)), stdout=subprocess.DEVNULL)
        frame = Image.open(Path(tmp) / "bitmap_frame_0.png").convert("L")

    # E-ink look: warm paper white, soft black ink, then the panel with its bezel and ribbon cable.
    ink = frame.point(lambda v: 38 if v < 128 else 232)
    paper = Image.merge("RGB", [ink.point(lambda v: min(255, v + 4)), ink, ink.point(lambda v: max(0, v - 12))])
    paper = paper.filter(ImageFilter.GaussianBlur(0.35))
    w, h = paper.size
    pad, bezel = 60, 34
    panel = Image.new("RGBA", (w + 2 * (pad + bezel), h + 2 * (pad + bezel) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    shadow = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([pad + 10, pad + 16, pad + w + 2 * bezel + 10, pad + h + 2 * bezel + 16],
                                             radius=18, fill=(0, 0, 0, 120))
    panel = Image.alpha_composite(panel, shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle([pad, pad, pad + w + 2 * bezel, pad + h + 2 * bezel], radius=16, fill=(62, 60, 58, 255))
    d.rectangle([pad + bezel - 3, pad + bezel - 3, pad + bezel + w + 2, pad + bezel + h + 2], fill=(40, 40, 40, 255))
    cable = pad + bezel + w // 2
    d.rectangle([cable - 70, pad + h + 2 * bezel, cable + 70, pad + h + 2 * bezel + 40], fill=(196, 134, 40, 255))
    panel.paste(paper, (pad + bezel, pad + bezel))
    panel.save(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "session"
    if cmd == "session":
        sys.stdout.write(session(sys.argv[2] if len(sys.argv) > 2 else "de"))
    elif cmd == "shot":
        render(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "de")
    else:
        sys.exit(__doc__)
