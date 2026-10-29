"""data/contributions.json -> contrib-heatmap.svg (diagonal reveal, plays once)"""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG, FG, DIM, ACCENT = "#0d1117", "#c9d1d9", "#6e7681", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

CELL, GAP = 12, 3
STEP = CELL + GAP
LEFT, TOP = 40, 44
W = 860


def level_of(d, top):
    # GitHub gives 0-4; promote your busiest days to a neon level 5
    lvl = d["level"]
    if lvl == 4 and top and d["count"] >= top * 0.8:
        lvl = 5
    return lvl


def main():
    data = json.loads(DATA.read_text())
    days = data["days"]
    top = max(d["count"] for d in days) or 1

    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # Sunday = row 0
    cells, months, last_month = [], [], None
    for i, d in enumerate(days):
        idx = i + offset
        col, row = idx // 7, idx % 7
        dt = date.fromisoformat(d["date"])
        if row == 0 and dt.month != last_month:
            if not months or col - months[-1][0] >= 3:
                months.append((col, dt.strftime("%b")))
            last_month = dt.month
        cells.append((col, row, level_of(d, top), d))
    ncols = cells[-1][0] + 1
    grid_w = ncols * STEP
    H = TOP + 7 * STEP + 58

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           "<style>",
           f"text{{font-family:{FONT};}}",
           "@keyframes drop{0%{opacity:0;transform:translateY(-6px)}100%{opacity:1;transform:translateY(0)}}",
           "@keyframes fade{from{opacity:0}to{opacity:1}}",
           ".c{opacity:0;animation:drop .35s ease-out forwards;transform-box:fill-box}",
           ".f{opacity:0;animation:fade .6s ease-out forwards}",
           "</style>",
           f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>']

    x0 = LEFT + (W - LEFT - 20 - grid_w) // 2
    for col, label in months:
        if col < ncols - 1:
            out.append(f'<text x="{x0 + col*STEP}" y="{TOP-10}" font-size="11" fill="{DIM}">{label}</text>')
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{x0-32}" y="{TOP + row*STEP + 10}" font-size="10" fill="{DIM}">{label}</text>')

    for col, row, lvl, d in cells:
        delay = (col + row) * 0.018
        out.append(f'<rect class="c" style="animation-delay:{delay:.3f}s" x="{x0+col*STEP}" y="{TOP+row*STEP}" '
                   f'width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}">'
                   f'<title>{d["count"]} on {d["date"]}</title></rect>')

    end = (ncols + 7) * 0.018 + 0.3
    fy = TOP + 7 * STEP + 26
    best = data["best_day"]
    stats = (f'<tspan fill="{ACCENT}" font-weight="bold">{data["total"]:,}</tspan> contributions in the last year'
             f'  ·  streak <tspan fill="{FG}">{data["current_streak"]}d</tspan>'
             f'  ·  longest <tspan fill="{FG}">{data["longest_streak"]}d</tspan>'
             f'  ·  best day <tspan fill="{FG}">{best["count"]}</tspan>')
    out.append(f'<g class="f" style="animation-delay:{end:.2f}s">')
    out.append(f'<text x="{x0}" y="{fy}" font-size="12" fill="{DIM}">{stats}</text>')
    lx = x0 + grid_w - 6 * STEP - 70
    out.append(f'<text x="{lx}" y="{fy+22}" font-size="10" fill="{DIM}">Less</text>')
    for i, c in enumerate(PALETTE):
        out.append(f'<rect x="{lx + 32 + i*STEP}" y="{fy+12}" width="{CELL-2}" height="{CELL-2}" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 36 + 6*STEP}" y="{fy+22}" font-size="10" fill="{DIM}">More</text>')
    out.append(f'<text x="{x0}" y="{fy+22}" font-size="10" fill="{DIM}">updated {data["generated"]}</text>')
    out.append("</g></svg>")
    OUT.write_text("\n".join(out))
    print(f"wrote {OUT} ({ncols} weeks)")


if __name__ == "__main__":
    main()
