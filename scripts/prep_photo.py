#!/usr/bin/env python3
"""Remove a photo background and prepare a high-contrast grayscale portrait."""

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def prepare_photo(source: Path, output: Path) -> None:
    image = Image.open(source).convert("RGBA")

    try:
        from rembg import new_session, remove
    except ImportError:
        print("rembg is not installed; keeping the original background.")
    else:
        image = remove(image, session=new_session("u2netp"))

    background = Image.new("RGBA", image.size, "white")
    background.alpha_composite(image)
    grayscale = np.asarray(background.convert("L"))
    contrast = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(grayscale)

    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(contrast).save(output)
    print(f"Prepared photo saved to {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photo", type=Path, help="Source photo")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/source-prepped.png"),
        help="Output path (default: data/source-prepped.png)",
    )
    args = parser.parse_args()
    if not args.photo.is_file():
        parser.error(f"photo does not exist: {args.photo}")
    prepare_photo(args.photo, args.output)


if __name__ == "__main__":
    main()
