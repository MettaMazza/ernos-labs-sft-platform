#!/usr/bin/env python3
"""Render the exhaustive Physics branch manuscript to an archival PDF."""

from __future__ import annotations

import json
import os
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get("SFT_PHYSICS_PAPER_SOURCE", ROOT / "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md")).resolve()
OUTPUT = Path(os.environ.get("SFT_PHYSICS_PDF_OUTPUT", ROOT / "output/pdf/from-fold-to-physics-branch-paper-001-v1.3.pdf")).resolve()
METADATA = Path(os.environ.get("SFT_PHYSICS_METADATA", ROOT / "publications/successors/physics/zenodo_metadata_v1_3.json")).resolve()


def cover(authorized: bool, doi: str, statistics: str, version: str):
    title = ParagraphStyle("PhysicsCoverTitle", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("PhysicsCoverSubtitle", fontName="Helvetica", fontSize=13, leading=18, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("PhysicsCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("PhysicsCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("PhysicsCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("PhysicsCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    result = ParagraphStyle("PhysicsCoverResult", fontName="Helvetica-Bold", fontSize=13, leading=18, textColor=base.ACCENT_DARK, alignment=TA_CENTER, leftIndent=12 * mm, rightIndent=12 * mm)
    return [
        Spacer(1, 18 * mm),
        Paragraph("SMITHIAN FOLD THEORY - PHYSICS BRANCH PAPER 001", kicker),
        Paragraph("From Fold to Physics", title),
        Spacer(1, 7 * mm),
        Paragraph("An Exact, Parameter-Free and Machine-Closed Reconstruction of Physical Science from Smithian Fold Theory", subtitle),
        Spacer(1, 7 * mm),
        Paragraph("Lead result: exact first-principles fine-structure constant<br/>alpha<super>-1</super> = 503846395469 / 3676744786 = 137.035999177180855...", result),
        Spacer(1, 7 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 9 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 9 * mm),
        Paragraph(f"Corrected and expanded complete-field edition<br/>Version {version}<br/>" + statistics + (f"<br/>Reserved DOI: {doi}" if doi else "<br/>Version DOI pending archival deposit") + "<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
        Spacer(1, 8 * mm),
        Paragraph("PUBLISHED OPEN-ACCESS BRANCH PAPER" if authorized else "FINAL PUBLICATION CANDIDATE - RELEASE NOT YET AUTHORISED", warning),
    ]


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    authorized = bool(metadata["publication_authorized"]); doi = str(metadata.get("doi", ""))
    version = str(metadata.get("metadata", {}).get("version", "unversioned"))
    inventory = json.loads((ROOT / "publications/inventories/physics.json").read_text(encoding="utf-8"))
    obligations = inventory["obligations"]
    candidate_total = sum(
        json.loads((ROOT / "claims" / row["claim_id"] / "candidate_census.json").read_text(encoding="utf-8"))["expected_cardinality"]
        for row in obligations
    )
    statistics = (
        f"{len(obligations)} current engine-admitted derivations - 488/488 categorical Physics atoms closed, lawful extensions open"
        f"<br/>{candidate_total:,} Physics candidates - {4 * len(obligations):,} mandatory adverse controls - 29 July 2026"
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    def draw_page(canvas, doc):
        canvas.saveState(); width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE); canvas.setLineWidth(0.4)
            canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1); canvas.setFillColor(base.MUTED)
            canvas.drawString(18 * mm, height - 11.8 * mm, "FROM FOLD TO PHYSICS - ERNOS LABS PHYSICS PAPER 001")
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            footer = f"Maria Smith - 2026 - CC BY 4.0 - DOI {doi}" if authorized else "Maria Smith - 2026 - CC BY 4.0 - FINAL CANDIDATE / UNRELEASED"
            canvas.drawString(18 * mm, 11 * mm, footer)
        canvas.restoreState()

    document = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm, title="From Fold to Physics",
        author="Maria Smith", subject="Completed Smithian Fold Theory Physics branch",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover(authorized, doi, statistics, version) + [PageBreak()] + base.body_story(SOURCE.read_text(encoding="utf-8")))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
