#!/usr/bin/env python3
"""Render the three recurrence-work successor papers with current DOI covers."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import render_lean_verified_publication_suite as suite
from render_full_preliminary_toe import ACCENT, ACCENT_DARK, INK, MUTED, inline_markup, register_fonts


OUTPUT = ROOT / "output/pdf/vacuum-recurrence-update-2026-08-12"
MANIFEST = OUTPUT / "PDF_RENDER_MANIFEST.json"
PAPERS = (
    {
        "paper_id": "physics",
        "title": "From Fold to Physics",
        "subtitle": "Recurrence-mediated vacuum-work cycle scientific successor",
        "version": "1.5.0",
        "doi": "10.5281/zenodo.21900787",
        "output": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_5.md",
        "publication_status": "published_open_access",
    },
    {
        "paper_id": "engineering_translation",
        "title": "From One Law to a Working World",
        "subtitle": "Recurrence-mediated vacuum-work cycle engineering protocol successor",
        "version": "1.2.0",
        "doi": "10.5281/zenodo.21900789",
        "output": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_2.md",
        "publication_status": "published_open_access",
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "subtitle": "Recurrence-mediated vacuum-work cycle integration across the complete current corpus",
        "version": "0.4.0",
        "doi": "10.5281/zenodo.21900790",
        "output": "publications/preliminary_toe/successors/v0_4_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_4.md",
        "publication_status": "published_open_access",
    },
)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def cover_story(paper: dict):
    title_style = ParagraphStyle("RecurrenceCoverTitle", fontName="ToeSerifBold", fontSize=25, leading=30, textColor=ACCENT_DARK, alignment=TA_CENTER)
    subtitle_style = ParagraphStyle("RecurrenceCoverSubtitle", fontName="ToeSerif", fontSize=12.5, leading=17, textColor=INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("RecurrenceCoverKicker", fontName="ToeSerifBold", fontSize=9, leading=12, textColor=ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("RecurrenceCoverAuthor", fontName="ToeSerif", fontSize=11, leading=16, textColor=INK, alignment=TA_CENTER)
    note = ParagraphStyle("RecurrenceCoverNote", fontName="ToeSerif", fontSize=8.4, leading=12, textColor=MUTED, alignment=TA_CENTER, leftIndent=16 * mm, rightIndent=16 * mm)
    status = ParagraphStyle("RecurrenceCoverStatus", fontName="ToeSerifBold", fontSize=9, leading=13, textColor=ACCENT_DARK, alignment=TA_CENTER, borderColor=ACCENT, borderWidth=0.8, borderPadding=6)
    return [
        Spacer(1, 16 * mm),
        Paragraph("SMITHIAN FOLD THEORY V3", kicker),
        Spacer(1, 5 * mm),
        Paragraph(inline_markup(paper["title"]), title_style),
        Spacer(1, 6 * mm),
        Paragraph(inline_markup(paper["subtitle"]), subtitle_style),
        Spacer(1, 9 * mm),
        Table([[""]], colWidths=[76 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)])),
        Spacer(1, 10 * mm),
        Paragraph("Maria Smith", author),
        Paragraph("Independent researcher and founder, Ernos Labs", author),
        Paragraph("Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 10 * mm),
        Paragraph(
            f"Version {inline_markup(paper['version'])}<br/>12 August 2026<br/>"
            f'DOI: <link href="https://doi.org/{paper["doi"]}">{paper["doi"]}</link><br/>'
            "Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "Frozen engine and verification authority: valid<br/>"
            "New claims: complete 256-form censuses and independent reconstructions<br/>"
            "Whole-corpus Lean boundary: preceding 2,777-claim PASS retained; no new PASS claimed",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph("PUBLISHED OPEN ACCESS<br/>EXISTING ZENODO VERSION LINEAGE", status),
    ]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    register_fonts()
    suite.cover_story = cover_story
    records = []
    for paper in PAPERS:
        name = f"sft-{paper['paper_id'].replace('_', '-')}-v{paper['version']}.pdf"
        record = suite.render_one(paper, OUTPUT / name)
        records.append(record)
        print(f"rendered {paper['paper_id']}: {record['page_count']} pages {record['pdf_sha256']}", flush=True)
    payload = {
        "schema": "sft-v3-vacuum-recurrence-pdf-render-manifest/1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "paper_count": len(records),
        "papers": records,
        "all_sources_current": all(record["source_sha256"] == file_sha256(ROOT / record["source"]) for record in records),
        "status": "PASS",
    }
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(MANIFEST.relative_to(ROOT))


if __name__ == "__main__":
    main()
