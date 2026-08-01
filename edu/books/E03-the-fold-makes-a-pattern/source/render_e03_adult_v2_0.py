#!/usr/bin/env python3
"""Render the E03 2.0.0 adult guide from versioned Markdown."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "adult-guide-v2.0.0.md"
OUTPUT = ROOT / "output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/2.0.0/SFT-E03-Adult-Guide-v2.0.0.pdf"
NAVY = colors.HexColor("#101A33")
TEAL = colors.HexColor("#248C83")
GOLD = colors.HexColor("#D39B18")
INK = colors.HexColor("#26354B")


def inline_markup(text: str) -> str:
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def footer(pdf_canvas, doc) -> None:
    pdf_canvas.saveState()
    pdf_canvas.setStrokeColor(colors.HexColor("#D8DDE6"))
    pdf_canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    pdf_canvas.setFont("Helvetica", 8)
    pdf_canvas.setFillColor(colors.HexColor("#64748B"))
    pdf_canvas.drawString(18 * mm, 9 * mm, "E03 The Fold Makes a Pattern · Adult Guide · review 2.0.0")
    pdf_canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, str(doc.page))
    pdf_canvas.restoreState()


def build_story() -> list:
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8 * mm)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=TEAL, spaceBefore=4.5 * mm, spaceAfter=2.3 * mm, keepWithNext=True)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=12.4, leading=15, textColor=GOLD, spaceBefore=3.2 * mm, spaceAfter=1.5 * mm, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.2, textColor=INK, spaceAfter=2.4 * mm)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=7 * mm, firstLineIndent=-4 * mm)
    story: list = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), body))
            paragraph.clear()

    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line == "<!-- PAGE BREAK -->":
            flush(); story.append(PageBreak())
        elif not line:
            flush()
        elif line.startswith("# "):
            flush(); story.append(Paragraph(inline_markup(line[2:]), title))
        elif line.startswith("## "):
            flush(); story.append(Paragraph(inline_markup(line[3:]), h2))
        elif line.startswith("### "):
            flush(); story.append(Paragraph(inline_markup(line[4:]), h3))
        elif re.match(r"^[-*] ", line):
            flush(); story.append(Paragraph("• " + inline_markup(line[2:]), bullet))
        elif re.match(r"^\d+\. ", line):
            flush(); number, content = line.split(". ", 1); story.append(Paragraph(f"{number}. " + inline_markup(content), bullet))
        else:
            paragraph.append(line)
    flush()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=17 * mm, bottomMargin=19 * mm,
                            title="Adult Guide — E03 The Fold Makes a Pattern", author="Maria Smith",
                            subject="SFT Open Education review guide")
    doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
