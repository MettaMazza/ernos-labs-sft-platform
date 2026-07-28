#!/usr/bin/env python3
"""Render the exhaustive Earth foundation manuscript to archival PDF."""

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
SOURCE = ROOT / "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md"
OUTPUT = ROOT / "output/pdf/from-one-world-to-earth-environment-foundation-paper-001-v1.0.pdf"
METADATA = ROOT / "publication/earth_environment_foundation_zenodo_metadata.json"


def cover(authorized: bool, doi: str):
    title = ParagraphStyle("EarthCoverTitle", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("EarthCoverSubtitle", fontName="Helvetica", fontSize=13, leading=18, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("EarthCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("EarthCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("EarthCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("EarthCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    return [
        Spacer(1, 15 * mm),
        Paragraph("SMITHIAN FOLD THEORY - EARTH AND ENVIRONMENTAL SCIENCES PAPER 001", kicker),
        Paragraph("From One World to Earth", title),
        Spacer(1, 7 * mm),
        Paragraph("An Exact, Zero-Parameter and Machine-Closed Foundational Reconstruction of Earth and Environmental Sciences from Smithian Fold Theory", subtitle),
        Spacer(1, 10 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 12 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 12 * mm),
        Paragraph("Version 1.0.0 - current-evidence closed, extension-open foundation<br/>74 required laws - 18,944 exact candidates<br/>28 July 2026" + (f"<br/>DOI: {doi}" if doi else "") + "<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
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
            canvas.drawString(18 * mm, height - 11.8 * mm, "FROM ONE WORLD TO EARTH - ERNOS LABS PAPER 001")
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            footer = f"Maria Smith - 2026 - CC BY 4.0 - DOI {doi}" if authorized else "Maria Smith - 2026 - CC BY 4.0 - LOCAL PREPUBLICATION"
            canvas.drawString(18 * mm, 11 * mm, footer)
        canvas.restoreState()

    document = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm,
        title="From One World to Earth", author="Maria Smith",
        subject="Foundational Smithian Fold Theory Earth and Environmental Sciences branch",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    source = SOURCE.read_text(encoding="utf-8").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    document.build(cover(authorized, doi) + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
