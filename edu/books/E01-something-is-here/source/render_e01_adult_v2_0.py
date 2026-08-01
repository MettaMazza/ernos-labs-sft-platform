#!/usr/bin/env python3
"""Render the E01 2.0.0 adult guide from its versioned Markdown source."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "adult-guide-v2.0.0.md"
OUTPUT = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "2.0.0" / "SFT-E01-Adult-Guide-v2.0.0.pdf"
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


def footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8DDE6"))
    canvas.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(18 * mm, 9 * mm, "E01 Something Is Here · Adult Guide · review 2.0.0")
    canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, str(doc.page))
    canvas.restoreState()


def build_story() -> list:
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=29, leading=34, textColor=NAVY, alignment=TA_CENTER, spaceAfter=10 * mm)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=TEAL, spaceBefore=6 * mm, spaceAfter=3 * mm, keepWithNext=True)
    h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=GOLD, spaceBefore=4 * mm, spaceAfter=2 * mm, keepWithNext=True)
    body = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.3, leading=15, textColor=INK, spaceAfter=3.2 * mm)
    bullet = ParagraphStyle("Bullet", parent=body, leftIndent=7 * mm, firstLineIndent=-4 * mm)
    quote = ParagraphStyle("Quote", parent=body, leftIndent=8 * mm, rightIndent=8 * mm, borderColor=GOLD, borderWidth=1, borderPadding=5 * mm, backColor=colors.HexColor("#FFF8E5"))
    story: list = []
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(paragraph)), body))
            paragraph.clear()

    for raw in SOURCE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        if line.startswith("# "):
            flush(); story.append(Paragraph(inline_markup(line[2:]), title))
        elif line.startswith("## "):
            flush(); story.append(Paragraph(inline_markup(line[3:]), h2))
        elif line.startswith("### "):
            flush(); story.append(Paragraph(inline_markup(line[4:]), h3))
        elif line.startswith("> "):
            flush(); story.append(Paragraph(inline_markup(line[2:]), quote))
        elif re.match(r"^[-*] ", line):
            flush(); story.append(Paragraph("• " + inline_markup(line[2:]), bullet))
        elif re.match(r"^\d+\. ", line):
            flush(); number, content = line.split(". ", 1); story.append(Paragraph(f"{number}. " + inline_markup(content), bullet))
        elif line.endswith("  "):
            paragraph.append(line[:-2] + "<br/>")
        else:
            paragraph.append(line)
    flush()
    return story


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=19 * mm, title="Adult Guide — E01 Something Is Here", author="Maria Smith", subject="SFT Open Education review guide")
    doc.build(build_story(), onFirstPage=footer, onLaterPages=footer)
    print(OUTPUT)


if __name__ == "__main__":
    main()
