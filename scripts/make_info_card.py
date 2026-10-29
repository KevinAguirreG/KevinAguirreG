"""Neofetch-style info card -> info-card.svg. Edit CARD below; STATIC=1 for a frozen frame."""
import os
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

TITLE = "kevin@github"
# (key, value) rows; None = blank spacer; ("#", text) = section header
CARD = [
    ("OS", "Monterrey, MX · ES · EN (C1) · FR"),
    ("Role", "Full-Stack Developer · Laravel/PHP"),
    ("Now", "Didaktron · makerSTEAM LMS (20+ schools)"),
    ("Prev", "ValoraCredit · Copixl · Freelance"),
    ("Edu", "B.Eng. Software Dev · TecMilenio '26"),
    ("Abroad", "Exchange · VIVES University, BE"),
    None,
    ("#", "stack"),
    ("Backend", "Laravel · Filament · Livewire · Node"),
    ("Frontend", "JavaScript · jQuery · Blade"),
    ("Data", "MySQL · Redis · MongoDB · Python"),
    ("Cloud", "AWS · EC2 S3 RDS CloudFront IAM"),
    ("DevOps", "Docker · Terraform · Ansible · GH Actions"),
    ("Testing", "PHPUnit · Playwright · Jest"),
    None,
    ("#", "highlights"),
    ("-", "Owning Laravel 5.8→13 / PHP 7.4→8.5 upgrade"),
    ("-", "2FA/TOTP for the LMS · tests 62 → 238"),
    ("-", "~1,600 → ~8 queries/view · 1.5 s → 17 ms"),
    ("-", "Legacy refactor: −60% controller code"),
    ("-", "2 ERPs shipped solo · prod on Docker"),
    None,
    ("#", "contact"),
    ("Mail", "kevinaguirre840@gmail.com"),
    ("LinkedIn", "in/kevinaguirreg"),
]

W, PAD, LH = 490, 22, 21
BG, BAR, FG, DIM, KEY, HEAD = "#0d1117", "#161b22", "#c9d1d9", "#6e7681", "#39d353", "#58a6ff"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SWATCH = ["#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#58a6ff", "#d2a8ff", "#c9d1d9"]


def main():
    H = 44 + 34 + len(CARD) * LH + 46
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         "<style>",
         f"text{{font-family:{FONT};font-size:13px;}}",
         "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}",
         "" if STATIC else ".l{opacity:0;animation:in .4s ease-out forwards}",
         "</style>",
         f'<rect width="{W}" height="{H}" rx="10" fill="{BG}" stroke="#30363d"/>',
         f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v20H0z" fill="{BAR}"/>']
    for i, c in enumerate(("#ff5f56", "#ffbd2e", "#27c93f")):
        o.append(f'<circle cx="{18+i*18}" cy="15" r="5.5" fill="{c}"/>')
    o.append(f'<text x="{W/2}" y="19" text-anchor="middle" font-size="12" fill="{DIM}">~/neofetch</text>')

    y, n = 58, 0

    def line(content):
        nonlocal n
        d = 0.25 + n * 0.09
        n += 1
        return f'<g class="l" style="animation-delay:{d:.2f}s">{content}</g>'

    o.append(line(f'<text x="{PAD}" y="{y}" fill="{KEY}" font-weight="bold">{TITLE}</text>'))
    y += 14
    o.append(line(f'<text x="{PAD}" y="{y}" fill="{DIM}">{"─" * 44}</text>'))
    y += LH
    for row in CARD:
        if row is None:
            y += LH
            continue
        k, v = row
        if k == "#":
            t = f'<text x="{PAD}" y="{y}" fill="{HEAD}">── {escape(v)} {"─" * (38 - len(v))}</text>'
        elif k == "-":
            t = f'<text x="{PAD}" y="{y}"><tspan fill="{KEY}">▸ </tspan><tspan fill="{FG}">{escape(v)}</tspan></text>'
        else:
            t = (f'<text x="{PAD}" y="{y}"><tspan fill="{KEY}" font-weight="bold">{escape(k)}</tspan>'
                 f'<tspan fill="{DIM}">:</tspan><tspan x="{PAD+92}" fill="{FG}">{escape(v)}</tspan></text>')
        o.append(line(t))
        y += LH
    y += 4
    sw = "".join(f'<rect x="{PAD + i*26}" y="{y}" width="22" height="12" rx="2" fill="{c}"/>' for i, c in enumerate(SWATCH))
    o.append(line(sw))
    o.append("</svg>")
    OUT.write_text("\n".join(o))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
