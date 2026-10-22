#!/usr/bin/env python3
"""Generate the animated profile information card."""

import os
from html import escape
from pathlib import Path

WIDTH = 490
PADDING = 22
LINE_HEIGHT = 27
ROWS = [
    ("Now", "Software Engineer"),
    ("Prev", "Final year student"),
    ("Stack", "Python · JavaScript · HTML · CSS · Node.js · Express · React · Vite · SQL · MongoDB"),
    ("Highlights", "Problem-solving · Data Structures and Algorithms · Backend Development · Python Programming"),
    ("Projects", "SmartQ Hospital Queue Management · Healthcare Triage Bot"),
    ("Learning", "Deloitte Technology Job Simulation · Python DSA Certification · MERN Stack Development Certification"),
]


def wrap(value: str, max_chars: int) -> list[str]:
    words = value.split()
    lines: list[str] = []
    line = ""
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) > max_chars and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def render_info_card(output: Path, static: bool = False) -> None:
    label_width = 96
    value_width = WIDTH - (PADDING * 2) - label_width
    max_chars = value_width // 7
    row_lines = [(label, wrap(value, max_chars)) for label, value in ROWS]
    card_height = 68 + sum(max(1, len(lines)) * LINE_HEIGHT for _, lines in row_lines) + 20
    elements = [
        '<rect x="1" y="1" width="488" height="{}" rx="12" '
        'fill="#0d1117" stroke="#30363d"/>'.format(card_height - 2),
        '<path d="M13 1h464a12 12 0 0 1 12 12v30H1V13A12 12 0 0 1 13 1Z" '
        'fill="#161b22"/>',
        '<circle cx="20" cy="22" r="5" fill="#ff5f57"/>',
        '<circle cx="38" cy="22" r="5" fill="#febc2e"/>',
        '<circle cx="56" cy="22" r="5" fill="#28c840"/>',
        '<text x="75" y="26" fill="#8b949e" font-family="monospace" font-size="12">'
        'ayaan0060 — neofetch</text>',
        '<text x="22" y="64" fill="#58a6ff" font-family="monospace" '
        'font-size="13" font-weight="bold">ayaan0060@github</text>',
    ]
    current_y = 91
    step = 0.16
    index = 0
    for label, lines in row_lines:
        elements.append(
            f'<text x="22" y="{current_y}" fill="#7ee787" '
            f'font-family="monospace" font-size="11">{escape(label)}:</text>'
        )
        for line_num, line in enumerate(lines):
            y = current_y + line_num * LINE_HEIGHT
            text = (
                f'<text x="{PADDING + label_width}" y="{y}" fill="#c9d1d9" '
                f'font-family="monospace" font-size="11">{escape(line)}</text>'
            )
            if not static:
                text = (
                    f'<g opacity="0"><animate attributeName="opacity" from="0" '
                    f'to="1" begin="{index * step:.2f}s" dur="0.35s" '
                    f'fill="freeze"/>{text}</g>'
                )
            elements.append(text)
            index += 1
        current_y += max(1, len(lines)) * LINE_HEIGHT

    output.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
        f'height="{card_height}" viewBox="0 0 {WIDTH} {card_height}" '
        'role="img" aria-label="ayaan0060 profile information">'
        + "".join(elements)
        + "</svg>\n",
        encoding="utf-8",
    )
    print(f"Info card saved to {output}")


if __name__ == "__main__":
    render_info_card(Path("info-card.svg"), static=os.getenv("STATIC") == "1")
