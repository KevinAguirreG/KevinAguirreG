"""Scrape the public GitHub contribution calendar (no token) -> data/contributions.json"""
import json
import os
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USER", "KevinAguirreG")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"


def fetch_days(user: str) -> list[dict]:
    url = f"https://github.com/users/{user}/contributions"
    r = requests.get(url, headers={"User-Agent": "profile-art-bot"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # counts live in <tool-tip for="contribution-day-component-X-Y">N contributions on ...</tool-tip>
    counts = {}
    for tip in soup.find_all("tool-tip"):
        m = re.match(r"\s*(\d+|No) contributions?", tip.get_text())
        if m and tip.get("for"):
            counts[tip["for"]] = 0 if m.group(1) == "No" else int(m.group(1))

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "level": int(td.get("data-level", 0)),
            "count": counts.get(td.get("id"), 0),
        })
    if not days:
        raise SystemExit("No contribution cells found — GitHub markup may have changed.")
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] > 0 else 0
        longest = max(longest, run)
    current = 0
    rev = list(reversed(days))
    if rev and rev[0]["count"] == 0:  # today not counted yet -> don't break the streak
        rev = rev[1:]
    for d in rev:
        if d["count"] == 0:
            break
        current += 1
    return current, longest


def main():
    days = fetch_days(USERNAME)
    current, longest = streaks(days)
    best = max(days, key=lambda d: d["count"])
    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
    data = {
        "user": USERNAME,
        "generated": date.today().isoformat(),
        "total": sum(d["count"] for d in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly": dict(monthly),
        "days": days,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"{USERNAME}: {data['total']} contributions, streak {current}/{longest} -> {OUT}")


if __name__ == "__main__":
    main()
