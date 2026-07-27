#!/usr/bin/env python3
"""Render the exhaustive Medicine foundation manuscript to archival PDF."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/current/medicine/FROM_FOLD_TO_MEDICINE.md"
OUTPUT = ROOT / "output/pdf/from-fold-to-medicine-health-sciences-foundation-paper-001-v1.0.pdf"
METADATA = ROOT / "publication/medicine_foundation_zenodo_metadata.json"


def cover(authorized: bool, doi: str):
    title = ParagraphStyle("MedicineCoverTitle", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("MedicineCoverSubtitle", fontName="Helvetica", fontSize=13, leading=18, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("MedicineCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("MedicineCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("MedicineCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("MedicineCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    return [
        Spacer(1, 18 * mm),
        Paragraph("SMITHIAN FOLD THEORY - MEDICINE AND HEALTH SCIENCES PAPER 001", kicker),
        Paragraph("From Fold to Medicine", title),
        Spacer(1, 7 * mm),
        Paragraph("An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Medicine and Health Sciences from Smithian Fold Theory", subtitle),
        Spacer(1, 10 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 13 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 13 * mm),
        Paragraph("Version 1.0.0 - current-evidence closed, extension-open foundation<br/>72 required laws - 18,432 exact candidates<br/>27 July 2026" + (f"<br/>DOI: {doi}" if doi else "") + "<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
        Spacer(1, 8 * mm),
        Paragraph("PUBLISHED OPEN-ACCESS BRANCH PAPER" if authorized else "LOCAL PREPUBLICATION MANUSCRIPT - PUBLICATION NOT YET AUTHORIZED", warning),
    ]


def main() -> None:
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    def draw_page(canvas, doc):
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE)
            canvas.setLineWidth(0.4)
            canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1)
            canvas.setFillColor(base.MUTED)
            canvas.drawString(18 * mm, height - 11.8 * mm, "FROM FOLD TO MEDICINE - ERNOS LABS MEDICINE PAPER 001")
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            footer = f"Maria Smith - 2026 - CC BY 4.0 - DOI {doi}" if authorized else "Maria Smith - 2026 - CC BY 4.0 - LOCAL PREPUBLICATION"
            canvas.drawString(18 * mm, 11 * mm, footer)
        canvas.restoreState()

    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=21 * mm, bottomMargin=18 * mm, title="From Fold to Medicine", author="Maria Smith", subject="Foundational Smithian Fold Theory Medicine and Health Sciences branch", creator="Ernos Labs publication renderer")
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover(authorized, doi) + [PageBreak()] + base.body_story(SOURCE.read_text(encoding="utf-8")))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
