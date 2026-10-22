#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar without an API token."""

import json
import re
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "ayaan0060"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUTPUT = Path("data/contributions.json")
COUNT_PATTERN = re.compile(r"(\d[\d,]*)\s+contributions?", re.IGNORECASE)


def parse_calendar(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    days = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        day_date = cell.get("data-date")
        level = cell.get("data-level")
        if not day_date or level is None:
            continue

        tooltip = cell.find_next_sibling("tool-tip")
        tooltip_text = tooltip.get_text(" ", strip=True) if tooltip else ""
        match = COUNT_PATTERN.search(tooltip_text)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append(
            {
                "date": day_date,
                "count": count,
                "level": min(5, max(0, int(level))),
            }
        )

    if not days:
        raise ValueError("No contribution days found in GitHub's response")

    days.sort(key=lambda item: item["date"])
    total = sum(item["count"] for item in days)
    positive_days = {date.fromisoformat(item["date"]) for item in days if item["count"]}
    longest_streak = current_streak = run = 0
    previous = None
    for day in sorted(positive_days):
        run = run + 1 if previous and day == previous + timedelta(days=1) else 1
        longest_streak = max(longest_streak, run)
        previous = day

    today = date.today()
    streak_day = today if today in positive_days else today - timedelta(days=1)
    while streak_day in positive_days:
        current_streak += 1
        streak_day -= timedelta(days=1)

    monthly_totals: dict[str, int] = defaultdict(int)
    for item in days:
        monthly_totals[item["date"][:7]] += item["count"]

    best_day = max(days, key=lambda item: item["count"])
    return {
        "username": USERNAME,
        "updated_at": today.isoformat(),
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": dict(sorted(monthly_totals.items())),
        "days": days,
    }


def main() -> None:
    response = requests.get(URL, timeout=30, headers={"User-Agent": "ayaan0060-profile-readme"})
    response.raise_for_status()
    data = parse_calendar(response.text)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(data['days'])} days and {data['total']:,} contributions to {OUTPUT}")


if __name__ == "__main__":
    main()
