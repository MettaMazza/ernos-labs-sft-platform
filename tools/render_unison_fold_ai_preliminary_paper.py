#!/usr/bin/env python3
"""Render the Unison Fold AI preliminary computational-proof paper."""

from pathlib import Path
import re
import sys

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


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import render_platform_paper as base  # noqa: E402


SOURCE = ROOT / (
    "applications/frontier/v3_computational_proofs/Unison Fold AI/paper/"
    "UNISON_FOLD_AI_SFT_V3_COMPUTATIONAL_PROOF_PRELIMINARY.md"
)
OUTPUT = ROOT / (
    "output/pdf/"
    "sft-v3-unison-fold-ai-computational-proof-preliminary-v0.1.0-rc1.pdf"
)
VERSION = "0.1.0-rc1"


def publication_source(source: str) -> str:
    """Join wrapped list continuations so the shared renderer retains them."""

    lines = source.splitlines()
    joined: list[str] = []
    index = 0
    in_code = False
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith("```"):
            in_code = not in_code
            joined.append(line)
            index += 1
            continue
        if not in_code and re.match(r"^(?:[-*]|\d+\.)\s+", line.strip()):
            item = line.strip()
            index += 1
            while index < len(lines):
                continuation = lines[index]
                stripped = continuation.strip()
                if (
                    not stripped
                    or stripped.startswith(("#", "|", ">", "```"))
                    or re.match(r"^(?:[-*]|\d+\.)\s+", stripped)
                ):
                    break
                item += " " + stripped
                index += 1
            joined.append(item)
            continue
        joined.append(line)
        index += 1
    return "\n".join(joined)


def cover():
    title = ParagraphStyle(
        "UnisonCoverTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=31,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "UnisonCoverSubtitle",
        fontName="Helvetica",
        fontSize=12.5,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "UnisonCoverKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "UnisonCoverAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "UnisonCoverNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=18 * mm,
        rightIndent=18 * mm,
    )
    status = ParagraphStyle(
        "UnisonCoverStatus",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    return [
        Spacer(1, 14 * mm),
        Paragraph("SMITHIAN FOLD THEORY - COMPUTATIONAL PROOF PAPER 002", kicker),
        Paragraph("From Attention to an Exact Conversational Architecture", title),
        Spacer(1, 7 * mm),
        Paragraph(
            "Unison Fold AI: a V3-native translation of a GPT-2-class causal conversational transformer",
            subtitle,
        ),
        Spacer(1, 7 * mm),
        Paragraph(
            "Architecture proof, clean-room implementation, zero-copy teacher distillation and an open conversational gate",
            subtitle,
        ),
        Spacer(1, 9 * mm),
        Table(
            [[""]],
            colWidths=[70 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)]),
        ),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 12 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com",
            author,
        ),
        Spacer(1, 11 * mm),
        Paragraph(
            "Version 0.1.0-rc1 - published open-access preliminary version<br/>"
            "31 July 2026<br/>DOI: 10.5281/zenodo.21726397<br/>"
            "Paper and documentation: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "OPEN-ACCESS PRELIMINARY VERSION - RESULTS IN PROGRESS",
            status,
        ),
    ]


def main() -> None:
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
            canvas.drawString(
                18 * mm,
                height - 11.8 * mm,
                "SFT V3 UNISON FOLD AI - PRELIMINARY V0.1.0-RC1",
            )
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            canvas.drawString(
                18 * mm,
                11 * mm,
                "Maria Smith - 2026 - CC BY 4.0 - DOI 10.5281/zenodo.21726397",
            )
        canvas.restoreState()

    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=21 * mm,
        bottomMargin=18 * mm,
        title="From Attention to an Exact Conversational Architecture",
        author="Maria Smith",
        subject="Preliminary Unison Fold AI SFT V3 computational-proof paper",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates(
        [PageTemplate(id="paper", frames=[frame], onPage=draw_page)]
    )
    source = publication_source(SOURCE.read_text(encoding="utf-8"))
    document.build(cover() + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
