#!/usr/bin/env python3
"""Render E04 2.0.0 as a paper-native illustrated picture book."""

from __future__ import annotations

import html
import json
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from svglib.svglib import svg2rlg


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source/book-v2.0.0.json"
GAME = ROOT / "edu/games/companion-adventures"
OPENMOJI = GAME / "node_modules/openmoji/color/svg"
ART = GAME / "dist/client/art"
RELEASE_DIR = ROOT / "output/pdf/edu/SFT-EDU-E04-LOOK-AGAIN-HOW-WE-CHECK/2.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E04-Look-Again-How-We-Check-v2.0.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible/student-book-v2.0.0.html"

PAGE = 210 * mm
NAVY = colors.HexColor("#101A33")
INK = colors.HexColor("#1E2B42")
CREAM = colors.HexColor("#FFF7E7")
PAPER = colors.HexColor("#FFF2C8")
GOLD = colors.HexColor("#FFD45A")
TEAL = colors.HexColor("#54C9C5")
PURPLE = colors.HexColor("#76519B")
GREEN = colors.HexColor("#2C765C")
CORAL = colors.HexColor("#F06450")
WHITE = colors.white

SCENES = {
    "gate": ART / "stages/e04-source/e04-stage-01-look-and-point-v2.png",
    "look": ART / "stages/e04-source/e04-stage-01-look-and-point-v1.png",
    "build": ART / "stages/e04-source/e04-stage-02-build-the-board-v1.png",
    "curtain": ART / "stages/e04-source/e04-stage-03-curtain-memory-v1.png",
    "compare": ART / "stages/e04-source/e04-stage-04-difference-finder-v1.png",
    "steps": ART / "stages/e04-source/e04-stage-05-placement-record-v2.png",
    "measure": ART / "stages/e04-source/e04-stage-06-measuring-ribbon-v1.png",
    "friend": ART / "stages/e04-source/e04-stage-07-friend-check-v1.png",
    "height": ART / "stages/e04-source/e04-stage-08-height-check-v2.png",
    "checkpoint": ART / "stages/e04-source/e04-stage-09-record-checkpoint-v2.png",
}

SPRITES = {
    "Mia": ART / "characters/individual/mira-v1.png",
    "Sol": ART / "characters/individual/sol.png",
    "Tavi": ART / "characters/individual/tavi.png",
    "Ivo": ART / "characters/individual/ivo.png",
}

EMOJI = {
    "sun": "2600", "moon": "1F319", "leaf": "1F343", "star": "2B50",
    "sunflower": "1F33B", "bee": "1F41D", "apple": "1F34E", "boot": "1F97E",
    "yellow": "1F7E8", "blue": "1F7E6", "check": "2705", "cross": "274C",
    "lens": "1F50D", "unknown": "2753",
}

LABEL = {
    "sun": "SUN", "moon": "MOON", "leaf": "LEAF", "star": "STAR",
    "sunflower": "SUNFLOWER", "bee": "BEE", "apple": "APPLE", "boot": "BOOT",
}

PLAN = {"sun": "sunflower", "moon": "bee", "leaf": "apple", "star": "boot"}
FAILED = {"sun": "sunflower", "moon": "boot", "leaf": "apple", "star": "bee"}
WRONG_C = {"sun": "apple", "moon": "bee", "leaf": "sunflower", "star": "boot"}
IMAGE_CACHE: dict[Path, ImageReader] = {}
SVG_CACHE = {}


def register_fonts() -> tuple[str, str]:
    regular = GAME / "node_modules/@vercel/og/dist/noto-sans-v27-latin-regular.ttf"
    if regular.exists():
        pdfmetrics.registerFont(TTFont("SFTNoto", str(regular)))
        return "SFTNoto", "Helvetica-Bold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = register_fonts()


def raster(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def svg(name: str):
    path = OPENMOJI / f"{EMOJI[name]}.svg"
    if name not in SVG_CACHE:
        SVG_CACHE[name] = svg2rlg(str(path))
    return SVG_CACHE[name]


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32 or [p["page"] for p in book["pages"]] != list(range(1, 33)):
        raise ValueError("E04 2.0.0 must contain exactly 32 contiguous pages")
    return book


def wrap_lines(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        words = paragraph.split()
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if pdfmetrics.stringWidth(trial, font, size) <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(c: canvas.Canvas, text: str, *, x: float, top: float, width: float,
              size: float, colour, font: str = REGULAR, leading: float | None = None,
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


def draw_emoji(c: canvas.Canvas, name: str, cx: float, cy: float, size: float) -> None:
    drawing = svg(name)
    scale = size / max(drawing.width, drawing.height)
    c.saveState()
    c.translate(cx - drawing.width * scale / 2, cy - drawing.height * scale / 2)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()


def draw_crop(c: canvas.Canvas, path: Path) -> None:
    reader = raster(path)
    iw, ih = reader.getSize()
    scale = max(PAGE / iw, PAGE / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(reader, (PAGE - dw) / 2, (PAGE - dh) / 2, width=dw, height=dh, mask="auto")


def draw_paper(c: canvas.Canvas, seed: int) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#F2E4C1"))
    for index in range(28):
        x = ((index * 71 + seed * 31) % 199 + 5) * mm
        y = ((index * 47 + seed * 19) % 199 + 5) * mm
        c.circle(x, y, (.35 + (index % 3) * .25) * mm, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#E2C782"))
    c.roundRect(8 * mm, 8 * mm, PAGE - 16 * mm, PAGE - 16 * mm, 7 * mm, fill=0, stroke=1)


def draw_page_number(c: canvas.Canvas, number: int, dark: bool) -> None:
    c.setFillColor(WHITE if dark else INK)
    c.setFont(BOLD, 8)
    c.drawCentredString(PAGE / 2, 5.5 * mm, str(number))


def draw_cast(c: canvas.Canvas, names: list[str], *, y: float = 5 * mm, scale: float = 1.0) -> None:
    widths = {"Mia": 45 * mm, "Sol": 34 * mm, "Tavi": 34 * mm, "Ivo": 36 * mm}
    centres = {1: [105], 2: [78, 132], 3: [49, 104, 159], 4: [30, 79, 128, 177]}[len(names)]
    for cx, name in zip(centres, names):
        w = widths[name] * scale
        c.drawImage(raster(SPRITES[name]), cx * mm - w / 2, y, width=w, height=w,
                    preserveAspectRatio=True, anchor="c", mask="auto")


def draw_card(c: canvas.Canvas, name: str, cx: float, cy: float, size: float = 25 * mm,
              label: str | None = None, ring=None, light_label: bool = False) -> None:
    c.setFillColor(PAPER)
    c.setStrokeColor(ring or GOLD)
    c.setLineWidth(3 if ring else 1.6)
    c.roundRect(cx - size / 2, cy - size / 2, size, size, 3.5 * mm, fill=1, stroke=1)
    if label:
        c.setFont(BOLD, min(9, size / mm * .32))
        if light_label:
            c.setFillColor(NAVY)
            c.drawCentredString(cx + .4 * mm, cy + size / 2 + 3.6 * mm, label)
            c.setFillColor(WHITE)
        else:
            c.setFillColor(INK)
        c.drawCentredString(cx, cy + size / 2 + 4 * mm, label)
    draw_emoji(c, name, cx, cy - size * .03, size * .68)


def draw_choice_cards(c: canvas.Canvas, names: list[str], y: float, *, size: float = 25 * mm,
                      light_label: bool = False) -> None:
    gap = min(38 * mm, (PAGE - 28 * mm - size) / max(1, len(names) - 1))
    total = size + gap * (len(names) - 1)
    start = (PAGE - total) / 2 + size / 2
    for index, name in enumerate(names):
        draw_card(c, name, start + gap * index, y, size, LABEL.get(name, name.upper()),
                  light_label=light_label)


def draw_sign(c: canvas.Canvas, cx: float, cy: float, mapping: dict[str, str] | None,
              title: str, width: float = 72 * mm, height: float = 58 * mm,
              highlight: set[str] | None = None, covered: bool = False,
              cover_label: str = "PLAN COVERED") -> None:
    highlight = highlight or set()
    c.setFillColor(colors.HexColor("#6A432E"))
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.roundRect(cx - width / 2, cy - height / 2, width, height, 5 * mm, fill=1, stroke=1)
    c.setFillColor(GOLD)
    c.roundRect(cx - width * .38, cy + height / 2 + 2 * mm, width * .76, 8 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont(BOLD, 7.5)
    c.drawCentredString(cx, cy + height / 2 + 4.7 * mm, title)
    gap = 2 * mm
    cell_w = (width - 6 * mm - gap) / 2
    cell_h = (height - 6 * mm - gap) / 2
    positions = {
        "sun": (-1, 1), "moon": (1, 1), "leaf": (-1, -1), "star": (1, -1)
    }
    for corner, (sx, sy) in positions.items():
        px = cx + sx * (cell_w + gap) / 2
        py = cy + sy * (cell_h + gap) / 2
        c.setFillColor(colors.HexColor("#FFF9E7"))
        c.setStrokeColor(CORAL if corner in highlight else colors.HexColor("#D8CDAA"))
        c.setLineWidth(3 if corner in highlight else 1)
        c.roundRect(px - cell_w / 2, py - cell_h / 2, cell_w, cell_h, 2.2 * mm, fill=1, stroke=1)
        draw_emoji(c, corner, px - cell_w * .36, py - cell_h * .28, min(7 * mm, cell_h * .28))
        if mapping:
            item = mapping[corner]
            c.setFillColor(INK)
            c.setFont(BOLD, min(6.3, cell_w / mm * .22))
            c.drawCentredString(px + 2 * mm, py + cell_h * .28, LABEL[item])
            draw_emoji(c, item, px + 2 * mm, py - cell_h * .10, min(14 * mm, cell_h * .58))
        else:
            c.setFillColor(INK)
            c.setFont(BOLD, 18)
            c.drawCentredString(px + 2 * mm, py - 2 * mm, "?")
    if covered:
        c.setFillColor(colors.HexColor("#E4A941"))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(cx - width / 2 + 2 * mm, cy - height / 2 + 2 * mm,
                    width - 4 * mm, height - 4 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(BOLD, 10)
        c.drawCentredString(cx, cy - 2 * mm, cover_label)


def draw_plan_and_blank(c: canvas.Canvas, y: float, failed: bool = False) -> None:
    draw_sign(c, 61 * mm, y, PLAN, "PICTURE PLAN", 74 * mm, 59 * mm)
    draw_sign(c, 149 * mm, y, FAILED if failed else None, "SOL'S FIRST TRY" if failed else "BLANK SIGN", 74 * mm, 59 * mm)


def draw_step_cards(c: canvas.Canvas, *, y: float, answer: bool) -> None:
    steps = [("sunflower", "sun"), ("apple", "leaf"), ("boot", "moon"), ("bee", "star")]
    centres = [33, 81, 129, 177]
    for index, ((item, corner), cx) in enumerate(zip(steps, centres), start=1):
        c.setFillColor(PAPER)
        c.setStrokeColor(CORAL if answer and index == 3 else GOLD)
        c.setLineWidth(4 if answer and index == 3 else 1.5)
        c.roundRect((cx - 19) * mm, y - 24 * mm, 38 * mm, 48 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(BOLD, 8)
        c.drawCentredString(cx * mm, y + 18 * mm, f"STEP {index}")
        c.drawCentredString(cx * mm, y + 11 * mm, LABEL[item])
        draw_emoji(c, item, cx * mm, y, 17 * mm)
        c.setFont(BOLD, 7); c.drawCentredString(cx * mm, y - 17 * mm, f"TO {LABEL[corner]}")
        draw_emoji(c, corner, (cx - 12) * mm, y - 16 * mm, 6 * mm)


def draw_tiles(c: canvas.Canvas, *, horizontal: bool, answer: bool, y: float = 78 * mm) -> None:
    c.setFillColor(colors.HexColor("#E8D8B0"))
    c.setStrokeColor(INK); c.setLineWidth(2)
    c.roundRect(55 * mm, 55 * mm, 100 * mm, 64 * mm, 6 * mm, fill=1, stroke=1)
    c.setFillColor(INK); c.setFont(BOLD, 10)
    c.drawCentredString(PAGE / 2, 108 * mm, "WELCOME SIGN")
    if horizontal:
        for index in range(4):
            draw_emoji(c, "yellow", (77 + index * 19) * mm, y, 17 * mm)
        label = "4 TILES WIDE"
        if answer:
            c.setFillColor(WHITE); c.setFont(BOLD, 8)
            c.drawCentredString(PAGE / 2, 49 * mm, "GATE SPACE")
            for index in range(4):
                draw_emoji(c, "yellow", (84 + index * 14) * mm, 38 * mm, 12 * mm)
    else:
        sign_x = 80 * mm if answer else 105 * mm
        for index in range(3):
            draw_emoji(c, "blue", sign_x, (65 + index * 18) * mm, 16 * mm)
        label = "3 TILES TALL"
        if answer:
            c.setFillColor(colors.HexColor("#E8D8B0")); c.rect(67 * mm, 103 * mm, 76 * mm, 10 * mm, fill=1, stroke=0)
            c.setFillColor(INK); c.setFont(BOLD, 7.5)
            c.drawCentredString(80 * mm, 108 * mm, "SIGN")
            c.drawCentredString(130 * mm, 108 * mm, "GATE SPACE")
            for index in range(3):
                draw_emoji(c, "blue", 130 * mm, (65 + index * 18) * mm, 13 * mm)
    if answer and not horizontal:
        c.setFillColor(GREEN); c.roundRect(76 * mm, 38 * mm, 58 * mm, 10 * mm, 5 * mm, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont(BOLD, 9); c.drawCentredString(PAGE / 2, 41.5 * mm, label)


def draw_paper_heading(c: canvas.Canvas, page: dict) -> None:
    draw_text(c, page["heading"], x=16 * mm, top=PAGE - 20 * mm, width=178 * mm,
              size=25, colour=INK, font=BOLD, max_lines=2)
    draw_text(c, page["text"], x=16 * mm, top=PAGE - 42 * mm, width=178 * mm,
              size=16.2, colour=PURPLE, leading=20.5, max_lines=8)
    draw_text(c, page["subtext"], x=18 * mm, top=20 * mm, width=174 * mm,
              size=10.5, colour=INK, font=BOLD, leading=14, max_lines=3, centred=True)


def draw_word_choices(c: canvas.Canvas, words: list[str], y: float) -> None:
    width = 45 * mm if len(words) == 3 else 63 * mm
    gap = 8 * mm
    total = len(words) * width + (len(words) - 1) * gap
    start = (PAGE - total) / 2
    for index, word in enumerate(words):
        x = start + index * (width + gap)
        c.setFillColor(PAPER); c.setStrokeColor(GOLD); c.setLineWidth(2)
        c.roundRect(x, y, width, 23 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(BOLD, 12 if len(word) < 10 else 9)
        c.drawCentredString(x + width / 2, y + 8 * mm, word)


def draw_activity(c: canvas.Canvas, page: dict) -> None:
    draw_paper(c, page["page"])
    draw_paper_heading(c, page)
    kind = page["activity"]
    if kind == "moon-picture":
        draw_sign(c, PAGE / 2, 100 * mm, PLAN, "PICTURE PLAN", 76 * mm, 59 * mm)
        draw_choice_cards(c, ["sunflower", "bee", "apple", "boot"], 42 * mm, size=23 * mm)
    elif kind == "choose-sign":
        mappings = [FAILED, PLAN, WRONG_C]
        for cx, mapping, title in zip((39, 105, 171), mappings, ("A", "B", "C")):
            draw_sign(c, cx * mm, 80 * mm, mapping, title, 57 * mm, 48 * mm)
    elif kind == "star-memory":
        draw_sign(c, PAGE / 2, 100 * mm, PLAN, "PICTURE PLAN", 76 * mm, 59 * mm, covered=True)
        draw_choice_cards(c, ["bee", "apple", "boot"], 42 * mm, size=25 * mm)
    elif kind == "find-changes":
        draw_plan_and_blank(c, 78 * mm, failed=True)
    elif kind == "first-change":
        draw_sign(c, PAGE / 2, 108 * mm, PLAN, "PICTURE PLAN", 58 * mm, 44 * mm)
        draw_step_cards(c, y=52 * mm, answer=False)
    elif kind == "repair-moon":
        draw_sign(c, PAGE / 2, 95 * mm, FAILED, "SOL'S FIRST TRY", 76 * mm, 59 * mm, {"moon"})
        draw_choice_cards(c, ["sunflower", "bee", "apple", "boot"], 41 * mm, size=22 * mm)
    elif kind == "width-count":
        draw_tiles(c, horizontal=True, answer=False)
        draw_word_choices(c, ["3", "4", "5"], 30 * mm)
    elif kind == "height-count":
        draw_tiles(c, horizontal=False, answer=False)
        draw_word_choices(c, ["2", "3", "4"], 30 * mm)
    elif kind == "friend-compare":
        draw_sign(c, 61 * mm, 82 * mm, PLAN, "TEAM SIGN", 74 * mm, 59 * mm)
        draw_sign(c, 149 * mm, 82 * mm, PLAN, "IVO'S SIGN", 74 * mm, 59 * mm)
        draw_word_choices(c, ["SAME", "DIFFERENT"], 29 * mm)
    elif kind == "choose-picture-check":
        draw_record_cards(c, 74 * mm, simple=True)
    elif kind == "ready-check":
        draw_record_cards(c, 80 * mm, complete=True)
        draw_word_choices(c, ["YES", "NOT YET"], 29 * mm)


def draw_record_cards(c: canvas.Canvas, y: float, *, simple: bool = False, complete: bool = False) -> None:
    labels = ["PLAN + SIGN", "WIDTH TILES", "HEIGHT TILES"] if simple else ["PICTURES", "WIDTH", "HEIGHT", "IVO'S SIGN"]
    names = ["sunflower", "yellow", "blue"] if simple else ["sunflower", "yellow", "blue", "bee"]
    centres = [45, 105, 165] if simple else [31, 80, 129, 178]
    size = 36 * mm if simple else 32 * mm
    for index, (label, name, cx) in enumerate(zip(labels, names, centres)):
        c.setFillColor(PAPER); c.setStrokeColor(GREEN if complete else GOLD); c.setLineWidth(2)
        c.roundRect(cx * mm - size / 2, y - size / 2, size, size, 4 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(BOLD, 7)
        c.drawCentredString(cx * mm, y + size / 2 - 7 * mm, label)
        if index == 0:
            for panel_x in (cx * mm - 7 * mm, cx * mm + 7 * mm):
                c.setFillColor(colors.HexColor("#FFF9E7")); c.setStrokeColor(INK); c.setLineWidth(1)
                c.roundRect(panel_x - 6 * mm, y - 9 * mm, 12 * mm, 15 * mm, 2 * mm, fill=1, stroke=1)
                draw_emoji(c, "sunflower", panel_x, y - 1.5 * mm, 8 * mm)
        else:
            draw_emoji(c, name, cx * mm, y - 2 * mm, 15 * mm)
        if complete:
            draw_emoji(c, "check", cx * mm + 10 * mm, y - 10 * mm, 8 * mm)


def draw_story_text(c: canvas.Canvas, page: dict) -> None:
    top = PAGE - 13 * mm
    draw_text(c, page["heading"], x=13.5 * mm, top=top - .6 * mm, width=183 * mm,
              size=23, colour=NAVY, font=BOLD, max_lines=2)
    draw_text(c, page["heading"], x=13 * mm, top=top, width=183 * mm,
              size=23, colour=GOLD, font=BOLD, max_lines=2)
    body_top = top - (18 * mm if len(page["heading"]) < 28 else 27 * mm)
    size = 15.2 if page["page"] == 32 else 17.0
    leading = 18.4 if page["page"] == 32 else 21.2
    max_lines = 12 if page["page"] == 32 else 9
    draw_text(c, page["text"], x=13.5 * mm, top=body_top - .6 * mm, width=183 * mm,
              size=size, colour=NAVY, leading=leading, max_lines=max_lines)
    draw_text(c, page["text"], x=13 * mm, top=body_top, width=183 * mm,
              size=size, colour=WHITE, leading=leading, max_lines=max_lines)


def draw_story_diagram(c: canvas.Canvas, page: dict) -> None:
    kind = page.get("diagram")
    cast = page.get("cast", [])
    if kind == "plan-and-blank":
        draw_plan_and_blank(c, 66 * mm)
    elif kind == "lens":
        draw_emoji(c, "lens", PAGE / 2, 65 * mm, 34 * mm)
    elif kind == "plan":
        draw_sign(c, PAGE / 2, 64 * mm, PLAN, "PICTURE PLAN", 76 * mm, 59 * mm)
    elif kind == "moon-answer":
        draw_card(c, "moon", 80 * mm, 62 * mm, 34 * mm, "MOON", light_label=True)
        draw_card(c, "bee", 130 * mm, 62 * mm, 34 * mm, "BEE", GREEN, light_label=True)
    elif kind == "loose-cards":
        draw_choice_cards(c, ["sunflower", "bee", "apple", "boot"], 62 * mm,
                          size=25 * mm, light_label=True)
    elif kind == "matching-sign":
        draw_sign(c, 61 * mm, 65 * mm, PLAN, "PICTURE PLAN", 72 * mm, 57 * mm)
        draw_sign(c, 149 * mm, 65 * mm, PLAN, "SIGN B", 72 * mm, 57 * mm)
    elif kind == "plan-covered":
        draw_sign(c, 61 * mm, 65 * mm, PLAN, "LOOK ONCE", 72 * mm, 57 * mm)
        draw_sign(c, 149 * mm, 65 * mm, PLAN, "THEN COVER", 72 * mm, 57 * mm, covered=True)
    elif kind == "star-answer":
        draw_sign(c, PAGE / 2, 64 * mm, PLAN, "LOOK AGAIN", 78 * mm, 60 * mm, {"star"})
    elif kind == "changes-answer":
        draw_sign(c, 61 * mm, 66 * mm, PLAN, "PICTURE PLAN", 72 * mm, 57 * mm, {"moon", "star"})
        draw_sign(c, 149 * mm, 66 * mm, FAILED, "SOL'S FIRST TRY", 72 * mm, 57 * mm, {"moon", "star"})
    elif kind == "step-answer":
        draw_step_cards(c, y=63 * mm, answer=True)
    elif kind == "repaired-sign":
        draw_sign(c, 61 * mm, 65 * mm, PLAN, "PICTURE PLAN", 72 * mm, 57 * mm)
        draw_sign(c, 149 * mm, 65 * mm, PLAN, "REPAIRED SIGN", 72 * mm, 57 * mm)
    elif kind == "width-answer":
        draw_tiles(c, horizontal=True, answer=True, y=78 * mm)
    elif kind == "height-answer":
        draw_tiles(c, horizontal=False, answer=True)
    elif kind == "friend-build":
        draw_sign(c, 61 * mm, 65 * mm, PLAN, "TEAM SIGN", 72 * mm, 57 * mm,
                  covered=True, cover_label="TEAM SIGN COVERED")
        draw_sign(c, 149 * mm, 65 * mm, PLAN, "IVO'S OWN SIGN", 72 * mm, 57 * mm)
    elif kind == "friend-answer":
        draw_sign(c, 61 * mm, 67 * mm, PLAN, "TEAM SIGN", 70 * mm, 56 * mm)
        draw_sign(c, 149 * mm, 67 * mm, PLAN, "IVO'S SIGN", 70 * mm, 56 * mm)
        for x in (46, 76, 134, 164):
            draw_emoji(c, "check", x * mm, 29 * mm, 8 * mm)
    elif kind == "records":
        draw_record_cards(c, 59 * mm, complete=True)
    elif kind == "gate-open":
        draw_sign(c, PAGE / 2, 64 * mm, PLAN, "CHECKED WELCOME SIGN", 82 * mm, 62 * mm)
    elif kind == "final-sign":
        draw_sign(c, PAGE / 2, 51 * mm, PLAN, "CHECKED WELCOME SIGN", 75 * mm, 58 * mm)
    if cast:
        y = 2 * mm if kind in {"matching-sign", "changes-answer", "repaired-sign", "friend-answer", "records", "gate-open", "final-sign"} else 3 * mm
        scale = .38 if len(cast) == 4 else .52
        draw_cast(c, cast, y=y, scale=scale)


def draw_cover(c: canvas.Canvas, book: dict) -> None:
    draw_crop(c, SCENES["gate"])
    c.setFillColor(colors.Color(.02, .04, .10, alpha=.55)); c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(GOLD); c.setFont(BOLD, 10); c.drawCentredString(PAGE / 2, PAGE - 15 * mm, "A STAR ROOMS ADVENTURE · BOOK 4")
    c.setFillColor(WHITE); c.setFont(BOLD, 28); c.drawCentredString(PAGE / 2, PAGE - 36 * mm, book["title"])
    c.setFillColor(GOLD); c.setFont(BOLD, 18); c.drawCentredString(PAGE / 2, PAGE - 51 * mm, book["subtitle"])
    draw_sign(c, PAGE / 2, 104 * mm, PLAN, "GARDEN WELCOME SIGN", 82 * mm, 63 * mm)
    draw_cast(c, ["Mia", "Tavi", "Sol", "Ivo"], y=15 * mm, scale=.86)
    c.setFillColor(WHITE); c.setFont(BOLD, 12); c.drawCentredString(PAGE / 2, 8 * mm, "Maria Smith")


def draw_title(c: canvas.Canvas, book: dict, page: dict) -> None:
    draw_paper(c, 2)
    c.setFillColor(NAVY); c.setFont(BOLD, 27); c.drawCentredString(PAGE / 2, PAGE - 37 * mm, book["title"])
    c.setFillColor(PURPLE); c.setFont(BOLD, 17); c.drawCentredString(PAGE / 2, PAGE - 52 * mm, book["subtitle"])
    draw_choice_cards(c, ["sunflower", "bee", "apple", "boot"], 112 * mm, size=28 * mm)
    draw_text(c, page["text"], x=27 * mm, top=81 * mm, width=156 * mm, size=13.2,
              colour=INK, leading=17.5, max_lines=7, centred=True)
    draw_text(c, page["subtext"], x=25 * mm, top=41 * mm, width=160 * mm, size=8.2,
              colour=colors.HexColor("#5A6473"), leading=10.5, max_lines=7, centred=True)


def render_page(c: canvas.Canvas, book: dict, page: dict) -> None:
    if page["kind"] == "cover":
        draw_cover(c, book); return
    if page["kind"] == "title":
        draw_title(c, book, page); draw_page_number(c, page["page"], False); return
    if page["kind"] == "activity":
        draw_activity(c, page); draw_page_number(c, page["page"], False); return
    draw_crop(c, SCENES[page["scene"]])
    c.setFillColor(colors.Color(.02, .04, .10, alpha=.38)); c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    draw_story_text(c, page)
    draw_story_diagram(c, page)
    draw_page_number(c, page["page"], True)


def render_pdf(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']}: {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Open Education Early Years paper-native picture book")
    c.setKeywords("Smithian Fold Theory, early years, checking, observation, measurement")
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
        sections.append(f'<section aria-labelledby="p{page["page"]}"><h2 id="p{page["page"]}">Page {page["page"]}: {html.escape(page["heading"])}</h2>{activity}<p>{text}</p><p>{subtext}</p><p class="description"><strong>Picture description:</strong> {html.escape(page["alt"])}</p></section>')
    document = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])} — accessible review {book['version']}</title><style>body{{font-family:Arial,sans-serif;line-height:1.6;max-width:48rem;margin:auto;padding:2rem;color:#1e2b42}}section{{border-bottom:1px solid #ddd;padding:1rem 0 2rem}}h1,h2{{line-height:1.2}}.activity{{background:#fff3c9;padding:1rem;border-left:6px solid #76519b}}.description{{color:#45566f}}</style></head><body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])}</p><p>By {html.escape(book['author'])} · Book 4 of 4 · ages 3–5 · review edition {book['version']}</p></header><main>{''.join(sections)}</main></body></html>'''
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    ACCESSIBLE_HTML.write_text(document, encoding="utf-8")


def main() -> None:
    book = load_book()
    required = list(SCENES.values()) + list(SPRITES.values()) + [OPENMOJI / f"{code}.svg" for code in EMOJI.values()]
    missing = [p for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing art: " + ", ".join(map(str, missing)))
    render_pdf(book)
    render_html(book)
    print(STUDENT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
