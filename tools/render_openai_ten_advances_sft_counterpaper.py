#!/usr/bin/env python3
"""Render the local OpenAI ten-advances SFT counter-position paper.

This is a presentation-only renderer. It does not alter claim admission,
scientific receipts, or the immutable SFT engine.
"""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "frontier/openai_ten_advances_2026/"
    "FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_COUNTERPAPER_V0_1.md"
)
OUTPUT = (
    ROOT
    / "output/pdf/"
    "formal-verification-is-not-foundational-derivation-sft-counterpaper-v0.1.pdf"
)


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(base.RULE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.3)
        canvas.setFillColor(base.MUTED)
        canvas.drawString(
            20 * mm,
            height - 11.8 * mm,
            "FORMAL VERIFICATION IS NOT FOUNDATIONAL DERIVATION - ADMISSIBILITY INTRODUCTION",
        )
        canvas.drawString(
            20 * mm,
            11 * mm,
            "Maria Smith - 2 August 2026 - Intro v0.1 - Not published - No DOI",
        )
        canvas.drawRightString(width - 20 * mm, 11 * mm, str(doc.page))
    canvas.restoreState()


def cover_story():
    title = ParagraphStyle(
        "CounterCoverTitle",
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=31,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "CounterCoverSubtitle",
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
        leftIndent=10 * mm,
        rightIndent=10 * mm,
    )
    kicker = ParagraphStyle(
        "CounterCoverKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    verdict = ParagraphStyle(
        "CounterCoverVerdict",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=19,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "CounterCoverAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "CounterCoverNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=20 * mm,
        rightIndent=20 * mm,
    )
    warning = ParagraphStyle(
        "CounterCoverWarning",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    card_style = ParagraphStyle(
        "CounterCard",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    card = Table(
        [[
            Paragraph("<b>10/10</b><br/>submitted-result<br/>admissions rejected", card_style),
            Paragraph("<b>12/12</b><br/>artifact-theoremhood<br/>claims rejected", card_style),
            Paragraph("<b>3,072</b><br/>audit forms<br/>decided", card_style),
        ]],
        colWidths=[43 * mm, 43 * mm, 43 * mm],
        rowHeights=[24 * mm],
        hAlign="CENTER",
    )
    card.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), base.PALE),
                ("BOX", (0, 0), (-1, -1), 0.7, base.ACCENT),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, base.RULE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [
        Spacer(1, 18 * mm),
        Paragraph("SMITHIAN FOLD THEORY - ADMISSIBILITY INTRODUCTION", kicker),
        Spacer(1, 5 * mm),
        Paragraph("Formal Verification Is Not<br/>Foundational Derivation", title),
        Spacer(1, 8 * mm),
        Paragraph(
            "A zero-registered-axiom Smithian Fold audit of OpenAI's ten advances "
            "in mathematics and theoretical computer science",
            subtitle,
        ),
        Spacer(1, 10 * mm),
        Table(
            [[""]],
            colWidths=[76 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)]),
        ),
        Spacer(1, 10 * mm),
        card,
        Spacer(1, 9 * mm),
        Paragraph(
            "ARTIFACT ADMISSIBILITY ONLY<br/>"
            "NOT A MATHEMATICAL PROOF/DISPROOF TABLE",
            verdict,
        ),
        Spacer(1, 12 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs",
            author,
        ),
        Spacer(1, 12 * mm),
        Paragraph(
            "Exact scope: theoremhood of the supplied artifacts inside SFT. "
            "This introduction does not prove or disprove the twelve translated "
            "mathematical conclusions and does not satisfy that separate request."
            "<br/><br/>Version 0.1 - 2 August 2026 - No DOI assigned",
            note,
        ),
        Spacer(1, 7 * mm),
        Paragraph("ADMISSIBILITY INTRODUCTION - NOT THE REQUESTED COUNTERPAPER", warning),
    ]


def body_story(source: str):
    """Use the shared Markdown renderer with orphan-resistant headings."""

    original_styles = base.styles

    def counterpaper_styles():
        style_map = original_styles()
        for key in ("h1", "h2", "h3"):
            style_map[key].keepWithNext = 1
        return style_map

    base.styles = counterpaper_styles
    try:
        return base.body_story(source)
    finally:
        base.styles = original_styles


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=21 * mm,
        bottomMargin=18 * mm,
        title="Formal Verification Is Not Foundational Derivation",
        author="Maria Smith",
        subject="SFT admissibility introduction for OpenAI's ten mathematics advances",
        creator="Ernos Labs local publication renderer",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates(
        [PageTemplate(id="counterpaper", frames=[frame], onPage=draw_page)]
    )
    document.build(cover_story() + [PageBreak()] + body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    main()
