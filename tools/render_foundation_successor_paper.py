#!/usr/bin/env python3
"""Render Foundation Branch Paper 001 version 1.1 to archival PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_1.md"
OUTPUT = ROOT / "output/pdf/from-nothing-to-fold-foundation-branch-paper-001-v1.1.pdf"


def draw_page(canvas, doc):
    canvas.saveState(); width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(base.RULE); canvas.setLineWidth(0.4)
        canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.2); canvas.setFillColor(base.MUTED)
        canvas.drawString(20 * mm, height - 11.8 * mm, "FROM NOTHING TO FOLD - FOUNDATION BRANCH PAPER 001 - VERSION 1.1")
        canvas.drawRightString(width - 20 * mm, 11 * mm, str(doc.page))
        canvas.drawString(20 * mm, 11 * mm, "Maria Smith - 2026 - CC BY 4.0 - expanded technical and empirical patch")
    canvas.restoreState()


def cover_story():
    title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=29, leading=34, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("Subtitle", fontName="Helvetica", fontSize=14, leading=20, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("Kicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("Author", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("Note", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=23 * mm, rightIndent=23 * mm)
    return [
        Spacer(1, 27 * mm),
        Paragraph("SMITHIAN FOLD THEORY - FOUNDATION BRANCH PAPER 001 - VERSION 1.1", kicker),
        Paragraph("From Nothing to Fold", title),
        Spacer(1, 7 * mm),
        Paragraph("A Premise-Free, Parameter-Free and Machine-Closed Foundation for Smithian Fold Theory", subtitle),
        Spacer(1, 11 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 11 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 17 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 18 * mm),
        Paragraph("Third clean-room reconstruction - expanded Foundation patch<br/>16 admitted theorems - 5,222 generated candidate classes - 32/32 prior obligations closed<br/>Version 1.1.0 - 24 July 2026<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
    ]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    if any(character in source for character in ("—", "–", "‑")):
        raise SystemExit("paper contains a non-ASCII dash")
    doc = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=21 * mm, bottomMargin=18 * mm, title="From Nothing to Fold: Foundation Branch Paper 001 version 1.1", author="Maria Smith", subject="Expanded technical and empirical Smithian Fold Theory Foundation", creator="Ernos Labs publication renderer")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    doc.build(cover_story() + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__": main()
