#!/usr/bin/env python3
"""Render the standalone Mathematics branch paper to archival PDF."""

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
SOURCE = ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md"
DOI_PATH = ROOT / "publications/current/mathematics/doi.txt"
OUTPUT = ROOT / "output/pdf/from-fold-to-mathematics-branch-paper-001.pdf"


def doi() -> str:
    return DOI_PATH.read_text(encoding="utf-8").strip() if DOI_PATH.is_file() else "DOI pending archival deposit"


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(base.RULE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(base.MUTED)
        canvas.drawString(
            20 * mm,
            height - 11.8 * mm,
            "FROM FOLD TO MATHEMATICS - ERNOS LABS MATHEMATICS BRANCH PAPER 001",
        )
        canvas.drawRightString(width - 20 * mm, 11 * mm, str(doc.page))
        canvas.drawString(
            20 * mm,
            11 * mm,
            f"Maria Smith - 2026 - CC BY 4.0 - {doi()}",
        )
    canvas.restoreState()


def cover():
    title = ParagraphStyle(
        "MathematicsCoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=33,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "MathematicsCoverSubtitle",
        fontName="Helvetica",
        fontSize=13.5,
        leading=19,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "MathematicsCoverKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "MathematicsCoverAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "MathematicsCoverNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=22 * mm,
        rightIndent=22 * mm,
    )
    return [
        Spacer(1, 24 * mm),
        Paragraph("SMITHIAN FOLD THEORY - MATHEMATICS BRANCH PAPER 001", kicker),
        Paragraph("From Fold to Mathematics", title),
        Spacer(1, 8 * mm),
        Paragraph(
            "An Exact, Parameter-Free and Machine-Closed Derivation of "
            "Mathematical Foundations from Smithian Fold Theory",
            subtitle,
        ),
        Spacer(1, 11 * mm),
        Table(
            [[""]],
            colWidths=[70 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)]),
        ),
        Spacer(1, 11 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 15 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs"
            "<br/>Maria.Smith.Sftoe@gmail.com",
            author,
        ),
        Spacer(1, 17 * mm),
        Paragraph(
            "Third clean-room reconstruction - Mathematics current-knowledge inventory complete"
            "<br/>Twelve admitted derivations - 7,424 generated candidate structures"
            "<br/>Version 1.0 - 23 July 2026"
            f"<br/>{doi()}"
            "<br/>Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
    ]


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
        title="From Fold to Mathematics",
        author="Maria Smith",
        subject="Completed Smithian Fold Theory Mathematics branch",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover() + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    main()
