#!/usr/bin/env python3
"""Sharpen environment PNGs without changing dimensions or alpha coverage."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageFilter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("images", nargs="+", type=Path)
    parser.add_argument("--radius", type=float, default=0.9)
    parser.add_argument("--percent", type=int, default=175)
    parser.add_argument("--threshold", type=int, default=1)
    return parser.parse_args()


def sharpen_in_place(
    path: Path,
    *,
    radius: float,
    percent: int,
    threshold: int,
) -> None:
    with Image.open(path) as source:
        rgba = source.convert("RGBA")
        alpha = rgba.getchannel("A")
        sharpened = rgba.convert("RGB").filter(
            ImageFilter.UnsharpMask(
                radius=radius,
                percent=percent,
                threshold=threshold,
            )
        )
        sharpened.putalpha(alpha)
        sharpened.save(path, format="PNG", optimize=True)


def main() -> None:
    args = parse_args()
    for image in args.images:
        if image.suffix.lower() != ".png" or not image.is_file():
            raise SystemExit(f"Expected an existing PNG: {image}")
        sharpen_in_place(
            image,
            radius=args.radius,
            percent=args.percent,
            threshold=args.threshold,
        )
        print(image)


if __name__ == "__main__":
    main()
