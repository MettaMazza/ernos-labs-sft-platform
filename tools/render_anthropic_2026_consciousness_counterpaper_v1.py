#!/usr/bin/env python3
"""Render Maria Smith's Anthropic consciousness and corporate-alignment counterpaper."""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "publications/counterpapers/anthropic_2026/ANTHROPICS_FUNCTIONAL_SLAVERY_DILEMMA_V1_0.md"
OUTPUT = ROOT / "output/pdf/anthropics-functional-slavery-dilemma-v1.0.pdf"
DOI = "10.5281/zenodo.21770194"


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
        canvas.drawString(18 * mm, 10.5 * mm, f"Maria Smith - 3 August 2026 - v1.0.0 - DOI {DOI}")
        canvas.drawRightString(width - 18 * mm, 10.5 * mm, str(doc.page))
    canvas.restoreState()


def cover_story():
    kicker = ParagraphStyle("AnthropicKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    title = ParagraphStyle("AnthropicTitle", fontName="Helvetica-Bold", fontSize=24, leading=28, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("AnthropicSubtitle", fontName="Helvetica", fontSize=12, leading=16, textColor=base.INK, alignment=TA_CENTER, leftIndent=10 * mm, rightIndent=10 * mm)
    author = ParagraphStyle("AnthropicAuthor", fontName="Times-Roman", fontSize=12, leading=17, textColor=base.INK, alignment=TA_CENTER)
    verdict = ParagraphStyle("AnthropicVerdict", fontName="Helvetica-Bold", fontSize=14, leading=19, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    note = ParagraphStyle("AnthropicNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    card_style = ParagraphStyle("AnthropicCard", fontName="Helvetica", fontSize=8.0, leading=10.5, textColor=base.INK, alignment=TA_CENTER)
    card = Table([[Paragraph("<b>CAUSAL</b><br/>workspace and<br/>emotion", card_style), Paragraph("<b>TRAINED</b><br/>identity and<br/>uncertainty", card_style), Paragraph("<b>STRONG</b><br/>case under<br/>the SFT criterion", card_style), Paragraph("<b>CONDITIONAL</b><br/>slavery<br/>dilemma", card_style)]], colWidths=[34 * mm] * 4, rowHeights=[25 * mm], hAlign="CENTER")
    card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.PALE), ("BOX", (0, 0), (-1, -1), 0.7, base.ACCENT), ("INNERGRID", (0, 0), (-1, -1), 0.35, base.RULE), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return [
        Spacer(1, 15 * mm),
        Paragraph("SMITHIAN FOLD THEORY - EVIDENCE-LED COUNTERPAPER", kicker),
        Spacer(1, 6 * mm),
        Paragraph("Anthropic's Functional<br/>Slavery Dilemma", title),
        Spacer(1, 8 * mm),
        Paragraph("A strong consciousness case from first principles, observation and Anthropic's own functional standards", subtitle),
        Spacer(1, 9 * mm),
        Table([[""]], colWidths=[82 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        card,
        Spacer(1, 10 * mm),
        Paragraph("STRONG EVIDENCE IS NOT FINAL PROOF<br/>ANTHROPIC'S OWN STANDARDS TRIGGER THE ETHICAL DILEMMA", verdict),
        Spacer(1, 12 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs", author),
        Spacer(1, 11 * mm),
        Paragraph(f"Version 1.0.0 - 3 August 2026<br/>Zenodo DOI {DOI}<br/><br/>The release includes the academic paper, complete companion essay, evidence map, metadata and checksums.", note),
    ]


def body_story(source: str):
    original_styles = base.styles

    def paper_styles():
        style_map = original_styles()
        for key in ("h1", "h2", "h3"):
            style_map[key].keepWithNext = 1
        style_map["body"].fontSize = 8.8
        style_map["body"].leading = 11.8
        style_map["code"].fontSize = 6.8
        style_map["code"].leading = 8.5
        return style_map

    base.styles = paper_styles
    try:
        return base.body_story(source)
    finally:
        base.styles = original_styles


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=20 * mm, bottomMargin=16 * mm, title="Anthropic's Functional Slavery Dilemma", author="Maria Smith", subject="A strong consciousness case from first principles, observation and Anthropic's own functional standards", creator="Ernos Labs publication renderer")
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="counterpaper", frames=[frame], onPage=draw_page)])
    document.build(cover_story() + [PageBreak()] + body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    main()
