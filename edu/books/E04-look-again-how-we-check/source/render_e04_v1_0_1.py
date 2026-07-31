#!/usr/bin/env python3
"""Render the complete E04 review edition 1.0.1 from canonical sources."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate

import generate_accessible_e04_v1_0_1
import render_e04_v1_0 as legacy


base = legacy.base
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.1.json"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"
RELEASE_DIR = BOOK_DIR / "editions" / "1.0.1"
STUDENT_PDF = RELEASE_DIR / "SFT-E04-Look-Again-How-We-Check-v1.0.1.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E04-Adult-Guide-v1.0.1.pdf"

PAGE = legacy.PAGE
NAVY = legacy.NAVY
INK = legacy.INK
CREAM = legacy.CREAM
PAPER = legacy.PAPER
GOLD = legacy.GOLD
GREEN = legacy.GREEN
MOSS = legacy.MOSS
TEAL = legacy.TEAL
BLUE = legacy.BLUE
PURPLE = legacy.PURPLE
CORAL = legacy.CORAL
GREY = legacy.GREY
WHITE = legacy.WHITE
SOURCE_MAP = legacy.SOURCE_MAP
FAILED_MAP = legacy.FAILED_MAP
MARKER_ORDER = legacy.MARKER_ORDER
DISPLAY = legacy.DISPLAY


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if book.get("version") != "1.0.1":
        raise ValueError("E04 renderer requires canonical version 1.0.1")
    if len(pages) != 32 or [page["page"] for page in pages] != list(range(1, 33)):
        raise ValueError("E04 1.0.1 must contain exactly 32 ordered pages")
    return book


def pill(*args, **kwargs) -> None:
    legacy.pill(*args, **kwargs)


def draw_sign(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    mapping: dict[str, str] | None,
    title: str,
    width: float = 78 * mm,
    height: float = 60 * mm,
    highlighted: set[str] | None = None,
    covered: bool = False,
    cover_label: str = "PICTURE PLAN COVERED",
) -> None:
    """Draw a sign with a protected word band above every object picture."""
    highlighted = highlighted or set()
    c.saveState()
    c.setFillColor(legacy.DARK_WOOD)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.roundRect(cx - width / 2, cy - height / 2, width, height, 5 * mm, fill=1, stroke=1)
    pill(c, title, cx - width * .42, cy + height / 2 + 2 * mm, width * .84, GOLD, 8 * mm)

    gap = 2 * mm
    cell_w = (width - 6 * mm - gap) / 2
    cell_h = (height - 6 * mm - gap) / 2
    positions = {
        "sun": (cx - cell_w / 2 - gap / 2, cy + cell_h / 2 + gap / 2),
        "moon": (cx + cell_w / 2 + gap / 2, cy + cell_h / 2 + gap / 2),
        "leaf": (cx - cell_w / 2 - gap / 2, cy - cell_h / 2 - gap / 2),
        "star": (cx + cell_w / 2 + gap / 2, cy - cell_h / 2 - gap / 2),
    }
    natural_bounds = {
        "sunflower": (16.0, 22.0, 0.0, 2.0),
        "bee": (20.0, 16.0, 0.0, 2.0),
        "watering can": (35.0, 22.0, -5.5, 3.0),
        "boot": (23.0, 25.0, 3.5, -0.5),
    }
    for marker in MARKER_ORDER:
        px, py = positions[marker]
        left = px - cell_w / 2
        bottom = py - cell_h / 2
        top = py + cell_h / 2
        c.setFillColor(PAPER)
        c.setStrokeColor(CORAL if marker in highlighted else colors.HexColor("#D9CDAA"))
        c.setLineWidth(3 if marker in highlighted else 1)
        c.roundRect(left, bottom, cell_w, cell_h, 2.2 * mm, fill=1, stroke=1)

        marker_radius = min(2.2 * mm, cell_h * .15)
        marker_x = left + 3.2 * mm
        marker_y = top - 3.2 * mm
        legacy.draw_marker(c, marker, marker_x, marker_y, marker_radius)

        if mapping:
            item = mapping[marker]
            label_h = min(4.4 * mm, max(3.2 * mm, cell_h * .24))
            label_x = left + 6.3 * mm
            label_y = top - label_h - .7 * mm
            label_w = cell_w - 7.2 * mm
            # The opaque label band and reserved gap ensure that no petal,
            # spout, wing or boot edge can enter the word area.
            c.setFillColor(PAPER)
            c.roundRect(label_x, label_y, label_w, label_h, .8 * mm, fill=1, stroke=0)
            max_label_size = 5.1 if cell_h >= 18 * mm else 4.4
            base.paragraph_in_box(
                c, DISPLAY[item], label_x + .4 * mm, label_y,
                label_w - .8 * mm, label_h, max_label_size, 3.4, INK,
            )

            art_bottom = bottom + .9 * mm
            art_top = label_y - .8 * mm
            art_height = max(4 * mm, art_top - art_bottom)
            art_width = max(8 * mm, cell_w - 3.2 * mm)
            natural_w, natural_h, x_offset, y_offset = natural_bounds[item]
            scale = min(
                .56,
                art_width / (natural_w * mm),
                art_height / (natural_h * mm),
            )
            art_cx = px - x_offset * mm * scale
            art_cy = (art_bottom + art_top) / 2 - y_offset * mm * scale
            legacy.draw_picture(c, item, art_cx, art_cy, scale)
        else:
            c.setFillColor(colors.HexColor("#E8E0CB"))
            c.setFont(base.font("bold"), max(9, min(18, cell_h / mm * .72)))
            c.drawCentredString(px, py - 2 * mm, "?")
    c.restoreState()

    if not covered:
        return
    c.saveState()
    c.setFillColor(MOSS)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.roundRect(
        cx - width / 2 + 2 * mm,
        cy - height / 2 + 2 * mm,
        width - 4 * mm,
        height - 4 * mm,
        4 * mm,
        fill=1,
        stroke=1,
    )
    rows = 3 if height < 45 * mm else 4
    columns = 6 if width < 64 * mm else 7
    for row in range(rows):
        for column in range(columns):
            px = cx - width * .38 + column * (width * .76 / max(1, columns - 1))
            py = cy - height * .30 + row * (height * .60 / max(1, rows - 1))
            legacy.draw_marker(c, "leaf", px, py, 2.1 * mm)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 6.2 if width < 64 * mm else 7.4)
    c.drawCentredString(cx, cy - 1.5 * mm, cover_label)
    c.restoreState()


def draw_choice_row(
    c: canvas.Canvas,
    items: list[str],
    cx: float,
    cy: float,
    width: float = 150 * mm,
) -> None:
    labels = {
        "does-not-match": "DOES NOT MATCH",
        "measure-bottom-to-top": "MEASURE BOTTOM TO TOP",
    }
    gap = 3 * mm
    cell = (width - gap * (len(items) - 1)) / len(items)
    start = cx - width / 2
    for index, item in enumerate(items):
        x = start + index * (cell + gap)
        c.setFillColor(PAPER)
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.5)
        c.roundRect(x, cy - 11 * mm, cell, 22 * mm, 3 * mm, fill=1, stroke=1)
        label = labels.get(item, DISPLAY.get(item, item.replace("-", " ").upper()))
        if item in DISPLAY:
            legacy.draw_picture(c, item, x + cell / 2, cy - 1 * mm, .38)
            c.setFillColor(INK)
            c.setFont(base.font("bold"), 4.4)
            c.drawCentredString(x + cell / 2, cy + 7 * mm, label)
        else:
            base.paragraph_in_box(
                c, label, x + 2 * mm, cy - 8 * mm, cell - 4 * mm,
                16 * mm, 7.2, 4.8, INK,
            )


def draw_step_cards(c: canvas.Canvas, cx: float, cy: float, answer: bool = False) -> None:
    steps = (("sunflower", "SUN"), ("watering can", "LEAF"), ("boot", "MOON"), ("bee", "STAR"))
    gap = 34 * mm
    start = cx - gap * 1.5
    for index, (item, corner) in enumerate(steps, start=1):
        x = start + (index - 1) * gap
        c.setFillColor(PAPER)
        c.setStrokeColor(CORAL if answer and index == 3 else GOLD)
        c.setLineWidth(3 if answer and index == 3 else 1.5)
        c.roundRect(x - 14 * mm, cy - 15 * mm, 28 * mm, 30 * mm, 3 * mm, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont(base.font("bold"), 5.2)
        c.drawCentredString(x, cy + 9.5 * mm, f"STEP {index}")
        legacy.draw_picture(c, item, x, cy - 1 * mm, .32)
        c.setFont(base.font("bold"), 4.3)
        c.drawCentredString(x, cy - 11 * mm, f"TO {corner}")
        if index < 4:
            legacy.draw_arrow(c, x + 15 * mm, cy, x + gap - 15 * mm, cy)
    if answer:
        # Keep the answer badge below Step 3 so the picture-plan boot remains
        # wholly visible and its word label stays unobstructed.
        pill(c, "FIRST CHANGE", start + gap * 2 - 15 * mm, cy - 26 * mm, 30 * mm, CORAL, 7 * mm)


def draw_measurement(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    direction: str,
    answer: bool = False,
) -> None:
    draw_sign(c, cx, cy, SOURCE_MAP, "REPAIRED SIGN", 68 * mm, 50 * mm)
    c.saveState()
    c.setStrokeColor(TEAL)
    c.setFillColor(TEAL)
    c.setLineWidth(4)
    if direction == "SIDE TO SIDE":
        y = cy - 32 * mm
        c.line(cx - 34 * mm, y, cx + 34 * mm, y)
        c.line(cx - 34 * mm, y - 5 * mm, cx - 34 * mm, y + 5 * mm)
        c.line(cx + 34 * mm, y - 5 * mm, cx + 34 * mm, y + 5 * mm)
        pill(c, "SIDE TO SIDE - WIDTH", cx - 28 * mm, y - 12 * mm, 56 * mm, TEAL, 7 * mm)
        result = "WIDTH: FITS"
    else:
        x = cx + 46 * mm
        c.line(x, cy - 25 * mm, x, cy + 25 * mm)
        c.line(x - 5 * mm, cy - 25 * mm, x + 5 * mm, cy - 25 * mm)
        c.line(x - 5 * mm, cy + 25 * mm, x + 5 * mm, cy + 25 * mm)
        pill(c, "BOTTOM TO TOP", x - 18 * mm, cy - 4 * mm, 36 * mm, TEAL, 7 * mm)
        result = "HEIGHT: FITS"
    c.restoreState()
    if answer:
        pill(c, result, cx - 24 * mm, cy + 34 * mm, 48 * mm, GREEN, 8 * mm)


def draw_mini_board(c: canvas.Canvas, cx: float, cy: float, size: float = 14 * mm) -> None:
    colors_by_cell = (GOLD, BLUE, MOSS, CORAL)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    for index, fill in enumerate(colors_by_cell):
        column = index % 2
        row = 1 - index // 2
        x = cx - size / 2 + column * size / 2
        y = cy - size / 2 + row * size / 2
        c.setFillColor(fill)
        c.rect(x, y, size / 2, size / 2, fill=1, stroke=1)


def draw_check_cards(c: canvas.Canvas, cx: float, cy: float, complete: bool = False) -> None:
    cards = (
        ("PICTURE-PLAN\nCOMPARISON", "pictures"),
        ("SIDE-TO-SIDE\nRIBBON", "width"),
        ("BOTTOM-TO-TOP\nRIBBON", "height"),
        ("IVO'S OWN\nSIGN", "ivo"),
    )
    gap = 3 * mm
    card_w = 36 * mm
    card_h = 47 * mm
    start = cx - (4 * card_w + 3 * gap) / 2
    for index, (label, kind) in enumerate(cards):
        x = start + index * (card_w + gap)
        c.setFillColor(PAPER)
        c.setStrokeColor(GREEN if complete else GOLD)
        c.setLineWidth(2.2)
        c.roundRect(x, cy - card_h / 2, card_w, card_h, 4 * mm, fill=1, stroke=1)
        base.paragraph_in_box(c, label, x + 2 * mm, cy + 11 * mm, card_w - 4 * mm, 10 * mm, 5.8, 4.4, INK)
        icon_y = cy - 5 * mm
        if kind == "pictures":
            draw_mini_board(c, x + 10 * mm, icon_y, 12 * mm)
            c.setFillColor(INK)
            c.setFont(base.font("bold"), 8)
            c.drawCentredString(x + card_w / 2, icon_y - 2 * mm, "=")
            draw_mini_board(c, x + card_w - 10 * mm, icon_y, 12 * mm)
        elif kind == "width":
            c.setStrokeColor(TEAL)
            c.setLineWidth(4)
            c.line(x + 7 * mm, icon_y, x + card_w - 7 * mm, icon_y)
            c.line(x + 7 * mm, icon_y - 5 * mm, x + 7 * mm, icon_y + 5 * mm)
            c.line(x + card_w - 7 * mm, icon_y - 5 * mm, x + card_w - 7 * mm, icon_y + 5 * mm)
        elif kind == "height":
            c.setStrokeColor(TEAL)
            c.setLineWidth(4)
            c.line(x + card_w / 2, icon_y - 10 * mm, x + card_w / 2, icon_y + 10 * mm)
            c.line(x + card_w / 2 - 5 * mm, icon_y - 10 * mm, x + card_w / 2 + 5 * mm, icon_y - 10 * mm)
            c.line(x + card_w / 2 - 5 * mm, icon_y + 10 * mm, x + card_w / 2 + 5 * mm, icon_y + 10 * mm)
        else:
            legacy.draw_character(c, "IVO", x + 10 * mm, icon_y, .48)
            draw_mini_board(c, x + card_w - 9 * mm, icon_y, 13 * mm)
        if complete:
            c.setFillColor(GREEN)
            c.setStrokeColor(WHITE)
            c.circle(x + card_w - 4 * mm, cy + card_h / 2 - 4 * mm, 4 * mm, fill=1, stroke=1)
            c.setFillColor(WHITE)
            c.setFont(base.font("bold"), 7)
            c.drawCentredString(x + card_w - 4 * mm, cy + card_h / 2 - 5.8 * mm, "OK")


def draw_recap(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    cards = (
        ("LOOK AT THE PLAN", "plan"),
        ("KEEP SOL'S TRY", "try"),
        ("FOLLOW THE CARDS", "steps"),
        ("CHECK TWO WAYS", "measure"),
        ("IVO CHECKS TOO", "ivo"),
    )
    card_w = 50 * mm
    card_h = 39 * mm
    positions = (
        (x + 31 * mm, y + h - 25 * mm),
        (x + w / 2, y + h - 25 * mm),
        (x + w - 31 * mm, y + h - 25 * mm),
        (x + w / 2 - 29 * mm, y + 24 * mm),
        (x + w / 2 + 29 * mm, y + 24 * mm),
    )
    for (label, kind), (cx, cy) in zip(cards, positions):
        c.setFillColor(PAPER)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.5)
        c.roundRect(cx - card_w / 2, cy - card_h / 2, card_w, card_h, 3 * mm, fill=1, stroke=1)
        c.setFillColor(INK)
        c.setFont(base.font("bold"), 5.2)
        c.drawCentredString(cx, cy + 13 * mm, label)
        if kind == "plan":
            draw_mini_board(c, cx, cy - 3 * mm, 19 * mm)
            pill(c, "PICTURE PLAN", cx - 17 * mm, cy - 16 * mm, 34 * mm, TEAL, 6 * mm)
        elif kind == "try":
            draw_mini_board(c, cx, cy - 3 * mm, 19 * mm)
            c.setStrokeColor(CORAL)
            c.setLineWidth(2.5)
            c.line(cx - 8 * mm, cy + 5 * mm, cx + 8 * mm, cy - 11 * mm)
        elif kind == "steps":
            for index in range(4):
                bx = cx - 15 * mm + index * 10 * mm
                c.setFillColor(WHITE)
                c.setStrokeColor(NAVY)
                c.roundRect(bx - 4 * mm, cy - 8 * mm, 8 * mm, 14 * mm, 1.5 * mm, fill=1, stroke=1)
                c.setFillColor(INK)
                c.setFont(base.font("bold"), 5)
                c.drawCentredString(bx, cy - 2 * mm, str(index + 1))
        elif kind == "measure":
            draw_mini_board(c, cx, cy - 2 * mm, 18 * mm)
            c.setStrokeColor(TEAL)
            c.setLineWidth(2.5)
            c.line(cx - 14 * mm, cy - 13 * mm, cx + 14 * mm, cy - 13 * mm)
            c.line(cx + 14 * mm, cy - 13 * mm, cx + 14 * mm, cy + 10 * mm)
        else:
            legacy.draw_character(c, "IVO", cx - 10 * mm, cy - 2 * mm, .48)
            draw_mini_board(c, cx + 10 * mm, cy - 2 * mm, 14 * mm)


def draw_page_diagram(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    number = page["page"]
    cx = x + w / 2
    cy = y + h * .53

    if number in (3, 32):
        legacy.scene_backdrop(c, x, y, w, h, gate_open=number == 32)
        if number == 3:
            pill(c, "THE REPAIRED LIGHT TRAIL", x + 8 * mm, y + h - 16 * mm, 66 * mm, PURPLE, 8 * mm)
            for index, marker in enumerate(("moon", "sun", "moon", "sun")):
                legacy.draw_marker(c, marker, x + 20 * mm + index * 14 * mm, y + 26 * mm, 4 * mm)
        else:
            draw_sign(c, x + w * .28, y + h * .54, SOURCE_MAP, "CHECKED SIGN", 62 * mm, 48 * mm)
            pill(c, "CLOSED STAR DOOR", x + w * .65, y + h * .78, 50 * mm, PURPLE, 8 * mm)
        legacy.draw_cast_row(c, page.get("cast", []), x, y + 12 * mm, w)
        return
    if number == 4:
        draw_sign(c, cx - 45 * mm, cy, SOURCE_MAP, "PICTURE PLAN", 70 * mm, 54 * mm)
        legacy.draw_arrow(c, cx - 7 * mm, cy, cx + 7 * mm, cy)
        draw_sign(c, cx + 45 * mm, cy, None, "SIGN TO REBUILD", 70 * mm, 54 * mm)
    elif number == 5:
        legacy.draw_character(c, "IVO", cx, cy, 1.8)
        pill(c, "ROUND MAGNIFYING LENS", cx - 70 * mm, cy + 26 * mm, 58 * mm, TEAL)
        pill(c, "CHECKERBOARD SATCHEL", cx + 12 * mm, cy + 26 * mm, 58 * mm, MOSS)
    elif number in (6, 7, 8):
        draw_sign(c, cx, cy + (5 * mm if number == 7 else 0), SOURCE_MAP, "PICTURE PLAN", 82 * mm, 62 * mm, {"moon"} if number == 8 else set())
        if number == 7:
            draw_choice_row(c, ["sunflower", "bee", "watering can", "boot"], cx, y + 15 * mm)
    elif number in (9, 10):
        draw_sign(c, cx - 46 * mm, cy + 8 * mm, SOURCE_MAP, "PICTURE PLAN", 62 * mm, 48 * mm)
        draw_sign(c, cx + 46 * mm, cy + 8 * mm, None, "BLANK SIGN", 62 * mm, 48 * mm)
        draw_choice_row(c, ["sunflower", "bee", "watering can", "boot"], cx, y + 13 * mm)
    elif number == 11:
        draw_sign(c, cx, cy, SOURCE_MAP, "BUILT FROM THE PLAN", 88 * mm, 66 * mm)
        pill(c, "ALL FOUR PICTURES ARE IN PLACE", cx - 43 * mm, y + 24 * mm, 86 * mm, GREEN)
    elif number == 12:
        draw_sign(c, cx - 45 * mm, cy + 6 * mm, SOURCE_MAP, "PICTURE PLAN", 66 * mm, 52 * mm, covered=True)
        draw_sign(c, cx + 45 * mm, cy + 6 * mm, None, "ANOTHER BLANK SIGN", 66 * mm, 52 * mm)
    elif number == 13:
        draw_sign(c, cx - 45 * mm, cy + 5 * mm, SOURCE_MAP, "PICTURE PLAN", 66 * mm, 50 * mm, covered=True)
        draw_sign(c, cx + 45 * mm, cy + 5 * mm, FAILED_MAP, "SOL'S FINISHED TRY", 66 * mm, 50 * mm)
        draw_choice_row(c, ["match", "does-not-match", "not-sure"], cx, y + 13 * mm, 150 * mm)
    elif number in (14, 15, 16):
        highlights = {"moon", "star"} if number == 16 else set()
        draw_sign(c, cx - 45 * mm, cy + 4 * mm, SOURCE_MAP, "PICTURE PLAN", 66 * mm, 52 * mm)
        draw_sign(c, cx + 45 * mm, cy + 4 * mm, FAILED_MAP, "SOL'S FIRST TRY - KEEP", 66 * mm, 52 * mm, highlights)
        if number == 15:
            pill(c, "POINT TO BOTH DIFFERENCES", cx - 36 * mm, y + 24 * mm, 72 * mm, PURPLE)
    elif number == 17:
        pill(c, "SOL'S FOUR STEP CARDS", cx - 38 * mm, y + h - 15 * mm, 76 * mm, TEAL, 8 * mm)
        draw_step_cards(c, cx, cy - 4 * mm)
    elif number in (18, 19):
        plan_title = "PLAN: BEE AT MOON" if number == 19 else "PICTURE PLAN"
        draw_sign(c, cx, cy + 22 * mm, SOURCE_MAP, plan_title, 58 * mm, 38 * mm)
        draw_step_cards(c, cx, cy - 13 * mm, answer=number == 19)
        if number == 18:
            draw_choice_row(c, ["step-1", "step-2", "step-3", "step-4"], cx, y + 12 * mm)
    elif number in (20, 21, 22):
        draw_measurement(c, cx, cy + 8 * mm, "SIDE TO SIDE", answer=False)
        if number == 21:
            draw_choice_row(c, ["fits", "too-wide"], cx, y + 10 * mm, 86 * mm)
        elif number == 22:
            pill(c, "BOTTOM TO TOP: NOT CHECKED YET", cx - 48 * mm, y + 7 * mm, 96 * mm, PURPLE, 8 * mm)
    elif number == 23:
        c.setFillColor(MOSS)
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.rect(cx - 2 * mm, y + 7 * mm, 4 * mm, h - 14 * mm, fill=1, stroke=1)
        draw_sign(c, cx - 49 * mm, cy - 8 * mm, SOURCE_MAP, "TEAM SIGN", 58 * mm, 44 * mm, covered=True, cover_label="TEAM SIGN COVERED")
        draw_sign(c, cx + 49 * mm, cy - 23 * mm, SOURCE_MAP, "IVO'S OWN SIGN", 58 * mm, 38 * mm)
        draw_sign(c, cx + 49 * mm, cy + 24 * mm, SOURCE_MAP, "IVO'S PICTURE PLAN", 58 * mm, 34 * mm)
        legacy.draw_character(c, "IVO", cx + 10 * mm, y + 19 * mm, .55)
    elif number in (24, 25):
        draw_sign(c, cx - 45 * mm, cy + 5 * mm, SOURCE_MAP, "TEAM SIGN", 66 * mm, 52 * mm)
        draw_sign(c, cx + 45 * mm, cy + 5 * mm, SOURCE_MAP, "IVO'S OWN SIGN", 66 * mm, 52 * mm)
        if number == 24:
            draw_choice_row(c, ["same", "different"], cx, y + 10 * mm, 92 * mm)
        else:
            pill(c, "ALL FOUR PICTURES MATCH", cx - 40 * mm, y + 24 * mm, 80 * mm, GREEN)
    elif number == 26:
        pill(c, "MIA: WIDTH FITS. ARE WE DONE?", cx - 72 * mm, cy + 34 * mm, 68 * mm, PURPLE, 11 * mm)
        pill(c, "IVO: WHAT ABOUT BOTTOM TO TOP?", cx + 4 * mm, cy + 34 * mm, 68 * mm, MOSS, 11 * mm)
        draw_sign(c, cx, cy - 12 * mm, SOURCE_MAP, "REPAIRED SIGN", 68 * mm, 50 * mm)
        pill(c, "WIDTH: FITS", cx - 24 * mm, cy + 22 * mm, 48 * mm, GREEN, 8 * mm)
        draw_choice_row(c, ["guess", "vote", "measure-bottom-to-top"], cx, y + 10 * mm, 150 * mm)
    elif number == 27:
        draw_measurement(c, cx - 11 * mm, cy + 4 * mm, "BOTTOM TO TOP", answer=False)
        pill(c, "MEASURING ANSWERED THE QUESTION", cx - 47 * mm, y + 24 * mm, 94 * mm, GREEN)
    elif number in (28, 29, 30):
        draw_check_cards(c, cx, cy + 3 * mm, complete=number == 30)
        if number == 29:
            pill(c, "MATCH EACH QUESTION TO ONE CARD", cx - 48 * mm, y + 19 * mm, 96 * mm, PURPLE, 8 * mm)
        elif number == 30:
            pill(c, "GATE OPEN", cx - 28 * mm, y + 19 * mm, 56 * mm, GREEN)
    elif number == 31:
        draw_recap(c, x, y, w, h)
    elif number == 2:
        draw_sign(c, cx, cy, SOURCE_MAP, "LIVE REVIEW 1.0.1", 82 * mm, 62 * mm)
    else:
        draw_sign(c, cx, cy, SOURCE_MAP, "GARDEN WELCOME SIGN", 82 * mm, 62 * mm)

    interactive_pages = {7, 9, 10, 13, 17, 18, 19, 20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31}
    if number not in interactive_pages:
        legacy.draw_cast_row(c, page.get("cast", []), x, y + 9 * mm, w)


def draw_cover(c: canvas.Canvas, page: dict) -> None:
    legacy.scene_backdrop(c, 0, 0, PAGE, PAGE, gate_open=False)
    c.setFillColor(colors.Color(.02, .05, .10, alpha=.40))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    pill(c, page["badge"], 18 * mm, PAGE - 24 * mm, 174 * mm, GOLD, 10 * mm)
    base.paragraph_in_box(c, page["text"], 14 * mm, 145 * mm, 182 * mm, 37 * mm, 35, 25, WHITE)
    base.paragraph_in_box(c, page["subtext"], 22 * mm, 130 * mm, 166 * mm, 13 * mm, 17, 11, GOLD, bold=False)
    draw_sign(c, PAGE / 2, 80 * mm, SOURCE_MAP, "GARDEN WELCOME SIGN", 94 * mm, 68 * mm)
    legacy.draw_cast_row(c, page.get("cast", []), 15 * mm, 22 * mm, PAGE - 30 * mm)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 8.5)
    c.drawString(16 * mm, 8 * mm, "Maria Smith - Review edition 1.0.1")


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']} - {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years checking story and activity book, review 1.0.1")
    c.setKeywords("Smithian Fold Theory, early years, step cards, checking, measurement boundary, independent check")
    for page in book["pages"]:
        if page["kind"] == "cover":
            draw_cover(c, page)
        else:
            c.setFillColor(CREAM)
            c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
            badge_fill = GREEN if page["kind"] in ("reveal", "result", "summary", "end") else PURPLE if page["kind"] == "challenge" else TEAL
            pill(c, page["badge"], 15 * mm, PAGE - 23 * mm, 180 * mm, badge_fill, 10 * mm)
            if page["kind"] == "legal":
                base.paragraph_in_box(c, page["text"], 20 * mm, 145 * mm, 170 * mm, 42 * mm, 12, 8, INK, bold=False)
            else:
                base.paragraph_in_box(c, page["text"], 17 * mm, 148 * mm, 176 * mm, 38 * mm, 18.5, 11.2, INK)
            base.paragraph_in_box(c, page["subtext"], 21 * mm, 127 * mm, 168 * mm, 17 * mm, 10.5, 7, GREY, bold=False)
            art_x, art_y, art_w, art_h = 14 * mm, 15 * mm, 182 * mm, 108 * mm
            c.setFillColor(NAVY)
            c.roundRect(art_x - 1.5 * mm, art_y - 1.5 * mm, art_w + 3 * mm, art_h + 3 * mm, 7 * mm, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#204560"))
            c.roundRect(art_x, art_y, art_w, art_h, 5.8 * mm, fill=1, stroke=0)
            draw_page_diagram(c, page, art_x, art_y, art_w, art_h)
            # These pages label their concrete cards and mini-scenes directly;
            # repeating the JSON label strip would crowd the same illustrations.
            if page["page"] not in {19, 23, 28, 29, 30, 31}:
                legacy.draw_scene_labels(c, page.get("labels", []), art_x + 3 * mm, art_y + art_h - 9 * mm, art_w - 6 * mm)
            if page.get("code"):
                c.saveState()
                c.translate(art_x + art_w - 15 * mm, art_y + 6 * mm)
                c.rotate(-6)
                c.setFillColor(CREAM)
                c.setFont(base.font("bold"), 4.2)
                c.drawCentredString(0, 0, page["code"])
                c.restoreState()
            c.setFillColor(GREY)
            c.setFont(base.font("regular"), 7.5)
            c.drawRightString(PAGE - 7 * mm, 6 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 6, 9, 12, 15, 17, 20, 23, 26, 28, 31):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E04 Adult Guide - Review version 1.0.1")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=19 * mm, bottomMargin=20 * mm,
        title="Adult Guide - E04 - Review 1.0.1", author="Maria Smith",
    )
    story = base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    doc.build(story, onFirstPage=adult_footer, onLaterPages=adult_footer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-only", action="store_true")
    parser.add_argument("--adult-only", action="store_true")
    args = parser.parse_args()
    base.register_fonts()
    book = load_book()
    if not args.adult_only:
        render_student(book)
        generate_accessible_e04_v1_0_1.main()
    if not args.student_only:
        render_adult()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(generate_accessible_e04_v1_0_1.OUTPUT)


if __name__ == "__main__":
    main()
