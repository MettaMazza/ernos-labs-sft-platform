#!/usr/bin/env python3
"""Render the unpublished complete-field Classical Computation v1.4 paper."""

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
SOURCE = ROOT / "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"
OUTPUT = ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf"


def doi() -> str:
    return "Version 1.4 DOI pending archival deposit"


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
            "AFTER TURING: THE FOLD MACHINE - ERNOS LABS COMPUTATION PAPER 001",
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
        "ComputationV14CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=28,
        leading=33,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "ComputationV14CoverSubtitle",
        fontName="Helvetica",
        fontSize=13.5,
        leading=19,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "ComputationV14CoverKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "ComputationV14CoverAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "ComputationV14CoverNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=20 * mm,
        rightIndent=20 * mm,
    )
    warning = ParagraphStyle(
        "ComputationV14CoverWarning",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    return [
        Spacer(1, 22 * mm),
        Paragraph("SMITHIAN FOLD THEORY - CLASSICAL COMPUTATION BRANCH PAPER 001", kicker),
        Paragraph("After Turing: The Fold Machine", title),
        Spacer(1, 8 * mm),
        Paragraph(
            "An Exact, Parameter-Free and Machine-Closed Complete-Field Derivation "
            "of Classical Computational Science from Smithian Fold Theory",
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
        Spacer(1, 14 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs"
            "<br/>Maria.Smith.Sftoe@gmail.com",
            author,
        ),
        Spacer(1, 15 * mm),
        Paragraph(
            "Third clean-room reconstruction - complete-field Classical Computation"
            "<br/>369 of 369 frozen obligations - 12 complete families"
            "<br/>94,464 generated candidates - 369 unique survivors - 1,476 controls"
            "<br/>Dated completion - open to lawful extension"
            "<br/>Version 1.4 - 29 July 2026"
            f"<br/>{doi()}"
            "<br/>Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 7 * mm),
        Paragraph("FINAL PUBLICATION CANDIDATE - RELEASE NOT YET AUTHORISED", warning),
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
        title="After Turing: The Fold Machine",
        author="Maria Smith",
        subject="Complete-field Smithian Fold Theory Classical Computation branch, version 1.4",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover() + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT}")


if __name__ == "__main__":
    main()
