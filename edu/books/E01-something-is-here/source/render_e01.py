#!/usr/bin/env python3
"""Render E01 student and adult editions from the checked-in sources."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE_JSON = BOOK_DIR / "source" / "book.json"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book.html"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.0.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.0.0.pdf"

FONT_ROOT = Path(
    "/Users/mettamazza/.cache/codex-runtimes/codex-primary-runtime/"
    "dependencies/native/libreoffice-headless/libreoffice/"
    "LibreOfficeDev.app/Contents/Resources/fonts/truetype"
)

PAGE = 210 * mm
NAVY = colors.HexColor("#18324A")
INK = colors.HexColor("#173042")
CREAM = colors.HexColor("#FFF9ED")
SKY = colors.HexColor("#DDF3F7")
BLUE = colors.HexColor("#2D7EA2")
ORANGE = colors.HexColor("#F28C45")
YELLOW = colors.HexColor("#F6C64E")
GREEN = colors.HexColor("#3A8D75")
CORAL = colors.HexColor("#E76F61")
PALE_GREEN = colors.HexColor("#E4F3EC")
WHITE = colors.white
GREY = colors.HexColor("#596A74")


def register_fonts() -> None:
    regular = FONT_ROOT / "DejaVuSans.ttf"
    bold = FONT_ROOT / "DejaVuSans-Bold.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("SFTSans", str(regular)))
        pdfmetrics.registerFont(TTFont("SFTSans-Bold", str(bold)))
    else:
        pdfmetrics.registerFontFamily(
            "SFTSans", normal="Helvetica", bold="Helvetica-Bold"
        )


def font(name: str) -> str:
    if name == "bold":
        return "SFTSans-Bold" if "SFTSans-Bold" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
    return "SFTSans" if "SFTSans" in pdfmetrics.getRegisteredFontNames() else "Helvetica"


def rounded_label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill: colors.Color) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, 10 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(WHITE if fill in (NAVY, BLUE, GREEN, CORAL) else INK)
    c.setFont(font("bold"), 8.5)
    c.drawCentredString(x + width / 2, y + 3.4 * mm, text)


def draw_mira(c: canvas.Canvas, x: float, y: float, scale: float = 1.0) -> None:
    c.setStrokeColor(NAVY)
    c.setLineWidth(2.2)
    c.setFillColor(colors.HexColor("#8FD2D8"))
    c.circle(x, y + 25 * scale, 14 * scale, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.circle(x - 4.5 * scale, y + 28 * scale, 1.4 * scale, fill=1, stroke=0)
    c.circle(x + 4.5 * scale, y + 28 * scale, 1.4 * scale, fill=1, stroke=0)
    c.arc(x - 5 * scale, y + 19 * scale, x + 5 * scale, y + 26 * scale, 200, 140)
    c.setFillColor(BLUE)
    c.roundRect(x - 14 * scale, y - 8 * scale, 28 * scale, 25 * scale, 7 * scale, fill=1, stroke=1)
    c.line(x - 8 * scale, y - 8 * scale, x - 10 * scale, y - 25 * scale)
    c.line(x + 8 * scale, y - 8 * scale, x + 10 * scale, y - 25 * scale)


def draw_pip(c: canvas.Canvas, x: float, y: float, scale: float = 1.0) -> None:
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.8)
    c.setFillColor(ORANGE)
    c.circle(x, y, 10 * scale, fill=1, stroke=1)
    c.setFillColor(YELLOW)
    c.wedge(x - 8 * scale, y - 8 * scale, x + 8 * scale, y + 8 * scale, 210, 120, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.circle(x + 3 * scale, y + 3 * scale, 1.2 * scale, fill=1, stroke=0)
    c.setFillColor(CORAL)
    p = c.beginPath()
    p.moveTo(x + 10 * scale, y + 1 * scale)
    p.lineTo(x + 17 * scale, y - 2 * scale)
    p.lineTo(x + 10 * scale, y - 5 * scale)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setStrokeColor(NAVY)
    c.line(x - 3 * scale, y - 10 * scale, x - 5 * scale, y - 16 * scale)
    c.line(x + 3 * scale, y - 10 * scale, x + 5 * scale, y - 16 * scale)


def draw_box(c: canvas.Canvas, x: float, y: float, scale: float = 1.0) -> None:
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.setFillColor(colors.HexColor("#79B9D1"))
    c.rect(x - 35 * scale, y - 24 * scale, 70 * scale, 48 * scale, fill=1, stroke=1)
    c.setFillColor(SKY)
    c.rect(x - 29 * scale, y - 18 * scale, 58 * scale, 36 * scale, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#A7D7E5"))
    p = c.beginPath()
    p.moveTo(x - 35 * scale, y + 24 * scale)
    p.lineTo(x - 20 * scale, y + 48 * scale)
    p.lineTo(x + 20 * scale, y + 48 * scale)
    p.lineTo(x + 35 * scale, y + 24 * scale)
    p.close()
    c.drawPath(p, fill=1, stroke=1)


def icon_card(c: canvas.Canvas, x: float, y: float, label: str, symbol: str, fill: colors.Color = WHITE) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.roundRect(x - 25 * mm, y - 18 * mm, 50 * mm, 36 * mm, 5 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(font("bold"), 28)
    c.drawCentredString(x, y + 1 * mm, symbol)
    c.setFont(font("bold"), 8)
    c.drawCentredString(x, y - 11 * mm, label.upper())


def draw_art(c: canvas.Canvas, art: str) -> None:
    cx = PAGE / 2
    if art == "cover":
        cy = 96 * mm
    elif art in ("question", "search"):
        cy = 102 * mm
    elif art == "paths_complete":
        cy = 125 * mm
    elif art in ("root", "end"):
        cy = 122 * mm
    else:
        cy = 115 * mm
    if art == "cover":
        c.setFillColor(YELLOW)
        c.circle(cx + 50 * mm, cy + 35 * mm, 17 * mm, fill=1, stroke=0)
        draw_box(c, cx, cy - 4 * mm, 1.25)
        draw_mira(c, cx - 58 * mm, cy - 1 * mm, 1.5)
        draw_pip(c, cx + 55 * mm, cy + 2 * mm, 1.5)
        c.setStrokeColor(CORAL)
        c.setLineWidth(5)
        c.arc(cx - 12 * mm, cy + 30 * mm, cx + 35 * mm, cy + 78 * mm, 15, 230)
        c.setFillColor(CORAL)
        c.circle(cx + 10 * mm, cy + 26 * mm, 3 * mm, fill=1, stroke=0)
    elif art == "imprint":
        icon_card(c, cx - 35 * mm, cy, "open book", "<> ", SKY)
        c.setFillColor(PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.setLineWidth(3)
        c.circle(cx + 42 * mm, cy, 25 * mm, fill=1, stroke=1)
        c.setFillColor(GREEN)
        c.setFont(font("bold"), 18)
        c.drawCentredString(cx + 42 * mm, cy + 3 * mm, "1.0.0")
        c.setFont(font("bold"), 8)
        c.drawCentredString(cx + 42 * mm, cy - 8 * mm, "LIVE-WORK VERSION")
    elif art in ("question", "search"):
        draw_mira(c, cx - 35 * mm, cy - 6 * mm, 1.6)
        draw_pip(c, cx + 45 * mm, cy + 2 * mm, 1.5)
        c.setFillColor(CORAL)
        c.setFont(font("bold"), 86 if art == "question" else 58)
        c.drawCentredString(cx + 5 * mm, cy + 30 * mm, "?")
        if art == "search":
            c.setStrokeColor(BLUE)
            c.setLineWidth(8)
            c.circle(cx + 3 * mm, cy + 18 * mm, 30 * mm, fill=0, stroke=1)
            c.line(cx + 25 * mm, cy - 4 * mm, cx + 50 * mm, cy - 30 * mm)
    elif art in ("empty_box", "box_present"):
        draw_box(c, cx, cy - 8 * mm, 1.35)
        draw_mira(c, cx - 63 * mm, cy - 6 * mm, 1.35)
        draw_pip(c, cx + 59 * mm, cy - 5 * mm, 1.25)
        if art == "box_present":
            for i, (sym, label) in enumerate((("EYE", "looking"), ("?", "question"), ("|", "record"))):
                x = cx - 45 * mm + i * 45 * mm
                c.setFillColor(WHITE)
                c.setStrokeColor(GREEN)
                c.circle(x, cy + 50 * mm, 12 * mm, fill=1, stroke=1)
                c.setFillColor(GREEN)
                c.setFont(font("bold"), 8 if sym == "EYE" else 18)
                c.drawCentredString(x, cy + 48 * mm, sym)
                c.setFont(font("bold"), 7)
                c.drawCentredString(x, cy + 33 * mm, label.upper())
    elif art in ("listen", "quiet_record", "activity_listen"):
        draw_mira(c, cx - 35 * mm, cy - 5 * mm, 1.45)
        draw_pip(c, cx + 40 * mm, cy - 4 * mm, 1.35)
        c.setStrokeColor(GREY)
        c.setLineWidth(5)
        c.arc(cx - 5 * mm, cy + 18 * mm, cx + 33 * mm, cy + 58 * mm, 80, 200)
        c.arc(cx + 3 * mm, cy + 25 * mm, cx + 25 * mm, cy + 51 * mm, 80, 200)
        c.setFillColor(PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.roundRect(cx - 6 * mm, cy - 34 * mm, 52 * mm, 22 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(GREEN)
        c.setFont(font("bold"), 10)
        c.drawCentredString(cx + 20 * mm, cy - 25 * mm, "LISTENING RECORD")
        if art == "activity_listen":
            c.setFillColor(YELLOW)
            c.circle(cx + 67 * mm, cy + 32 * mm, 14 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(font("bold"), 11)
            c.drawCentredString(cx + 67 * mm, cy + 30 * mm, "SHORT")
    elif art in ("word", "word_record"):
        c.setFillColor(WHITE)
        c.setStrokeColor(NAVY)
        c.setLineWidth(2.5)
        c.roundRect(cx - 63 * mm, cy - 34 * mm, 126 * mm, 68 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(font("bold"), 34)
        c.drawCentredString(cx, cy - 2 * mm, "NOTHING")
        c.setStrokeColor(ORANGE)
        c.setLineWidth(7)
        c.line(cx + 50 * mm, cy - 44 * mm, cx + 75 * mm, cy - 20 * mm)
        if art == "word_record":
            c.setStrokeColor(GREEN)
            c.setLineWidth(3)
            for x in (cx - 52 * mm, cx, cx + 52 * mm):
                c.circle(x, cy, 16 * mm, fill=0, stroke=1)
    elif art == "pip_asks":
        draw_pip(c, cx - 45 * mm, cy - 5 * mm, 1.7)
        draw_mira(c, cx + 48 * mm, cy - 10 * mm, 1.5)
        c.setFillColor(WHITE)
        c.setStrokeColor(NAVY)
        c.roundRect(cx - 30 * mm, cy + 23 * mm, 70 * mm, 35 * mm, 8 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(font("bold"), 26)
        c.drawCentredString(cx + 5 * mm, cy + 34 * mm, "?")
    elif art == "no_example":
        labels = ("POINT", "SAY", "RECORD", "CHECK")
        for i, label in enumerate(labels):
            x = cx - 60 * mm + (i % 2) * 80 * mm
            y = cy + 33 * mm - (i // 2) * 58 * mm
            c.setStrokeColor(GREY)
            c.setDash(5, 4)
            c.roundRect(x, y - 18 * mm, 55 * mm, 36 * mm, 5 * mm, fill=0, stroke=1)
            c.setDash()
            c.setFillColor(GREY)
            c.setFont(font("bold"), 9)
            c.drawCentredString(x + 27.5 * mm, y - 28 * mm, label)
    elif art in ("two_paths", "paths_complete"):
        c.setStrokeColor(NAVY)
        c.setLineWidth(5)
        c.line(cx, cy + 55 * mm, cx, cy + 28 * mm)
        c.line(cx, cy + 28 * mm, cx - 48 * mm, cy - 8 * mm)
        c.line(cx, cy + 28 * mm, cx + 48 * mm, cy - 8 * mm)
        c.setFillColor(GREEN)
        c.circle(cx - 48 * mm, cy - 15 * mm, 18 * mm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont(font("bold"), 11)
        c.drawCentredString(cx - 48 * mm, cy - 18 * mm, "PRESENTED")
        c.setFillColor(WHITE)
        c.setStrokeColor(CORAL)
        c.setDash(5, 3)
        c.circle(cx + 48 * mm, cy - 15 * mm, 18 * mm, fill=1, stroke=1)
        c.setDash()
        c.setFillColor(CORAL)
        c.setFont(font("bold"), 9)
        c.drawCentredString(cx + 48 * mm, cy - 18 * mm, "NOT PRESENTED")
        if art == "paths_complete":
            c.setStrokeColor(BLUE)
            c.setLineWidth(4)
            c.arc(cx - 79 * mm, cy - 45 * mm, cx + 79 * mm, cy + 12 * mm, 190, 160)
            c.setFillColor(BLUE)
            c.setFont(font("bold"), 11)
            c.drawCentredString(cx, cy - 34 * mm, "COMPLETE DECLARED PATHS")
    elif art in ("presented_path", "result"):
        icon_card(c, cx, cy, "presented occurrence", "!", PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.setLineWidth(5)
        c.circle(cx, cy, 34 * mm, fill=0, stroke=1)
        if art == "result":
            labels = ((-60, 35, "SHOW"), (60, 35, "SAY"), (-60, -35, "RECORD"), (60, -35, "CHECK"))
            for dx, dy, label in labels:
                c.setFillColor(YELLOW)
                c.circle(cx + dx * mm / 1.6, cy + dy * mm / 1.6, 10 * mm, fill=1, stroke=0)
                c.setFillColor(NAVY)
                c.setFont(font("bold"), 7)
                c.drawCentredString(cx + dx * mm / 1.6, cy + dy * mm / 1.6 - 2 * mm, label)
    elif art == "unpresented_path":
        c.setStrokeColor(CORAL)
        c.setLineWidth(3)
        c.setDash(8, 5)
        c.roundRect(cx - 55 * mm, cy - 34 * mm, 110 * mm, 68 * mm, 10 * mm, fill=0, stroke=1)
        c.setDash()
        c.setFillColor(CORAL)
        c.setFont(font("bold"), 13)
        c.drawCentredString(cx, cy + 43 * mm, "NO PRESENTED EXAMPLE")
    elif art == "root":
        c.setStrokeColor(GREEN)
        c.setLineWidth(7)
        c.line(cx, cy - 45 * mm, cx, cy + 25 * mm)
        for dx in (-55, -30, 30, 55):
            c.line(cx, cy + 15 * mm, cx + dx * mm, cy + 48 * mm)
        for dx in (-45, -20, 20, 45):
            c.line(cx, cy - 25 * mm, cx + dx * mm, cy - 55 * mm)
        c.setFillColor(YELLOW)
        c.circle(cx, cy + 18 * mm, 13 * mm, fill=1, stroke=0)
    elif art == "boundary":
        c.setFillColor(PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.setLineWidth(4)
        c.circle(cx - 18 * mm, cy, 48 * mm, fill=1, stroke=1)
        for i, label in enumerate(("SHOW", "SAY", "RECORD", "CHECK")):
            angle_positions = ((-18, 17), (18, 17), (-18, -17), (18, -17))
            dx, dy = angle_positions[i]
            c.setFillColor(WHITE)
            c.circle(cx - 18 * mm + dx * mm, cy + dy * mm, 9 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(font("bold"), 6.5)
            c.drawCentredString(cx - 18 * mm + dx * mm, cy + dy * mm - 2 * mm, label)
        c.setStrokeColor(GREY)
        c.setDash(6, 4)
        c.line(cx + 38 * mm, cy - 55 * mm, cx + 38 * mm, cy + 55 * mm)
        c.setDash()
        c.setFillColor(GREY)
        c.setFont(font("bold"), 8)
        c.drawCentredString(cx + 63 * mm, cy - 2 * mm, "NO CLAIM ADDED")
    elif art == "activity_bowl":
        c.setFillColor(YELLOW)
        c.setStrokeColor(NAVY)
        c.setLineWidth(3)
        c.wedge(cx - 43 * mm, cy - 20 * mm, cx + 43 * mm, cy + 30 * mm, 180, 180, fill=1, stroke=1)
        c.line(cx - 60 * mm, cy - 22 * mm, cx + 60 * mm, cy - 22 * mm)
        for i, label in enumerate(("PRESENT", "NOT INSIDE", "OBSERVED")):
            c.setFillColor(WHITE)
            c.roundRect(cx - 70 * mm + i * 48 * mm, cy + 45 * mm, 43 * mm, 17 * mm, 3 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(font("bold"), 7)
            c.drawCentredString(cx - 48.5 * mm + i * 48 * mm, cy + 51 * mm, label)
    elif art == "activity_draw":
        icon_card(c, cx - 38 * mm, cy, "first record", "1", SKY)
        icon_card(c, cx + 38 * mm, cy, "second check", "2", PALE_GREEN)
        c.setFillColor(CORAL)
        c.setFont(font("bold"), 24)
        c.drawCentredString(cx, cy + 33 * mm, "=  or  !=")
    elif art == "keep_record":
        c.setFillColor(colors.HexColor("#A8D5C3"))
        c.setStrokeColor(NAVY)
        c.setLineWidth(3)
        c.roundRect(cx - 68 * mm, cy - 37 * mm, 136 * mm, 74 * mm, 7 * mm, fill=1, stroke=1)
        icon_card(c, cx - 35 * mm, cy, "record A", "A", WHITE)
        icon_card(c, cx + 35 * mm, cy, "record B", "B", WHITE)
    elif art == "end":
        draw_mira(c, cx - 58 * mm, cy - 8 * mm, 1.25)
        draw_pip(c, cx + 60 * mm, cy - 2 * mm, 1.2)
        for i, (label, fill) in enumerate((("QUESTION", YELLOW), ("CHECK", SKY), ("RECORD", PALE_GREEN))):
            x = cx - 42 * mm + i * 42 * mm
            c.setFillColor(fill)
            c.setStrokeColor(NAVY)
            c.roundRect(x, cy + 20 * mm, 34 * mm, 27 * mm, 4 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(font("bold"), 7)
            c.drawCentredString(x + 17 * mm, cy + 31 * mm, label)
        draw_box(c, cx, cy - 30 * mm, 0.65)


def paragraph_in_box(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    max_size: float,
    min_size: float,
    color: colors.Color,
    bold: bool = True,
    align: int = TA_CENTER,
) -> None:
    safe = html.escape(text).replace("\n", "<br/>")
    chosen = min_size
    para = None
    for size in range(int(max_size), int(min_size) - 1, -1):
        style = ParagraphStyle(
            "fit",
            fontName=font("bold" if bold else "regular"),
            fontSize=size,
            leading=size * 1.22,
            textColor=color,
            alignment=align,
            spaceAfter=0,
        )
        candidate = Paragraph(safe, style)
        _, h = candidate.wrap(width, height)
        if h <= height:
            para = candidate
            chosen = size
            break
    if para is None:
        style = ParagraphStyle(
            "fit-min",
            fontName=font("bold" if bold else "regular"),
            fontSize=chosen,
            leading=chosen * 1.2,
            textColor=color,
            alignment=align,
        )
        para = Paragraph(safe, style)
    _, actual_h = para.wrap(width, height)
    para.drawOn(c, x, y + (height - actual_h) / 2)


def page_background(c: canvas.Canvas, kind: str) -> None:
    palette = {
        "cover": NAVY,
        "legal": CREAM,
        "story": CREAM,
        "derivation": SKY,
        "result": PALE_GREEN,
        "boundary": colors.HexColor("#F2EFE8"),
        "activity": colors.HexColor("#FFF2D6"),
        "check": colors.HexColor("#EAE7F4"),
        "end": NAVY,
    }
    c.setFillColor(palette.get(kind, CREAM))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(ORANGE if kind in ("cover", "end") else BLUE)
    c.circle(15 * mm, PAGE - 15 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(YELLOW)
    c.circle(PAGE - 15 * mm, 15 * mm, 4 * mm, fill=1, stroke=0)


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(book["title"])
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years operational foundation picture and activity book")
    c.setKeywords("Smithian Fold Theory, early years, presence, absence, checking")
    for page in book["pages"]:
        kind = page["kind"]
        page_background(c, kind)
        badge_fill = ORANGE if kind in ("cover", "end") else (GREEN if kind in ("derivation", "result") else BLUE)
        rounded_label(c, page["badge"], 20 * mm, PAGE - 22 * mm, PAGE - 40 * mm, badge_fill)

        if kind == "cover":
            paragraph_in_box(c, page["text"], 18 * mm, PAGE - 78 * mm, PAGE - 36 * mm, 40 * mm, 40, 28, WHITE)
            draw_art(c, page["art"])
            paragraph_in_box(c, page["subtext"], 30 * mm, 22 * mm, PAGE - 60 * mm, 22 * mm, 16, 12, WHITE, bold=False)
        elif kind == "legal":
            draw_art(c, page["art"])
            paragraph_in_box(c, page["text"], 28 * mm, 24 * mm, PAGE - 56 * mm, 68 * mm, 12, 9, INK, bold=False)
            paragraph_in_box(c, page["subtext"], 30 * mm, 10 * mm, PAGE - 60 * mm, 12 * mm, 10, 8, GREY, bold=False)
        else:
            draw_art(c, page["art"])
            main_color = WHITE if kind == "end" else INK
            paragraph_in_box(c, page["text"], 18 * mm, 25 * mm, PAGE - 36 * mm, 48 * mm, 24, 17, main_color)
            paragraph_in_box(c, page["subtext"], 26 * mm, 10 * mm, PAGE - 52 * mm, 15 * mm, 10, 8, WHITE if kind == "end" else GREY, bold=False)

        if page["page"] > 2:
            c.setFillColor(WHITE if kind in ("cover", "end") else GREY)
            c.setFont(font("regular"), 8)
            c.drawRightString(PAGE - 9 * mm, 7 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 13, 17, 20):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def generate_accessible_html(book: dict) -> None:
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(book['title'])} - accessible edition</title>",
        "<style>",
        ":root{color-scheme:light;--ink:#173042;--navy:#18324a;--sky:#ddf3f7;--cream:#fff9ed;--orange:#c95f17;}",
        "body{margin:0;font-family:system-ui,-apple-system,sans-serif;color:var(--ink);background:#f4f6f7;line-height:1.6;}",
        "header,main,footer{max-width:52rem;margin:auto;padding:1.5rem;}",
        "header{background:var(--navy);color:white;}h1{font-size:clamp(2.2rem,7vw,4rem);line-height:1.05;margin:.3rem 0;}",
        ".page{background:white;margin:1.5rem 0;padding:1.5rem;border-radius:1rem;border:.15rem solid #aac2cc;}",
        ".badge{display:inline-block;font-weight:800;letter-spacing:.04em;background:var(--sky);padding:.35rem .7rem;border-radius:2rem;}",
        ".story{font-size:clamp(1.45rem,4vw,2.2rem);font-weight:750;line-height:1.25;white-space:pre-line;}",
        ".subtext{font-size:1.15rem;}.art{border-left:.35rem solid var(--orange);padding:.6rem 1rem;background:var(--cream);}",
        "a:focus{outline:.25rem solid #000;outline-offset:.2rem;}@media print{.page{break-after:page;box-shadow:none;}}",
        "</style></head><body>",
        "<header>",
        f"<p>{html.escape(book['stage'])} - Book E01 - Version {html.escape(book['version'])}</p>",
        f"<h1>{html.escape(book['title'])}</h1>",
        f"<p>{html.escape(book['subtitle'])}</p>",
        f"<p>Written by {html.escape(book['author'])}. This semantic edition includes an illustration description for every page.</p>",
        "</header><main>",
    ]
    for page in book["pages"]:
        parts.extend(
            [
                f'<section class="page" aria-labelledby="page-{page["page"]}">',
                f'<p class="badge">{html.escape(page["badge"])}</p>',
                f'<h2 id="page-{page["page"]}">Page {page["page"]}</h2>',
                f'<p class="story">{html.escape(page["text"])}</p>',
                f'<p class="subtext">{html.escape(page["subtext"])}</p>',
                f'<figure class="art" role="img" aria-label="{html.escape(page["alt"], quote=True)}"><figcaption><strong>Illustration description:</strong> {html.escape(page["alt"])}</figcaption></figure>',
                "</section>",
            ]
        )
    parts.extend(
        [
            "</main><footer>",
            "<p>Scientific source: SFT-ROOT-THERE-IS-NO-NOTHING. The rule is limited to the operational boundary of what can be presented, stated, recorded or checked.</p>",
            "<p>Copyright 2026 Maria Smith. Licensed CC BY 4.0.</p>",
            "</footer></body></html>",
        ]
    )
    ACCESSIBLE_HTML.write_text("\n".join(parts), encoding="utf-8")


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", escaped)
    return escaped


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide - Version 1.0.0 live edition")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def parse_markdown_to_story(markdown_text: str) -> list:
    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "SFTBody",
        parent=styles["BodyText"],
        fontName=font("regular"),
        fontSize=10.1,
        leading=14,
        textColor=INK,
        spaceAfter=5,
    )
    h1 = ParagraphStyle(
        "SFTH1",
        parent=styles["Heading1"],
        fontName=font("bold"),
        fontSize=25,
        leading=29,
        textColor=NAVY,
        spaceAfter=14,
    )
    h2 = ParagraphStyle(
        "SFTH2",
        parent=styles["Heading2"],
        fontName=font("bold"),
        fontSize=16,
        leading=20,
        textColor=BLUE,
        spaceBefore=10,
        spaceAfter=7,
    )
    h3 = ParagraphStyle(
        "SFTH3",
        parent=styles["Heading3"],
        fontName=font("bold"),
        fontSize=12,
        leading=15,
        textColor=GREEN,
        spaceBefore=7,
        spaceAfter=4,
    )
    quote = ParagraphStyle(
        "SFTQuote",
        parent=body,
        leftIndent=10 * mm,
        rightIndent=6 * mm,
        borderColor=ORANGE,
        borderWidth=2,
        borderPadding=7,
        backColor=CREAM,
    )
    story = []
    paragraph_lines: list[str] = []
    list_items: list[str] = []
    list_kind = "bullet"

    def flush_paragraph() -> None:
        if paragraph_lines:
            story.append(Paragraph(inline_markup(" ".join(paragraph_lines)), body))
            paragraph_lines.clear()

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            list_style = ParagraphStyle(
                "SFTList",
                parent=body,
                leftIndent=8 * mm,
                firstLineIndent=-5 * mm,
                spaceAfter=3,
            )
            for index, item in enumerate(list_items, start=1):
                prefix = f"{index}." if list_kind == "number" else "&#8226;"
                story.append(
                    Paragraph(
                        f"<b>{prefix}</b>&nbsp;&nbsp;{inline_markup(item)}",
                        list_style,
                    )
                )
            story.append(Spacer(1, 3))
            list_items = []

    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if not line:
            flush_paragraph()
            flush_list()
            continue
        if line.startswith("# "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline_markup(line[2:]), h1))
        elif line.startswith("## "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline_markup(line[3:]), h2))
        elif line.startswith("### "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline_markup(line[4:]), h3))
        elif line.startswith("> "):
            flush_paragraph(); flush_list()
            story.append(Paragraph(inline_markup(line[2:]), quote))
        elif line.startswith("- "):
            flush_paragraph()
            if list_items and list_kind != "bullet":
                flush_list()
            list_kind = "bullet"
            list_items.append(line[2:])
        elif re.match(r"^\d+\. ", line):
            flush_paragraph()
            if list_items and list_kind != "number":
                flush_list()
            list_kind = "number"
            list_items.append(re.sub(r"^\d+\. ", "", line))
        elif list_items and raw[:1].isspace():
            # Markdown wraps long list items onto indented continuation lines.
            # Keep those lines inside the current item so ordered lists retain
            # their sequence instead of restarting at 1 after every wrap.
            list_items[-1] = f"{list_items[-1]} {line.strip()}"
        else:
            flush_list()
            paragraph_lines.append(line)
    flush_paragraph(); flush_list()
    return story


def render_adult_guide() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=19 * mm,
        bottomMargin=20 * mm,
        title="Adult Guide - E01 Something Is Here",
        author="Maria Smith",
        subject="Adult guidance for SFT Early Years Book E01",
    )
    story = parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    doc.build(story, onFirstPage=adult_footer, onLaterPages=adult_footer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-only", action="store_true")
    parser.add_argument("--adult-only", action="store_true")
    args = parser.parse_args()
    register_fonts()
    book = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    if len(book["pages"]) != 24:
        raise ValueError("E01 must contain exactly 24 canonical pages")
    page_numbers = [page["page"] for page in book["pages"]]
    if page_numbers != list(range(1, 25)):
        raise ValueError("E01 page numbers must be continuous from 1 through 24")
    if not args.adult_only:
        render_student(book)
        generate_accessible_html(book)
    if not args.student_only:
        render_adult_guide()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
