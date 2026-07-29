#!/usr/bin/env python3
"""Rasterise every publication-candidate PDF page and build review sheets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

import audit_publication_pdfs_v1 as pdfs


THUMB_WIDTH = 120
THUMB_HEIGHT = 170
LABEL_HEIGHT = 14
COLUMNS = 10
ROWS = 20
PAGES_PER_SHEET = COLUMNS * ROWS


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    total_pages = 0
    for paper in pdfs.PAPERS:
        path = pdfs.ROOT / paper.pdf
        document = fitz.open(path)
        expected = len(document)
        total_pages += expected
        sheet_count = math.ceil(expected / PAGES_PER_SHEET)
        sheets = [
            Image.new(
                "L",
                (COLUMNS * THUMB_WIDTH, ROWS * (THUMB_HEIGHT + LABEL_HEIGHT)),
                255,
            )
            for _ in range(sheet_count)
        ]
        rendered = 0
        failures = []
        near_blank = []
        edge_ink = []

        for index, page in enumerate(document):
            try:
                matrix = fitz.Matrix(THUMB_WIDTH / page.rect.width, THUMB_HEIGHT / page.rect.height)
                pixmap = page.get_pixmap(matrix=matrix, colorspace=fitz.csGRAY, alpha=False)
                image = Image.frombytes("L", (pixmap.width, pixmap.height), pixmap.samples)
                if image.size != (THUMB_WIDTH, THUMB_HEIGHT):
                    image = image.resize((THUMB_WIDTH, THUMB_HEIGHT))
                pixels = list(image.getdata())
                ink = sum(value < 245 for value in pixels)
                coverage = ink / len(pixels)
                if coverage < 0.002:
                    near_blank.append({"page": index + 1, "ink_coverage": coverage})
                border = []
                border.extend(image.crop((0, 0, THUMB_WIDTH, 2)).getdata())
                border.extend(image.crop((0, THUMB_HEIGHT - 2, THUMB_WIDTH, THUMB_HEIGHT)).getdata())
                border.extend(image.crop((0, 2, 2, THUMB_HEIGHT - 2)).getdata())
                border.extend(image.crop((THUMB_WIDTH - 2, 2, THUMB_WIDTH, THUMB_HEIGHT - 2)).getdata())
                if any(value < 220 for value in border):
                    edge_ink.append(index + 1)

                sheet_index = index // PAGES_PER_SHEET
                slot = index % PAGES_PER_SHEET
                column = slot % COLUMNS
                row = slot // COLUMNS
                x = column * THUMB_WIDTH
                y = row * (THUMB_HEIGHT + LABEL_HEIGHT)
                sheets[sheet_index].paste(image, (x, y + LABEL_HEIGHT))
                draw = ImageDraw.Draw(sheets[sheet_index])
                draw.text((x + 2, y + 1), f"p{index + 1}", fill=0)
                rendered += 1
            except Exception as error:  # pragma: no cover - publication fail path
                failures.append({"page": index + 1, "error": repr(error)})

        sheet_files = []
        for index, sheet in enumerate(sheets, 1):
            destination = output_dir / f"{paper.branch}-{index:02d}-of-{sheet_count:02d}.png"
            sheet.save(destination, optimize=True)
            sheet_files.append(
                {
                    "path": destination.as_posix(),
                    "sha256": "sha256:" + hashlib.sha256(destination.read_bytes()).hexdigest(),
                }
            )
        document.close()
        report_failures = []
        if rendered != expected:
            report_failures.append(f"rendered {rendered}/{expected} pages")
        if failures:
            report_failures.append(f"{len(failures)} raster failures")
        if near_blank:
            report_failures.append(f"{len(near_blank)} near-blank raster pages")
        if edge_ink:
            report_failures.append(f"{len(edge_ink)} pages have ink at the outer two-pixel border")
        reports.append(
            {
                "branch": paper.branch,
                "pdf": paper.pdf,
                "pages": expected,
                "rendered_pages": rendered,
                "contact_sheets": sheet_files,
                "near_blank_pages": near_blank,
                "edge_ink_pages": edge_ink,
                "raster_failures": failures,
                "failures": report_failures,
                "status": "PASS" if not report_failures else "HALT",
            }
        )

    result = {
        "schema": "sft-v3-final-publication-pdf-raster-review/1",
        "thumbnail": {
            "width": THUMB_WIDTH,
            "height": THUMB_HEIGHT,
            "pages_per_contact_sheet": PAGES_PER_SHEET,
        },
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "halts": sum(report["status"] != "PASS" for report in reports),
            "pages_rasterised": sum(report["rendered_pages"] for report in reports),
            "contact_sheets": sum(len(report["contact_sheets"]) for report in reports),
        },
    }
    rendered_json = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = pdfs.ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered_json, encoding="utf-8")
    else:
        print(rendered_json, end="")
    print(
        f"publication PDF raster review v1: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['pages_rasterised']:,} pages rasterised; "
        f"{result['summary']['contact_sheets']} sheets"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
