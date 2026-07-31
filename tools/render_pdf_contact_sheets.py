#!/usr/bin/env python3
"""Render every PDF page to labelled contact sheets for complete visual QA."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


def page_image(page: fitz.Page, dpi: int) -> Image.Image:
    scale = dpi / 72
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--columns", type=int, default=5)
    parser.add_argument("--rows", type=int, default=8)
    parser.add_argument("--thumbnail-dpi", type=int, default=30)
    parser.add_argument("--sample-dpi", type=int, default=150)
    parser.add_argument("--sample-pages", default="")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(args.pdf)
    per_sheet = args.columns * args.rows
    font = ImageFont.load_default()
    first = page_image(document[0], args.thumbnail_dpi)
    tile_width = first.width + 12
    tile_height = first.height + 25
    sheets = math.ceil(len(document) / per_sheet)
    for sheet_number in range(sheets):
        canvas = Image.new(
            "RGB",
            (args.columns * tile_width, args.rows * tile_height),
            "#d8d2cd",
        )
        draw = ImageDraw.Draw(canvas)
        start = sheet_number * per_sheet
        stop = min(start + per_sheet, len(document))
        for page_index in range(start, stop):
            row, column = divmod(page_index - start, args.columns)
            rendered = page_image(document[page_index], args.thumbnail_dpi)
            x = column * tile_width + 6
            y = row * tile_height + 19
            canvas.paste(rendered, (x, y))
            draw.text((x, y - 15), f"p. {page_index + 1}", fill="#21150f", font=font)
        destination = args.output_dir / f"{args.prefix}-contact-{sheet_number + 1:03d}.png"
        canvas.save(destination, optimize=True)

    samples = []
    if args.sample_pages.strip():
        samples = sorted(
            {
                int(value)
                for value in args.sample_pages.split(",")
                if value.strip()
            }
        )
    for page_number in samples:
        if not 1 <= page_number <= len(document):
            raise ValueError(f"sample page outside 1..{len(document)}: {page_number}")
        rendered = page_image(document[page_number - 1], args.sample_dpi)
        rendered.save(
            args.output_dir / f"{args.prefix}-sample-{page_number:04d}.png",
            optimize=True,
        )
    print(
        f"rendered {len(document)} pages to {sheets} contact sheets and "
        f"{len(samples)} detailed samples"
    )


if __name__ == "__main__":
    main()
