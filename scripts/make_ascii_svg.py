#!/usr/bin/env python3
"""Convert a prepared grayscale photo into a self-typing ASCII SVG."""

from pathlib import Path

import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"
COLS = 100
ROWS = 53
CELL_WIDTH = 4
LINE_HEIGHT = 7
FONT_SIZE = 6


def render_ascii_svg(source: Path, output: Path) -> None:
    image = Image.open(source).convert("L")
    height = max(1, round(image.height * COLS / image.width * 0.52))
    image = image.resize((COLS, height), Image.Resampling.LANCZOS)

    canvas = Image.new("L", (COLS, ROWS), 255)
    top = max(0, (ROWS - height) // 2)
    canvas.paste(image.crop((0, 0, COLS, min(height, ROWS))), (0, top))
    pixels = np.asarray(canvas)
    svg_width = COLS * CELL_WIDTH
    svg_height = ROWS * LINE_HEIGHT
    rows = []

    for row in range(ROWS):
        text = "".join(
            RAMP[min(len(RAMP) - 1, int(pixel) * (len(RAMP) - 1) // 255)]
            for pixel in pixels[row]
        )
        delay = row * 0.12
        rows.append(
            f'<text x="0" y="{(row + 1) * LINE_HEIGHT}" '
            f'clip-path="url(#row-{row})">{text}</text>'
            f'<clipPath id="row-{row}"><rect x="0" y="{row * LINE_HEIGHT}" '
            f'width="0" height="{LINE_HEIGHT}"><animate attributeName="width" '
            f'from="0" to="{svg_width}" begin="{delay:.2f}s" dur="0.8s" '
            'fill="freeze"/></rect></clipPath>'
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" '
        f'height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" '
        'role="img" aria-label="Animated monochrome ASCII portrait">'
        '<rect width="100%" height="100%" fill="#0d1117"/>'
        '<g fill="#c9d1d9" font-family="monospace" '
        f'font-size="{FONT_SIZE}" xml:space="preserve">'
        + "".join(rows)
        + "</g></svg>\n",
        encoding="utf-8",
    )
    print(f"ASCII portrait saved to {output}")


if __name__ == "__main__":
    render_ascii_svg(Path("data/source-prepped.png"), Path("ayaan-ascii.svg"))
