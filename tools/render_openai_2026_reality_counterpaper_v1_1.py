#!/usr/bin/env python3
"""Render the evidence-led OpenAI 2026 SFT counterpaper successor."""

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
SOURCE = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1.md"
OUTPUT = ROOT / "output/pdf/openai-ten-mathematical-advances-fail-the-reality-test-sft-counterpaper-v1.1.pdf"
ZENODO_DOI = "10.5281/zenodo.21768714"
PRIOR_ZENODO_DOI = "10.5281/zenodo.21760208"
UNICODE_MONO = Path(
    "/Users/mettamazza/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/"
    "libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/"
    "truetype/DejaVuSansMono.ttf"
)

if not UNICODE_MONO.exists():
    raise FileNotFoundError(f"Unicode monospaced font missing: {UNICODE_MONO}")
pdfmetrics.registerFont(TTFont("SFTUnicodeMono", str(UNICODE_MONO)))


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(base.RULE)
        canvas.setLineWidth(0.4)
        canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.0)
        canvas.setFillColor(base.MUTED)
        canvas.drawString(
            18 * mm,
            height - 11.8 * mm,
            "OPENAI'S TEN MATHEMATICAL ADVANCES FAIL THE REALITY TEST — SFT COUNTERPAPER",
        )
        canvas.drawString(
            18 * mm,
            10.5 * mm,
            f"Maria Smith — 3 August 2026 — v1.1.0 — DOI {ZENODO_DOI}",
        )
        canvas.drawRightString(width - 18 * mm, 10.5 * mm, str(doc.page))
    canvas.restoreState()


def cover_story():
    kicker = ParagraphStyle(
        "SourceValidityKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    title = ParagraphStyle(
        "SourceValidityTitle",
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=29,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "SourceValiditySubtitle",
        fontName="Helvetica",
        fontSize=12.5,
        leading=17,
        textColor=base.INK,
        alignment=TA_CENTER,
        leftIndent=10 * mm,
        rightIndent=10 * mm,
    )
    author = ParagraphStyle(
        "SourceValidityAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=17,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    verdict = ParagraphStyle(
        "SourceValidityVerdict",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=20,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "SourceValidityNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=18 * mm,
        rightIndent=18 * mm,
    )
    card_style = ParagraphStyle(
        "SourceValidityCard",
        fontName="Helvetica",
        fontSize=8.2,
        leading=11,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    card = Table(
        [[
            Paragraph("<b>10/10</b><br/>public claims<br/>rejected", card_style),
            Paragraph("<b>12/12</b><br/>SFT replacements<br/>proved", card_style),
            Paragraph("<b>2,777</b><br/>claims across<br/>17 branches", card_style),
            Paragraph("<b>2,378</b><br/>external packages<br/>passed", card_style),
        ]],
        colWidths=[34 * mm, 34 * mm, 34 * mm, 34 * mm],
        rowHeights=[25 * mm],
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
        Spacer(1, 15 * mm),
        Paragraph("SMITHIAN FOLD THEORY — EVIDENCE-LED COUNTERPAPER", kicker),
        Spacer(1, 6 * mm),
        Paragraph("OpenAI's Ten Mathematical<br/>Advances Fail the Reality Test", title),
        Spacer(1, 8 * mm),
        Paragraph(
            "Twelve closed SFT disproofs and replacements grounded in the "
            "first-principles derivation of constants, forces and cross-domain law",
            subtitle,
        ),
        Spacer(1, 9 * mm),
        Table(
            [[""]],
            colWidths=[82 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)]),
        ),
        Spacer(1, 10 * mm),
        card,
        Spacer(1, 10 * mm),
        Paragraph(
            "OPENAI CLAIMS: REJECTED BY THE CUMULATIVE REALITY TEST<br/>"
            "SFT EVIDENCE: FIRST-PRINCIPLES CONSTANTS, FORCES AND CROSS-DOMAIN LAW",
            verdict,
        ),
        Spacer(1, 12 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs",
            author,
        ),
        Spacer(1, 11 * mm),
        Paragraph(
            "Version 1.1.0 — 3 August 2026<br/>"
            f"Zenodo version DOI {ZENODO_DOI}<br/>"
            f"Supersedes v1.0.0 - DOI {PRIOR_ZENODO_DOI}<br/><br/>"
            "The paper records the unified constants and force-sector evidence, twelve "
            "engine-admitted disproofs, twelve distinct replacements, the whole-model "
            "ledger, independent replay, Lean 4 verification and zero open chains.",
            note,
        ),
    ]


def body_story(source: str):
    original_styles = base.styles

    def paper_styles():
        style_map = original_styles()
        for key in ("h1", "h2", "h3"):
            style_map[key].keepWithNext = 1
        style_map["body"].fontSize = 8.7
        style_map["body"].leading = 11.6
        style_map["code"].fontName = "SFTUnicodeMono"
        style_map["code"].fontSize = 6.5
        style_map["code"].leading = 8.3
        return style_map

    base.styles = paper_styles
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
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=16 * mm,
        title="OpenAI's Ten Mathematical Advances Fail the Reality Test",
        author="Maria Smith",
        subject="Twelve closed SFT disproofs and replacements grounded in cumulative first-principles and cross-domain evidence",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates([PageTemplate(id="counterpaper", frames=[frame], onPage=draw_page)])
    document.build(cover_story() + [PageBreak()] + body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    main()
