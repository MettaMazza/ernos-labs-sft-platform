#!/usr/bin/env python3
"""Render every page of the Lean-verified PDF suite for visual QA."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RENDER_MANIFEST = (
    ROOT / "output/pdf/lean4_verified_2026-08-02/PDF_RENDER_MANIFEST.json"
)
DEFAULT_OUTPUT = ROOT / "output/qa/lean4_verified_2026-08-02"
COLS = 12
ROWS = 14
PAGES_PER_SHEET = COLS * ROWS
CELL_WIDTH = 148
CELL_HEIGHT = 210
HEADER_HEIGHT = 42


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_font(size: int):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


SMALL_FONT = safe_font(11)
HEADER_FONT = safe_font(20)


def page_image(page: fitz.Page, scale: float) -> Image.Image:
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def contact_sheets(paper: dict, document: fitz.Document, output_dir: Path) -> list[dict]:
    paper_dir = output_dir / "contact_sheets" / paper["paper_id"]
    paper_dir.mkdir(parents=True, exist_ok=True)
    records = []
    sheet_count = math.ceil(document.page_count / PAGES_PER_SHEET)
    for sheet_index in range(sheet_count):
        first = sheet_index * PAGES_PER_SHEET
        last = min(first + PAGES_PER_SHEET, document.page_count)
        canvas = Image.new(
            "RGB",
            (COLS * CELL_WIDTH, HEADER_HEIGHT + ROWS * CELL_HEIGHT),
            (224, 224, 224),
        )
        draw = ImageDraw.Draw(canvas)
        heading = (
            f"{paper['paper_id']} v{paper['version']} — pages {first + 1}-{last} "
            f"— sheet {sheet_index + 1}/{sheet_count}"
        )
        draw.text((12, 9), heading, fill=(20, 20, 20), font=HEADER_FONT)
        for offset, page_index in enumerate(range(first, last)):
            row, col = divmod(offset, COLS)
            x = col * CELL_WIDTH
            y = HEADER_HEIGHT + row * CELL_HEIGHT
            image = page_image(document[page_index], 0.22)
            image.thumbnail((CELL_WIDTH - 8, CELL_HEIGHT - 22), Image.Resampling.LANCZOS)
            paste_x = x + (CELL_WIDTH - image.width) // 2
            paste_y = y + 3
            canvas.paste(image, (paste_x, paste_y))
            draw.rectangle((x, y, x + CELL_WIDTH - 1, y + CELL_HEIGHT - 1), outline=(180, 180, 180))
            draw.text((x + 5, y + CELL_HEIGHT - 17), f"p{page_index + 1}", fill=(25, 25, 25), font=SMALL_FONT)
        path = paper_dir / f"sheet-{sheet_index + 1:03d}-pages-{first + 1:05d}-{last:05d}.jpg"
        canvas.save(path, "JPEG", quality=82, optimize=True, progressive=True)
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": f"sha256:{file_sha256(path)}",
                "first_page": first + 1,
                "last_page": last,
                "page_count": last - first,
            }
        )
        print(
            f"  contact {sheet_index + 1}/{sheet_count}: pages {first + 1}-{last}",
            flush=True,
        )
    return records


def key_page_sheet(paper: dict, document: fitz.Document, output_dir: Path) -> dict:
    selected = sorted(
        {
            0,
            min(1, document.page_count - 1),
            min(2, document.page_count - 1),
            document.page_count // 2,
            document.page_count - 1,
        }
    )
    width = 3 * 465
    height = 2 * 675 + 48
    canvas = Image.new("RGB", (width, height), (225, 225, 225))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (12, 10),
        f"{paper['paper_id']} v{paper['version']} — key-page visual QA",
        fill=(20, 20, 20),
        font=HEADER_FONT,
    )
    for offset, page_index in enumerate(selected):
        row, col = divmod(offset, 3)
        x = col * 465
        y = 48 + row * 675
        image = page_image(document[page_index], 0.78)
        image.thumbnail((445, 630), Image.Resampling.LANCZOS)
        canvas.paste(image, (x + (465 - image.width) // 2, y + 4))
        draw.text((x + 9, y + 645), f"page {page_index + 1}", fill=(20, 20, 20), font=SMALL_FONT)
    path = output_dir / "key_pages" / f"{paper['paper_id']}-key-pages.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "JPEG", quality=88, optimize=True, progressive=True)
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": f"sha256:{file_sha256(path)}",
        "pages": [page_index + 1 for page_index in selected],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-manifest", type=Path, default=DEFAULT_RENDER_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    render_path = arguments.render_manifest.resolve()
    output_dir = arguments.output_dir.resolve()
    manifest = json.loads(render_path.read_text(encoding="utf-8"))
    records = []
    for index, paper in enumerate(manifest["papers"], start=1):
        print(f"[{index}/{len(manifest['papers'])}] {paper['paper_id']}", flush=True)
        pdf_path = ROOT / paper["pdf"]
        with fitz.open(pdf_path) as document:
            contacts = contact_sheets(paper, document, output_dir)
            key_sheet = key_page_sheet(paper, document, output_dir)
        records.append(
            {
                "paper_id": paper["paper_id"],
                "version": paper["version"],
                "pdf": paper["pdf"],
                "pdf_sha256": paper["pdf_sha256"],
                "page_count": paper["page_count"],
                "contact_sheet_count": len(contacts),
                "contact_sheets": contacts,
                "key_page_sheet": key_sheet,
            }
        )
    payload = {
        "schema": "sft.lean4_verified_visual_qa_contact_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "render_manifest": str(render_path.relative_to(ROOT)),
        "render_manifest_sha256": f"sha256:{file_sha256(render_path)}",
        "paper_count": len(records),
        "page_count": sum(record["page_count"] for record in records),
        "contact_sheet_count": sum(record["contact_sheet_count"] for record in records),
        "key_page_sheet_count": len(records),
        "papers": records,
        "visual_review_status": "AWAITING_REVIEW",
        "publication_authorized": bool(manifest.get("publication_authorized")),
        "remote_actions_performed": [],
    }
    manifest_path = output_dir / "CONTACT_SHEET_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "papers": payload["paper_count"],
                "pages": payload["page_count"],
                "contact_sheets": payload["contact_sheet_count"],
                "key_page_sheets": payload["key_page_sheet_count"],
                "manifest": str(manifest_path.relative_to(ROOT)),
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
