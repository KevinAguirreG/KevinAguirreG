"""source-prepped.png -> kevin-ascii.svg (monochrome ASCII that types itself in, row by row, once)."""
import os
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "source-prepped.png"
OUT = ROOT / "kevin-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

RAMP = " .`:-=+*cs#%@"   # sparse -> dense; index 0 (space) is reserved for the background
INVERT = os.environ.get("INVERT", "1") == "1"  # 1: light skin = dense glyphs (reads right on a dark card)
COLS = int(os.environ.get("COLS", 100))
GAMMA = float(os.environ.get("GAMMA", 1.0))   # with INVERT=1: >1 = sparser/darker, <1 = denser/brighter
FS = 9.0                 # font size
CW, LH = FS * 0.6, FS * 1.05   # monospace char width / line height
PAD = 14
BG, FG, CURSOR = "#0d1117", "#c9d1d9", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
ROW_DUR, ROW_STAGGER = 0.35, 0.045


def to_ascii():
    img = Image.open(SRC).convert("L")
    w, h = img.size
    rows = int(COLS * (h / w) * (CW / LH))
    a = np.asarray(img.resize((COLS, rows), Image.LANCZOS), dtype=float) / 255.0
    bg = a > 0.97                      # pure white = background from prep_photo
    if (~bg).any():                    # stretch subject tones to the full ramp
        lo, hi = np.percentile(a[~bg], (2, 98))
        a = np.clip((a - lo) / max(hi - lo, 1e-3), 0, 1)
    a = a ** GAMMA
    t = a if INVERT else 1 - a
    idx = 1 + (t * (len(RAMP) - 2)).round().astype(int)
    idx[bg] = 0
    return ["".join(RAMP[i] for i in r).rstrip() for r in idx]


def main():
    lines = to_ascii()
    W = int(PAD * 2 + COLS * CW)
    H = int(PAD * 2 + len(lines) * LH + 4)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>',
         f'<g font-family="{FONT}" font-size="{FS}" fill="{FG}" style="white-space:pre" xml:space="preserve">']
    full = COLS * CW + 2
    for i, line in enumerate(lines):
        y = PAD + (i + 1) * LH
        if not line.strip():
            continue
        txt = f'<text x="{PAD}" y="{y:.1f}">{escape(line).replace(" ", "\u00a0")}</text>'  # nbsp: never collapses
        if STATIC:
            o.append(txt)
            continue
        b = 0.2 + i * ROW_STAGGER
        o.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{y-LH:.1f}" width="0" height="{LH+1:.1f}">'
            f'<animate attributeName="width" from="0" to="{full:.0f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'</rect></clipPath>'
            f'<g clip-path="url(#r{i})">{txt}</g>'
            f'<rect x="{PAD}" y="{y-LH+1:.1f}" width="{CW:.1f}" height="{LH-1:.1f}" fill="{CURSOR}" opacity="0">'
            f'<animate attributeName="x" from="{PAD}" to="{PAD+full:.0f}" begin="{b:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="1" begin="{b:.2f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{b+ROW_DUR:.2f}s"/></rect>'
        )
    o.append("</g></svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT} ({COLS}x{len(lines)}, {W}x{H}px)")


if __name__ == "__main__":
    main()
