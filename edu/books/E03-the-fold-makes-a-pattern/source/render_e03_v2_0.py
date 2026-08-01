#!/usr/bin/env python3
"""Render E03 2.0.0 as a paper-native illustrated picture book."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source/book-v2.0.0.json"
GAME = ROOT / "edu/games/companion-adventures"
EMOJI_DIR = ROOT / "edu/assets/openmoji/16.0.0/color/png-512"
RELEASE_DIR = ROOT / "output/pdf/edu/SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN/2.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E03-The-Fold-Makes-A-Pattern-v2.0.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible/student-book-v2.0.0.html"

PAGE = 210 * mm
NAVY = colors.HexColor("#101A33")
INK = colors.HexColor("#1E2B42")
CREAM = colors.HexColor("#FFF7E7")
GOLD = colors.HexColor("#FFD45A")
TEAL = colors.HexColor("#54C9C5")
PURPLE = colors.HexColor("#76519B")
CORAL = colors.HexColor("#F06450")
WHITE = colors.white

SCENES = {
    "balcony": BOOK_DIR.parent / "E02-one-whole-many-parts/art/v2.0.0/story/e02-balcony-ending-v2.0.0.png",
    "gate": GAME / "public/art/stages/e03-source/e03-stage-02-turn-gate-v1.png",
    "bridge": GAME / "public/art/stages/e03-source/e03-stage-03-over-under-bridge-v1.png",
    "arch": GAME / "public/art/stages/e03-source/e03-stage-04-sunrise-arch-v1.png",
}

SPRITES = {
    "Mia": GAME / "public/art/characters/individual/mira-v1.png",
    "Sol": GAME / "public/art/characters/individual/sol.png",
    "Tavi": GAME / "public/art/characters/individual/tavi.png",
    "Vee": GAME / "public/art/characters/individual/vee.png",
}

EMOJI = {
    "moon": EMOJI_DIR / "1F319.png",
    "sun": EMOJI_DIR / "2600.png",
    "star": EMOJI_DIR / "2B50.png",
    "leaf": EMOJI_DIR / "1F343.png",
    "blank": EMOJI_DIR / "2B1C.png",
    "lantern": EMOJI_DIR / "1F3EE.png",
}

IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def register_fonts() -> tuple[str, str]:
    regular = GAME / "node_modules/@vercel/og/dist/noto-sans-v27-latin-regular.ttf"
    if regular.exists():
        pdfmetrics.registerFont(TTFont("SFTNoto", str(regular)))
        return "SFTNoto", "Helvetica-Bold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = register_fonts()


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32 or [p["page"] for p in book["pages"]] != list(range(1, 33)):
        raise ValueError("E03 2.0.0 must contain exactly 32 contiguous pages")
    return book


def draw_crop(c: canvas.Canvas, path: Path) -> None:
    reader = image(path)
    iw, ih = reader.getSize()
    scale = max(PAGE / iw, PAGE / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(reader, (PAGE - dw) / 2, (PAGE - dh) / 2, width=dw, height=dh, mask="auto")


def draw_paper(c: canvas.Canvas, seed: int) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#F3E6C8"))
    for index in range(30):
        x = ((index * 71 + seed * 31) % 199 + 5) * mm
        y = ((index * 47 + seed * 19) % 199 + 5) * mm
        c.circle(x, y, (0.35 + (index % 3) * .25) * mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#E2C782"))
    c.setLineWidth(1)
    c.roundRect(8 * mm, 8 * mm, PAGE - 16 * mm, PAGE - 16 * mm, 7 * mm, fill=0, stroke=1)


def wrap_lines(text: str, font_name: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font_name, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(c: canvas.Canvas, text: str, *, x: float, top: float, width: float, size: float,
              colour, font: str = REGULAR, leading: float | None = None,
              max_lines: int | None = None, centred: bool = False) -> float:
    leading = leading or size * 1.24
    lines = wrap_lines(text, font, size, width)
    if max_lines and len(lines) > max_lines:
        raise ValueError(f"Text does not fit: {text}")
    c.setFont(font, size)
    c.setFillColor(colour)
    y = top
    for line in lines:
        if line:
            if centred:
                c.drawCentredString(x + width / 2, y, line)
            else:
                c.drawString(x, y, line)
        y -= leading
    return y


def draw_story_text(c: canvas.Canvas, page: dict) -> None:
    heading = page.get("heading", "")
    top = PAGE - 13 * mm
    draw_text(c, heading, x=13.5 * mm, top=top - .6 * mm, width=183 * mm, size=23,
              colour=NAVY, font=BOLD, max_lines=2)
    draw_text(c, heading, x=13 * mm, top=top, width=183 * mm, size=23,
              colour=GOLD, font=BOLD, max_lines=2)
    body_top = top - (18 * mm if len(heading) < 28 else 27 * mm)
    body_size = 15.4 if page["page"] == 32 else 17.2
    body_leading = 18.8 if page["page"] == 32 else 21.5
    body_lines = 12 if page["page"] == 32 else 9
    draw_text(c, page["text"], x=13.5 * mm, top=body_top - .6 * mm, width=183 * mm,
              size=body_size, colour=NAVY, leading=body_leading, max_lines=body_lines)
    draw_text(c, page["text"], x=13 * mm, top=body_top, width=183 * mm,
              size=body_size, colour=WHITE, leading=body_leading, max_lines=body_lines)


def draw_page_number(c: canvas.Canvas, number: int, dark: bool) -> None:
    c.setFillColor(WHITE if dark else INK)
    c.setFont(BOLD, 8)
    c.drawCentredString(PAGE / 2, 5.5 * mm, str(number))


def draw_cast(c: canvas.Canvas, names: list[str], *, y: float = 13 * mm, scale: float = 1.0) -> None:
    widths = {"Mia": 45 * mm, "Sol": 34 * mm, "Tavi": 34 * mm, "Vee": 37 * mm}
    centres = {
        1: [105],
        2: [78, 132],
        3: [49, 104, 159],
        4: [30, 79, 128, 177],
    }[len(names)]
    for cx, name in zip(centres, names):
        w = widths[name] * scale
        c.drawImage(image(SPRITES[name]), cx * mm - w / 2, y, width=w, height=w,
                    preserveAspectRatio=True, anchor="c", mask="auto")


def draw_card(c: canvas.Canvas, role: str, cx: float, cy: float, size: float = 25 * mm,
              label: str | None = None, dim: bool = False, ring=None,
              dark_label: bool = True) -> None:
    fill = colors.HexColor("#FFF2C8") if not dim else colors.HexColor("#D8D4CA")
    c.setFillColor(fill)
    c.setStrokeColor(ring or GOLD)
    c.setLineWidth(3 if ring else 1.8)
    c.roundRect(cx - size / 2, cy - size / 2, size, size, 3.5 * mm, fill=1, stroke=1)
    inset = size * .14
    if role == "unknown":
        c.setFillColor(NAVY)
        c.setFont(BOLD, size * .48)
        c.drawCentredString(cx, cy - size * .16, "?")
    else:
        c.saveState()
        if dim:
            c.setFillAlpha(.35)
        c.drawImage(image(EMOJI[role]), cx - size / 2 + inset, cy - size / 2 + inset,
                    width=size - 2 * inset, height=size - 2 * inset, mask="auto")
        c.restoreState()
    if label:
        c.setFont(BOLD, 8.2)
        ly = cy + size / 2 + 4 * mm
        if not dark_label:
            c.setFillColor(NAVY)
            c.drawCentredString(cx + .4 * mm, ly - .4 * mm, label)
            c.setFillColor(WHITE)
        else:
            c.setFillColor(INK)
        c.drawCentredString(cx, ly, label)


def draw_arrow(c: canvas.Canvas, x1: float, x2: float, y: float, label: str | None = None,
               dark_label: bool = False) -> None:
    c.setStrokeColor(GOLD)
    c.setFillColor(GOLD)
    c.setLineWidth(3)
    c.line(x1, y, x2 - 4 * mm, y)
    path = c.beginPath()
    path.moveTo(x2, y)
    path.lineTo(x2 - 5 * mm, y + 3.5 * mm)
    path.lineTo(x2 - 5 * mm, y - 3.5 * mm)
    path.close()
    c.drawPath(path, fill=1, stroke=0)
    if label:
        c.setFillColor(INK if dark_label else WHITE)
        c.setFont(BOLD, 8)
        c.drawCentredString((x1 + x2) / 2, y + 5 * mm, label)


def draw_sequence(c: canvas.Canvas, roles: list[str], *, y: float, size: float = 25 * mm,
                  labels: list[str] | None = None, ring: int | None = None,
                  dark_labels: bool = True) -> None:
    gap = min(37 * mm, (PAGE - 30 * mm - size) / max(1, len(roles) - 1))
    total = size + gap * (len(roles) - 1)
    start = (PAGE - total) / 2 + size / 2
    for index, role in enumerate(roles):
        draw_card(c, role, start + gap * index, y, size=size,
                  label=labels[index] if labels else None,
                  ring=CORAL if ring == index else None,
                  dark_label=dark_labels)


def draw_turn(c: canvas.Canvas, before: str, after: str, *, y: float, paper: bool = False) -> None:
    label_colour = INK if paper else WHITE
    draw_card(c, before, 62 * mm, y, 35 * mm, label=f"BEFORE: {before.upper()}", dark_label=paper)
    draw_arrow(c, 83 * mm, 127 * mm, y, "ONE TURN", dark_label=paper)
    draw_card(c, after, 148 * mm, y, 35 * mm,
              label="AFTER: ?" if after == "unknown" else f"AFTER: {after.upper()}",
              dark_label=paper)
    if paper:
        c.setFillColor(label_colour)


def paper_heading(c: canvas.Canvas, page: dict) -> None:
    draw_text(c, page["heading"], x=16 * mm, top=PAGE - 20 * mm, width=178 * mm,
              size=25, colour=INK, font=BOLD, max_lines=2)
    draw_text(c, page["text"], x=16 * mm, top=PAGE - 42 * mm, width=178 * mm,
              size=16.2, colour=PURPLE, leading=20.5, max_lines=8)
    if page.get("subtext"):
        draw_text(c, page["subtext"], x=18 * mm, top=20 * mm, width=174 * mm,
                  size=10.5, colour=INK, font=BOLD, leading=14, max_lines=3, centred=True)


def draw_choices(c: canvas.Canvas, roles: tuple[str, str], y: float = 43 * mm) -> None:
    draw_card(c, roles[0], 76 * mm, y, 28 * mm, label=roles[0].upper())
    draw_card(c, roles[1], 134 * mm, y, 28 * mm, label=roles[1].upper())


def draw_arch_route(c: canvas.Canvas, cx: float, cy: float, over: bool, label: str,
                    dark_label: bool = True) -> None:
    c.setStrokeColor(TEAL if over else PURPLE)
    c.setLineWidth(4)
    c.arc(cx - 19 * mm, cy - 10 * mm, cx + 19 * mm, cy + 16 * mm, 0, 180)
    c.line(cx - 19 * mm, cy + 3 * mm, cx - 19 * mm, cy - 12 * mm)
    c.line(cx + 19 * mm, cy + 3 * mm, cx + 19 * mm, cy - 12 * mm)
    path_y = cy + 14 * mm if over else cy - 7 * mm
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.line(cx - 26 * mm, path_y, cx + 26 * mm, path_y)
    c.setFont(BOLD, 10)
    ly = cy + 25 * mm
    if dark_label:
        c.setFillColor(INK)
    else:
        c.setFillColor(NAVY)
        c.drawCentredString(cx + .4 * mm, ly - .4 * mm, label)
        c.setFillColor(WHITE)
    c.drawCentredString(cx, ly, label)


def draw_routes(c: canvas.Canvas, answer: bool) -> None:
    rows = [
        ("A", ["moon", "sun", "moon"], False),
        ("B", ["moon", "sun", "sun", "moon"], True),
        ("C", ["moon", "sun", "moon", "sun"], True),
    ]
    for idx, (name, roles, reaches) in enumerate(rows):
        y = (115 - idx * 34) * mm
        chosen = answer and name == "C"
        c.setFillColor(colors.HexColor("#F1E3BF"))
        c.setStrokeColor(GOLD if chosen else colors.HexColor("#8390A3"))
        c.setLineWidth(4 if chosen else 1.5)
        c.roundRect(18 * mm, y - 13 * mm, 174 * mm, 27 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont(BOLD, 15)
        c.drawCentredString(33 * mm, y - 2 * mm, name)
        for role_idx, role in enumerate(roles):
            draw_card(c, role, (58 + role_idx * 27) * mm, y, 19 * mm)
        c.setFont(BOLD, 8.5)
        c.setFillColor(INK)
        c.drawRightString(185 * mm, y - 2 * mm, "ARCH" if reaches else "STOPS")


def draw_activity(c: canvas.Canvas, page: dict) -> None:
    draw_paper(c, page["page"])
    paper_heading(c, page)
    activity = page["activity"]
    if activity == "showing-side":
        draw_card(c, "moon", PAGE / 2, 104 * mm, 42 * mm, label="TILE SHOWING NOW")
        draw_choices(c, ("moon", "sun"), 54 * mm)
    elif activity == "first-turn":
        draw_turn(c, "moon", "unknown", y=99 * mm, paper=True)
        draw_choices(c, ("moon", "sun"), 49 * mm)
    elif activity == "second-turn":
        draw_turn(c, "sun", "unknown", y=99 * mm, paper=True)
        draw_choices(c, ("moon", "sun"), 49 * mm)
    elif activity == "copy-row":
        draw_sequence(c, ["moon", "sun", "moon", "sun"], y=83 * mm, size=30 * mm,
                      labels=["MOON", "SUN", "MOON", "SUN"])
    elif activity == "next-light":
        draw_sequence(c, ["moon", "sun", "moon", "sun", "unknown"], y=91 * mm, size=25 * mm)
        draw_choices(c, ("moon", "sun"), 47 * mm)
    elif activity == "find-break":
        draw_sequence(c, ["moon", "sun", "moon", "moon"], y=82 * mm, size=30 * mm,
                      labels=["1", "2", "3", "4"])
    elif activity == "over-under":
        draw_arch_route(c, 50 * mm, 92 * mm, True, "OVER")
        draw_arch_route(c, 105 * mm, 92 * mm, False, "UNDER")
        draw_arch_route(c, 160 * mm, 92 * mm, True, "OVER")
        c.setFillColor(WHITE); c.setStrokeColor(GOLD); c.setLineWidth(2)
        c.roundRect(82 * mm, 44 * mm, 46 * mm, 25 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(BOLD, 18); c.drawCentredString(105 * mm, 51 * mm, "?")
    elif activity == "route-check":
        draw_routes(c, False)
    elif activity == "remember-turn":
        draw_turn(c, "moon", "unknown", y=99 * mm, paper=True)
        draw_choices(c, ("moon", "sun"), 49 * mm)
    elif activity == "new-roles":
        draw_sequence(c, ["star", "leaf", "star", "unknown"], y=91 * mm, size=28 * mm)
        draw_choices(c, ("star", "leaf"), 47 * mm)


def draw_story_diagram(c: canvas.Canvas, page: dict) -> None:
    n = page["page"]
    if n == 3:
        size = 35 * mm
        c.drawImage(image(EMOJI["lantern"]), 88 * mm, 54 * mm, width=size, height=size, mask="auto")
        draw_sequence(c, ["moon", "sun", "moon"], y=43 * mm, size=20 * mm)
    elif n == 4:
        draw_sequence(c, ["moon", "sun", "moon", "blank"], y=61 * mm, size=26 * mm,
                      labels=["MOON", "SUN", "MOON", "NO LIGHT"], dark_labels=False)
        draw_cast(c, ["Mia", "Tavi", "Sol"], y=5 * mm, scale=.55)
    elif n == 5:
        draw_sequence(c, ["moon", "sun", "moon", "blank"], y=65 * mm, size=22 * mm)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=9 * mm, scale=.78)
    elif n == 6:
        draw_card(c, "moon", 77 * mm, 66 * mm, 38 * mm, label="MOON SIDE", dark_label=False)
        draw_card(c, "sun", 133 * mm, 66 * mm, 38 * mm, label="SUN SIDE", dark_label=False)
        draw_cast(c, ["Mia", "Vee"], y=6 * mm, scale=.67)
    elif n == 8:
        draw_card(c, "moon", 83 * mm, 67 * mm, 40 * mm, label="SHOWING", dark_label=False)
        draw_card(c, "sun", 137 * mm, 50 * mm, 31 * mm, label="UNDERNEATH", dim=True, dark_label=False)
        draw_cast(c, ["Tavi", "Vee"], y=5 * mm, scale=.63)
    elif n == 9:
        draw_turn(c, "moon", "unknown", y=64 * mm)
        draw_cast(c, ["Mia", "Sol"], y=4 * mm, scale=.62)
    elif n == 11:
        draw_turn(c, "moon", "sun", y=64 * mm)
        draw_cast(c, ["Sol", "Vee"], y=4 * mm, scale=.62)
    elif n == 13:
        draw_turn(c, "sun", "moon", y=64 * mm)
        draw_cast(c, ["Tavi", "Vee"], y=4 * mm, scale=.62)
    elif n == 14:
        draw_sequence(c, ["moon", "sun", "moon"], y=62 * mm, size=32 * mm,
                      labels=["START", "ONE TURN", "RETURN"], dark_labels=False)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=2 * mm, scale=.48)
    elif n == 17:
        draw_sequence(c, ["moon", "sun", "moon", "sun", "moon"], y=61 * mm, size=24 * mm)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=2 * mm, scale=.48)
    elif n == 18:
        draw_sequence(c, ["moon", "sun", "moon", "moon"], y=61 * mm, size=28 * mm)
        draw_cast(c, ["Sol", "Vee"], y=3 * mm, scale=.63)
    elif n == 20:
        draw_sequence(c, ["moon", "sun", "moon", "moon"], y=67 * mm, size=25 * mm, ring=3)
        draw_card(c, "sun", 170 * mm, 30 * mm, 23 * mm, label="NEEDS SUN", dark_label=False)
        draw_cast(c, ["Sol", "Tavi"], y=2 * mm, scale=.57)
    elif n == 21:
        c.setFillColor(WHITE); c.setFont(BOLD, 8); c.drawCentredString(PAGE / 2, 91 * mm, "FIRST TRY KEPT")
        draw_sequence(c, ["moon", "sun", "moon", "moon"], y=78 * mm, size=16 * mm)
        c.setFillColor(WHITE); c.setFont(BOLD, 10); c.drawCentredString(PAGE / 2, 56 * mm, "REPAIRED TRAIL")
        draw_sequence(c, ["moon", "sun", "moon", "sun"], y=40 * mm, size=22 * mm)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=5 * mm, scale=.40)
    elif n == 22:
        draw_arch_route(c, 75 * mm, 56 * mm, True, "OVER", dark_label=False)
        draw_arch_route(c, 140 * mm, 56 * mm, False, "UNDER", dark_label=False)
        draw_cast(c, ["Mia", "Vee"], y=3 * mm, scale=.58)
    elif n == 24:
        for idx, (over, label) in enumerate(((True, "OVER"), (False, "UNDER"), (True, "OVER"), (False, "UNDER"))):
            draw_arch_route(c, (37 + idx * 46) * mm, 50 * mm, over, label, dark_label=False)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=3 * mm, scale=.37)
    elif n in (25, 27):
        c.saveState(); c.translate(0, -16 * mm); draw_routes(c, n == 27); c.restoreState()
        draw_cast(c, ["Tavi", "Vee"] if n == 25 else ["Mia", "Tavi", "Sol", "Vee"],
                  y=4 * mm if n == 27 else 1 * mm, scale=.40 if n == 27 else .54)
    elif n == 29:
        draw_turn(c, "moon", "sun", y=63 * mm)
        draw_cast(c, ["Mia", "Tavi"], y=3 * mm, scale=.58)
    elif n == 31:
        draw_sequence(c, ["star", "leaf", "star", "leaf"], y=59 * mm, size=28 * mm)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=4 * mm, scale=.66)
    elif n == 32:
        draw_sequence(c, ["moon", "sun", "moon", "sun"], y=44 * mm, size=20 * mm)
        draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=5 * mm, scale=.42)


def draw_cover(c: canvas.Canvas, book: dict) -> None:
    draw_crop(c, SCENES["arch"])
    c.setFillColor(colors.Color(.02, .04, .10, alpha=.55))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(GOLD); c.setFont(BOLD, 10)
    c.drawCentredString(PAGE / 2, PAGE - 15 * mm, "A STAR ROOMS ADVENTURE · BOOK 3")
    c.setFillColor(WHITE); c.setFont(BOLD, 29)
    c.drawCentredString(PAGE / 2, PAGE - 37 * mm, book["title"])
    c.setFillColor(GOLD); c.setFont(BOLD, 18)
    c.drawCentredString(PAGE / 2, PAGE - 52 * mm, book["subtitle"])
    draw_sequence(c, ["moon", "sun", "moon"], y=103 * mm, size=25 * mm)
    draw_cast(c, ["Mia", "Tavi", "Sol", "Vee"], y=17 * mm, scale=.92)
    c.setFillColor(WHITE); c.setFont(BOLD, 12)
    c.drawCentredString(PAGE / 2, 9 * mm, "Maria Smith")


def draw_title(c: canvas.Canvas, book: dict, page: dict) -> None:
    draw_paper(c, 2)
    c.setFillColor(NAVY); c.setFont(BOLD, 28)
    c.drawCentredString(PAGE / 2, PAGE - 39 * mm, book["title"])
    c.setFillColor(PURPLE); c.setFont(BOLD, 18)
    c.drawCentredString(PAGE / 2, PAGE - 54 * mm, book["subtitle"])
    draw_sequence(c, ["moon", "sun", "moon"], y=112 * mm, size=30 * mm)
    draw_text(c, page["text"], x=27 * mm, top=82 * mm, width=156 * mm, size=13.5,
              colour=INK, leading=18, max_lines=5, centred=True)
    draw_text(c, page["subtext"], x=25 * mm, top=48 * mm, width=160 * mm, size=8.5,
              colour=colors.HexColor("#5A6473"), leading=11, max_lines=7, centred=True)


def render_page(c: canvas.Canvas, book: dict, page: dict) -> None:
    if page["kind"] == "cover":
        draw_cover(c, book)
        return
    if page["kind"] == "title":
        draw_title(c, book, page)
        draw_page_number(c, page["page"], False)
        return
    if page["kind"] == "activity":
        draw_activity(c, page)
        draw_page_number(c, page["page"], False)
        return
    draw_crop(c, SCENES[page["scene"]])
    c.setFillColor(colors.Color(.02, .04, .10, alpha=.34))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    draw_story_text(c, page)
    draw_story_diagram(c, page)
    draw_page_number(c, page["page"], True)


def render_pdf(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']}: {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Open Education Early Years picture book")
    c.setKeywords("Smithian Fold Theory, early years, Fold, turn, return, pattern")
    for page in book["pages"]:
        render_page(c, book, page)
        c.showPage()
    c.save()


def render_html(book: dict) -> None:
    sections = []
    for page in book["pages"]:
        text = html.escape(page.get("text", "")).replace("\n", "<br>")
        subtext = html.escape(page.get("subtext", "")).replace("\n", "<br>")
        activity = '<p class="activity"><strong>This page is a paper activity.</strong></p>' if page.get("activity") else ""
        alt = html.escape(page["alt"])
        sections.append(f'<section aria-labelledby="p{page["page"]}"><h2 id="p{page["page"]}">Page {page["page"]}: {html.escape(page["heading"])}</h2>{activity}<p>{text}</p><p>{subtext}</p><p class="description"><strong>Picture description:</strong> {alt}</p></section>')
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])} — accessible review {book['version']}</title><style>body{{font-family:Arial,sans-serif;line-height:1.6;max-width:48rem;margin:auto;padding:2rem;color:#1e2b42}}section{{border-bottom:1px solid #ddd;padding:1rem 0 2rem}}h1,h2{{line-height:1.2}}.activity{{background:#fff3c9;padding:1rem;border-left:6px solid #76519b}}.description{{color:#45566f}}</style></head><body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])}</p><p>By {html.escape(book['author'])} · Book 3 of 4 · ages 3–5 · review edition {book['version']}</p></header><main>{''.join(sections)}</main></body></html>'''
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    ACCESSIBLE_HTML.write_text(document, encoding="utf-8")


def main() -> None:
    book = load_book()
    missing = [p for p in list(SCENES.values()) + list(SPRITES.values()) + list(EMOJI.values()) if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing art: " + ", ".join(map(str, missing)))
    render_pdf(book)
    render_html(book)
    print(STUDENT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
