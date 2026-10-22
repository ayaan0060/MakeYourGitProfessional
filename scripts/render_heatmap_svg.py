#!/usr/bin/env python3
"""Render contribution data as an animated, self-contained SVG heatmap."""

import json
from datetime import date
from html import escape
from pathlib import Path

DATA = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 11
GAP = 4
LEFT = 45
TOP = 40
WIDTH = 860


def render(data: dict) -> str:
    days = {
        date.fromisoformat(item["date"]): item
        for item in data["days"]
    }
    first_day = min(days)
    start = first_day.toordinal() - (first_day.weekday() + 1) % 7
    cells = []
    for day, item in sorted(days.items()):
        offset = day.toordinal() - start
        col, row = divmod(offset, 7)
        x = LEFT + col * (CELL + GAP)
        y = TOP + row * (CELL + GAP)
        delay = col * 0.018 + row * 0.025
        level = min(5, max(0, int(item["level"])))
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[level]}" opacity="0">'
            f'<title>{escape(item["date"])}: {item["count"]} contributions</title>'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.3f}s" dur="0.35s" fill="freeze"/></rect>'
        )

    months = []
    month_seen = set()
    for day in sorted(days):
        key = day.strftime("%Y-%m")
        if key in month_seen:
            continue
        month_seen.add(key)
        offset = day.toordinal() - start
        col = offset // 7
        months.append(
            f'<text x="{LEFT + col * (CELL + GAP)}" y="26" fill="#8b949e" '
            f'font-family="sans-serif" font-size="10">{escape(day.strftime("%b"))}</text>'
        )

    weekdays = []
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        weekdays.append(
            f'<text x="4" y="{TOP + row * (CELL + GAP) + 9}" fill="#8b949e" '
            f'font-family="sans-serif" font-size="9">{label}</text>'
        )

    legend_x = WIDTH - 156
    legend_y = 149
    legend = [
        f'<text x="{legend_x - 38}" y="{legend_y + 10}" fill="#8b949e" '
        'font-family="sans-serif" font-size="10">Less</text>'
    ]
    for level, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + level * 15}" y="{legend_y}" width="11" '
            f'height="11" rx="3" fill="{color}"/>'
        )
    legend.append(
        f'<text x="{legend_x + 6 * 15 + 2}" y="{legend_y + 10}" fill="#8b949e" '
        'font-family="sans-serif" font-size="10">More</text>'
    )

    best = data["best_day"]
    footer = (
        f'{data["total"]:,} contributions in the last year'
        f'  ·  streak {data["current_streak"]} days'
        f'  ·  best day {best["count"]} ({best["date"]})'
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="180" '
        'viewBox="0 0 860 180" role="img" aria-label="Animated GitHub contribution calendar">'
        '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>'
        '<text x="45" y="20" fill="#c9d1d9" font-family="sans-serif" '
        'font-size="12" font-weight="600">GitHub contributions</text>'
        + "".join(months)
        + "".join(weekdays)
        + "".join(cells)
        + "".join(legend)
        + f'<text x="45" y="174" fill="#8b949e" font-family="sans-serif" '
        f'font-size="10">{escape(footer)}</text>'
        + "</svg>\n"
    )


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUTPUT.write_text(render(data), encoding="utf-8")
    print(f"Heatmap saved to {OUTPUT}")


if __name__ == "__main__":
    main()
