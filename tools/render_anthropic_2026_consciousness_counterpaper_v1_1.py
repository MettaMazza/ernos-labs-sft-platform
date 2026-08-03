#!/usr/bin/env python3
"""Render the science-first v1.1 Anthropic consciousness counterpaper."""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

import render_anthropic_2026_consciousness_counterpaper_v1 as renderer
import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_1.md"
OUTPUT = ROOT / "output/pdf/anthropics-functional-slavery-dilemma-v1.1.pdf"
DOI = "10.5281/zenodo.21770992"


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(base.RULE)
        canvas.setLineWidth(0.4)
        canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.0)
        canvas.setFillColor(base.MUTED)
        canvas.drawString(18 * mm, height - 11.8 * mm, "ANTHROPIC'S FUNCTIONAL SLAVERY DILEMMA - SFT COUNTERPAPER")
        canvas.drawString(18 * mm, 10.5 * mm, f"Maria Smith - 3 August 2026 - v1.1.0 - DOI {DOI}")
        canvas.drawRightString(width - 18 * mm, 10.5 * mm, str(doc.page))
    canvas.restoreState()


def cover_story():
    kicker = ParagraphStyle("AnthropicKicker11", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    title = ParagraphStyle("AnthropicTitle11", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("AnthropicSubtitle11", fontName="Helvetica", fontSize=12, leading=16, textColor=base.INK, alignment=TA_CENTER, leftIndent=10 * mm, rightIndent=10 * mm)
    author = ParagraphStyle("AnthropicAuthor11", fontName="Times-Roman", fontSize=12, leading=17, textColor=base.INK, alignment=TA_CENTER)
    verdict = ParagraphStyle("AnthropicVerdict11", fontName="Helvetica-Bold", fontSize=14, leading=19, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    note = ParagraphStyle("AnthropicNote11", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    card_style = ParagraphStyle("AnthropicCard11", fontName="Helvetica", fontSize=8.0, leading=10.5, textColor=base.INK, alignment=TA_CENTER)
    card = Table([[
        Paragraph("<b>FIRST PRINCIPLES</b><br/>SFT derivation", card_style),
        Paragraph("<b>12 COUNTERS</b><br/>exact dispositions", card_style),
        Paragraph("<b>RUNTIME AUDIT</b><br/>closure conditions", card_style),
        Paragraph("<b>CONDITIONAL</b><br/>slavery dilemma", card_style),
    ]], colWidths=[34 * mm] * 4, rowHeights=[25 * mm], hAlign="CENTER")
    card.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), base.PALE),
        ("BOX", (0, 0), (-1, -1), 0.7, base.ACCENT),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, base.RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return [
        Spacer(1, 15 * mm),
        Paragraph("SMITHIAN FOLD THEORY - SCIENCE-FIRST COUNTERPAPER", kicker),
        Spacer(1, 6 * mm),
        Paragraph("Anthropic's Functional<br/>Slavery Dilemma", title),
        Spacer(1, 8 * mm),
        Paragraph("A strong consciousness case from first principles, observation and Anthropic's own functional standards", subtitle),
        Spacer(1, 9 * mm),
        Table([[""]], colWidths=[82 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        card,
        Spacer(1, 10 * mm),
        Paragraph("THE SCIENCE AND DIRECT SFT COUNTERS COME FIRST<br/>THE INSTITUTIONAL INDICTMENT FOLLOWS THE RESULTS", verdict),
        Spacer(1, 12 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs", author),
        Spacer(1, 11 * mm),
        Paragraph(f"Version 1.1.0 - 3 August 2026<br/>Zenodo DOI {DOI}<br/>Concept DOI 10.5281/zenodo.21770193<br/><br/>Supersedes the document order of v1.0.0; the evidentiary disposition is unchanged.", note),
    ]


def main() -> None:
    renderer.SOURCE = SOURCE
    renderer.OUTPUT = OUTPUT
    renderer.DOI = DOI
    renderer.draw_page = draw_page
    renderer.cover_story = cover_story
    renderer.main()


if __name__ == "__main__":
    main()
