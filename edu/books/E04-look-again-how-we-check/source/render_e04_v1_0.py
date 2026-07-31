#!/usr/bin/env python3
"""Render the complete E04 review edition 1.0.0 from canonical sources."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "E01-something-is-here" / "source"))
import render_e01 as base

import generate_accessible_e04


BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.0.json"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"
RELEASE_DIR = BOOK_DIR / "editions" / "1.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E04-Look-Again-How-We-Check-v1.0.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E04-Adult-Guide-v1.0.0.pdf"

PAGE = 210 * mm
NAVY = colors.HexColor("#14243E")
INK = colors.HexColor("#20314A")
CREAM = colors.HexColor("#FFF9EA")
PAPER = colors.HexColor("#FFFDF5")
GOLD = colors.HexColor("#FFD35C")
GREEN = colors.HexColor("#2C765C")
MOSS = colors.HexColor("#6F984A")
TEAL = colors.HexColor("#4FB9B3")
BLUE = colors.HexColor("#61C4E5")
PURPLE = colors.HexColor("#75529A")
CORAL = colors.HexColor("#E97464")
WOOD = colors.HexColor("#A66A3D")
DARK_WOOD = colors.HexColor("#633E2B")
GREY = colors.HexColor("#5B6678")
WHITE = colors.white

SOURCE_MAP = {
    "sun": "sunflower",
    "moon": "bee",
    "leaf": "watering can",
    "star": "boot",
}
FAILED_MAP = {
    "sun": "sunflower",
    "moon": "boot",
    "leaf": "watering can",
    "star": "bee",
}
MARKER_ORDER = ("sun", "moon", "leaf", "star")
DISPLAY = {
    "sunflower": "SUNFLOWER",
    "bee": "BEE",
    "watering can": "WATERING CAN",
    "boot": "BOOT",
}


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if len(pages) != 32 or [page["page"] for page in pages] != list(range(1, 33)):
        raise ValueError("E04 1.0.0 must contain exactly 32 ordered pages")
    return book


def pill(c: canvas.Canvas, text: str, x: float, y: float, w: float, fill: colors.Color, h: float = 9 * mm) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, h / 2, fill=1, stroke=1)
    color = NAVY if fill in (GOLD, CREAM, PAPER, BLUE) else WHITE
    base.paragraph_in_box(c, text, x + 2 * mm, y + 1.1 * mm, w - 4 * mm, h - 2.2 * mm, 7.6, 4.5, color)


def draw_marker(c: canvas.Canvas, marker: str, cx: float, cy: float, r: float = 3.4 * mm) -> None:
    c.saveState()
    c.setStrokeColor(NAVY)
    c.setFillColor({"sun": GOLD, "moon": BLUE, "leaf": MOSS, "star": PURPLE}[marker])
    c.setLineWidth(1)
    if marker == "sun":
        c.circle(cx, cy, r * .46, fill=1, stroke=1)
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            c.line(cx + math.cos(a) * r * .62, cy + math.sin(a) * r * .62,
                   cx + math.cos(a) * r, cy + math.sin(a) * r)
    elif marker == "moon":
        c.circle(cx, cy, r, fill=1, stroke=1)
        c.setFillColor(PAPER)
        c.setStrokeColor(PAPER)
        c.circle(cx + r * .38, cy + r * .18, r * .82, fill=1, stroke=0)
    elif marker == "leaf":
        path = c.beginPath()
        path.moveTo(cx, cy + r)
        path.curveTo(cx + r, cy + r * .4, cx + r * .8, cy - r * .7, cx, cy - r)
        path.curveTo(cx - r * .8, cy - r * .7, cx - r, cy + r * .4, cx, cy + r)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        c.line(cx, cy - r * .75, cx, cy + r * .7)
    else:
        path = c.beginPath()
        for i in range(10):
            a = math.radians(90 + i * 36)
            rr = r if i % 2 == 0 else r * .42
            px, py = cx + math.cos(a) * rr, cy + math.sin(a) * rr
            path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
    c.restoreState()


def draw_picture(c: canvas.Canvas, item: str, cx: float, cy: float, scale: float = 1.0) -> None:
    c.saveState()
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.4)
    if item == "sunflower":
        c.setStrokeColor(MOSS)
        c.setLineWidth(2.2 * scale)
        c.line(cx, cy - 9 * mm * scale, cx, cy + 2 * mm * scale)
        c.setFillColor(MOSS)
        c.ellipse(cx - 7 * mm * scale, cy - 4 * mm * scale, cx, cy + 1 * mm * scale, fill=1, stroke=0)
        c.ellipse(cx, cy - 1 * mm * scale, cx + 7 * mm * scale, cy + 4 * mm * scale, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setStrokeColor(DARK_WOOD)
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            px, py = cx + math.cos(a) * 5 * mm * scale, cy + 8 * mm * scale + math.sin(a) * 5 * mm * scale
            c.circle(px, py, 3.2 * mm * scale, fill=1, stroke=1)
        c.setFillColor(DARK_WOOD)
        c.circle(cx, cy + 8 * mm * scale, 3.8 * mm * scale, fill=1, stroke=1)
    elif item == "bee":
        c.setFillColor(WHITE)
        c.setStrokeColor(BLUE)
        c.ellipse(cx - 10 * mm * scale, cy + 1 * mm * scale, cx - 1 * mm * scale, cy + 10 * mm * scale, fill=1, stroke=1)
        c.ellipse(cx + 1 * mm * scale, cy + 1 * mm * scale, cx + 10 * mm * scale, cy + 10 * mm * scale, fill=1, stroke=1)
        c.setFillColor(GOLD)
        c.setStrokeColor(NAVY)
        c.ellipse(cx - 10 * mm * scale, cy - 6 * mm * scale, cx + 10 * mm * scale, cy + 6 * mm * scale, fill=1, stroke=1)
        c.setStrokeColor(NAVY)
        c.setLineWidth(2.2 * scale)
        c.line(cx - 4 * mm * scale, cy - 5 * mm * scale, cx - 4 * mm * scale, cy + 5 * mm * scale)
        c.line(cx + 3 * mm * scale, cy - 5.5 * mm * scale, cx + 3 * mm * scale, cy + 5.5 * mm * scale)
        c.setFillColor(NAVY)
        c.circle(cx + 7 * mm * scale, cy + 1.5 * mm * scale, 1.1 * mm * scale, fill=1, stroke=0)
    elif item == "watering can":
        c.setFillColor(TEAL)
        c.setStrokeColor(NAVY)
        c.roundRect(cx - 10 * mm * scale, cy - 8 * mm * scale, 18 * mm * scale, 15 * mm * scale, 2 * mm * scale, fill=1, stroke=1)
        c.setLineWidth(2 * scale)
        c.arc(cx - 5 * mm * scale, cy, cx + 12 * mm * scale, cy + 16 * mm * scale, 5, 170)
        spout = c.beginPath()
        spout.moveTo(cx - 10 * mm * scale, cy + 4 * mm * scale)
        spout.lineTo(cx - 20 * mm * scale, cy + 10 * mm * scale)
        spout.lineTo(cx - 18 * mm * scale, cy + 14 * mm * scale)
        spout.lineTo(cx - 8 * mm * scale, cy + 7 * mm * scale)
        spout.close()
        c.drawPath(spout, fill=1, stroke=1)
        c.line(cx - 20 * mm * scale, cy + 10 * mm * scale, cx - 23 * mm * scale, cy + 9 * mm * scale)
    elif item == "boot":
        c.setFillColor(CORAL)
        c.setStrokeColor(NAVY)
        path = c.beginPath()
        path.moveTo(cx - 7 * mm * scale, cy + 12 * mm * scale)
        path.lineTo(cx + 6 * mm * scale, cy + 12 * mm * scale)
        path.lineTo(cx + 4 * mm * scale, cy - 2 * mm * scale)
        path.curveTo(cx + 8 * mm * scale, cy - 4 * mm * scale, cx + 14 * mm * scale, cy - 5 * mm * scale, cx + 15 * mm * scale, cy - 9 * mm * scale)
        path.lineTo(cx + 15 * mm * scale, cy - 13 * mm * scale)
        path.lineTo(cx - 8 * mm * scale, cy - 13 * mm * scale)
        path.close()
        c.drawPath(path, fill=1, stroke=1)
        c.setFillColor(GOLD)
        c.rect(cx - 8 * mm * scale, cy - 13 * mm * scale, 23 * mm * scale, 3 * mm * scale, fill=1, stroke=1)
    c.restoreState()


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
) -> None:
    highlighted = highlighted or set()
    c.saveState()
    c.setFillColor(DARK_WOOD)
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
    for marker in MARKER_ORDER:
        px, py = positions[marker]
        c.setFillColor(PAPER)
        c.setStrokeColor(CORAL if marker in highlighted else colors.HexColor("#D9CDAA"))
        c.setLineWidth(3 if marker in highlighted else 1)
        c.roundRect(px - cell_w / 2, py - cell_h / 2, cell_w, cell_h, 2.2 * mm, fill=1, stroke=1)
        draw_marker(c, marker, px - cell_w / 2 + 4 * mm, py + cell_h / 2 - 4 * mm, 2.4 * mm)
        if mapping:
            item = mapping[marker]
            c.setFillColor(INK)
            c.setFont(base.font("bold"), 5.1)
            c.drawCentredString(px, py + cell_h / 2 - 5.4 * mm, DISPLAY[item])
            draw_picture(c, item, px, py - 3 * mm, .58)
        else:
            c.setFillColor(colors.HexColor("#E8E0CB"))
            c.setFont(base.font("bold"), 18)
            c.drawCentredString(px, py - 2 * mm, "?")
    if covered:
        c.setFillColor(colors.Color(MOSS.red, MOSS.green, MOSS.blue, alpha=.96))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(cx - width / 2 + 2 * mm, cy - height / 2 + 2 * mm, width - 4 * mm, height - 4 * mm, 4 * mm, fill=1, stroke=1)
        for row in range(4):
            for col in range(7):
                draw_marker(c, "leaf", cx - 30 * mm + col * 10 * mm, cy - 19 * mm + row * 13 * mm, 2.4 * mm)
        c.setFillColor(WHITE)
        c.setFont(base.font("bold"), 8)
        c.drawCentredString(cx, cy, "SOURCE COVERED")
    c.restoreState()


def draw_choice_row(c: canvas.Canvas, items: list[str], cx: float, cy: float, width: float = 150 * mm) -> None:
    gap = 3 * mm
    cell = (width - gap * (len(items) - 1)) / len(items)
    start = cx - width / 2
    for index, item in enumerate(items):
        x = start + index * (cell + gap)
        c.setFillColor(PAPER)
        c.setStrokeColor(WHITE)
        c.setLineWidth(1.5)
        c.roundRect(x, cy - 11 * mm, cell, 22 * mm, 3 * mm, fill=1, stroke=1)
        label = DISPLAY.get(item, item.replace("-", " ").upper())
        if item in DISPLAY:
            draw_picture(c, item, x + cell / 2, cy - 1 * mm, .38)
            c.setFillColor(INK)
            c.setFont(base.font("bold"), 4.4)
            c.drawCentredString(x + cell / 2, cy + 7 * mm, label)
        else:
            base.paragraph_in_box(c, label, x + 2 * mm, cy - 8 * mm, cell - 4 * mm, 16 * mm, 7, 4.5, INK)


def draw_character(c: canvas.Canvas, name: str, cx: float, cy: float, scale: float = 1.0) -> None:
    c.saveState()
    if name == "MIA":
        c.setFillColor(colors.HexColor("#E6A16B"))
        c.setStrokeColor(NAVY)
        c.circle(cx, cy + 8 * mm * scale, 6 * mm * scale, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#2C2A39"))
        c.wedge(cx - 7 * mm * scale, cy + 3 * mm * scale, cx + 7 * mm * scale, cy + 17 * mm * scale, 0, 180, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.roundRect(cx - 6 * mm * scale, cy - 8 * mm * scale, 12 * mm * scale, 12 * mm * scale, 3 * mm * scale, fill=1, stroke=1)
    else:
        fill = BLUE if name == "TAVI" else GOLD if name == "SOL" else MOSS
        c.setFillColor(fill)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.3)
        c.roundRect(cx - 7 * mm * scale, cy - 7 * mm * scale, 14 * mm * scale, 17 * mm * scale, 6 * mm * scale, fill=1, stroke=1)
        if name == "SOL":
            for dx in (-4, 0, 4):
                p = c.beginPath(); p.moveTo(cx + dx * mm * scale, cy + 10 * mm * scale); p.lineTo(cx + (dx + 2) * mm * scale, cy + 16 * mm * scale); p.lineTo(cx + (dx + 4) * mm * scale, cy + 10 * mm * scale); p.close(); c.drawPath(p, fill=1, stroke=1)
        else:
            c.line(cx - 4 * mm * scale, cy + 10 * mm * scale, cx - 5 * mm * scale, cy + 16 * mm * scale)
            c.line(cx + 4 * mm * scale, cy + 10 * mm * scale, cx + 5 * mm * scale, cy + 16 * mm * scale)
        if name == "IVO":
            c.setStrokeColor(NAVY)
            c.setLineWidth(2)
            c.circle(cx + 8 * mm * scale, cy + 6 * mm * scale, 4 * mm * scale, fill=0, stroke=1)
            c.line(cx + 11 * mm * scale, cy + 3 * mm * scale, cx + 15 * mm * scale, cy - 1 * mm * scale)
            c.setFillColor(PAPER)
            c.setStrokeColor(NAVY)
            c.rect(cx - 10 * mm * scale, cy - 5 * mm * scale, 5 * mm * scale, 8 * mm * scale, fill=1, stroke=1)
            c.setFillColor(NAVY)
            for rr in range(2):
                for cc in range(2):
                    if (rr + cc) % 2 == 0:
                        c.rect(cx - 10 * mm * scale + cc * 2.5 * mm * scale, cy - 5 * mm * scale + rr * 4 * mm * scale, 2.5 * mm * scale, 4 * mm * scale, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.circle(cx - 2.5 * mm * scale, cy + 4 * mm * scale, .8 * mm * scale, fill=1, stroke=0)
        c.circle(cx + 2.5 * mm * scale, cy + 4 * mm * scale, .8 * mm * scale, fill=1, stroke=0)
    c.setFillColor(PAPER)
    c.setStrokeColor(NAVY)
    c.roundRect(cx - 9 * mm * scale, cy - 13 * mm * scale, 18 * mm * scale, 6 * mm * scale, 3 * mm * scale, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(base.font("bold"), 4.6 * scale)
    c.drawCentredString(cx, cy - 11 * mm * scale, name)
    c.restoreState()


def scene_backdrop(c: canvas.Canvas, x: float, y: float, w: float, h: float, gate_open: bool = False) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#173252"))
    c.roundRect(x, y, w, h, 6 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#315D46"))
    c.rect(x, y, w, h * .34, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#D8B46B"))
    path = c.beginPath()
    path.moveTo(x + w * .42, y)
    path.lineTo(x + w * .58, y)
    path.lineTo(x + w * .68, y + h * .34)
    path.lineTo(x + w * .32, y + h * .34)
    path.close(); c.drawPath(path, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#497955"))
    for dx, dy, rr in ((.05, .25, .12), (.14, .46, .10), (.86, .42, .11), (.94, .23, .13)):
        c.circle(x + w * dx, y + h * dy, w * rr, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(4)
    gx = x + w * .5
    gy = y + h * .68
    c.line(gx - 28 * mm, y + h * .34, gx - 28 * mm, y + h * .92)
    c.line(gx + 28 * mm, y + h * .34, gx + 28 * mm, y + h * .92)
    c.arc(gx - 28 * mm, y + h * .66, gx + 28 * mm, y + h * 1.08, 0, 180)
    if not gate_open:
        for index in range(6):
            px = gx - 24 * mm + index * 9.6 * mm
            c.setStrokeColor(DARK_WOOD); c.setLineWidth(4)
            c.line(px, y + h * .35, px, y + h * .83)
        c.line(gx - 25 * mm, y + h * .55, gx + 25 * mm, y + h * .55)
    else:
        c.setFillColor(colors.HexColor("#8FD6ED"))
        c.rect(gx - 24 * mm, y + h * .35, 48 * mm, h * .42, fill=1, stroke=0)
        c.setStrokeColor(GOLD); c.setLineWidth(2)
        for index in range(3):
            c.arc(gx - 18 * mm + index * 10 * mm, y + h * .45, gx + index * 10 * mm, y + h * .70, 0, 180)
    c.restoreState()


def draw_cast_row(c: canvas.Canvas, cast: list[str], x: float, y: float, w: float) -> None:
    names = [name.upper() for name in cast]
    if not names:
        return
    spacing = min(34 * mm, w / max(1, len(names)))
    total = spacing * (len(names) - 1)
    start = x + w / 2 - total / 2
    for index, name in enumerate(names):
        draw_character(c, name, start + index * spacing, y, .72)


def draw_arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, fill: colors.Color = GOLD) -> None:
    c.saveState()
    c.setStrokeColor(fill); c.setFillColor(fill); c.setLineWidth(2)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 4 * mm
    p = c.beginPath(); p.moveTo(x2, y2)
    p.lineTo(x2 - size * math.cos(angle - .55), y2 - size * math.sin(angle - .55))
    p.lineTo(x2 - size * math.cos(angle + .55), y2 - size * math.sin(angle + .55))
    p.close(); c.drawPath(p, fill=1, stroke=0); c.restoreState()


def draw_trace(c: canvas.Canvas, cx: float, cy: float, answer: bool = False) -> None:
    steps = (("sunflower", "SUN"), ("watering can", "LEAF"), ("boot", "MOON"), ("bee", "STAR"))
    gap = 35 * mm
    start = cx - gap * 1.5
    for index, (item, corner) in enumerate(steps, start=1):
        x = start + (index - 1) * gap
        c.setFillColor(PAPER); c.setStrokeColor(CORAL if answer and index == 3 else GOLD); c.setLineWidth(3 if answer and index == 3 else 1.5)
        c.roundRect(x - 15 * mm, cy - 17 * mm, 30 * mm, 34 * mm, 3 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(base.font("bold"), 5.4); c.drawCentredString(x, cy + 11 * mm, f"STEP {index}")
        draw_picture(c, item, x, cy - 1 * mm, .36)
        c.setFont(base.font("bold"), 4.5); c.drawCentredString(x, cy - 12 * mm, f"TO {corner}")
        if index < 4:
            draw_arrow(c, x + 16 * mm, cy, x + gap - 16 * mm, cy)
    if answer:
        pill(c, "FIRST CHANGE", start + gap * 2 - 16 * mm, cy + 21 * mm, 32 * mm, CORAL, 7 * mm)


def draw_measurement(c: canvas.Canvas, cx: float, cy: float, dimension: str, answer: bool = False) -> None:
    draw_sign(c, cx, cy, SOURCE_MAP, "REPAIRED SIGN", 70 * mm, 52 * mm)
    c.saveState(); c.setStrokeColor(TEAL); c.setFillColor(TEAL); c.setLineWidth(4)
    if dimension == "WIDTH":
        y = cy - 33 * mm
        c.line(cx - 35 * mm, y, cx + 35 * mm, y)
        c.line(cx - 35 * mm, y - 5 * mm, cx - 35 * mm, y + 5 * mm)
        c.line(cx + 35 * mm, y - 5 * mm, cx + 35 * mm, y + 5 * mm)
        pill(c, "WIDTH RIBBON", cx - 23 * mm, y - 12 * mm, 46 * mm, TEAL, 7 * mm)
    else:
        x = cx + 48 * mm
        c.line(x, cy - 26 * mm, x, cy + 26 * mm)
        c.line(x - 5 * mm, cy - 26 * mm, x + 5 * mm, cy - 26 * mm)
        c.line(x - 5 * mm, cy + 26 * mm, x + 5 * mm, cy + 26 * mm)
        pill(c, "HEIGHT", x - 17 * mm, cy - 4 * mm, 34 * mm, TEAL, 7 * mm)
    c.restoreState()
    if answer:
        pill(c, f"{dimension}: FITS", cx - 25 * mm, cy + 37 * mm, 50 * mm, GREEN, 8 * mm)


def draw_checkpoints(c: canvas.Canvas, cx: float, cy: float, complete: bool = False) -> None:
    labels = ("PICTURES", "WIDTH", "HEIGHT", "FRIEND CHECK")
    fills = (GOLD, TEAL, BLUE, MOSS)
    start = cx - 63 * mm
    for index, (label, fill) in enumerate(zip(labels, fills)):
        x = start + index * 42 * mm
        c.setFillColor(PAPER); c.setStrokeColor(fill); c.setLineWidth(2)
        c.roundRect(x - 17 * mm, cy - 18 * mm, 34 * mm, 36 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(base.font("bold"), 5.2); c.drawCentredString(x, cy + 10 * mm, label)
        c.setFont(base.font("bold"), 22); c.setFillColor(GREEN if complete else GREY); c.drawCentredString(x, cy - 6 * mm, "OK" if complete else "?")
        if index < 3:
            draw_arrow(c, x + 18 * mm, cy, x + 24 * mm, cy, GOLD)


def draw_scene_labels(c: canvas.Canvas, labels: list[str], x: float, y: float, w: float) -> None:
    if not labels:
        return
    labels = labels[:5]
    gap = 2 * mm
    cell = (w - gap * (len(labels) - 1)) / len(labels)
    for index, label in enumerate(labels):
        pill(c, label, x + index * (cell + gap), y, cell, GOLD, 8 * mm)


def draw_page_diagram(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    number = page["page"]
    cx = x + w / 2
    cy = y + h * .53
    if number in (3, 32):
        scene_backdrop(c, x, y, w, h, gate_open=number == 32)
        if number == 3:
            pill(c, "THE REPAIRED LIGHT TRAIL", x + 8 * mm, y + h - 16 * mm, 66 * mm, PURPLE, 8 * mm)
            for index, marker in enumerate(("moon", "sun", "moon", "sun")):
                draw_marker(c, marker, x + 20 * mm + index * 14 * mm, y + 26 * mm, 4 * mm)
        else:
            draw_sign(c, x + w * .28, y + h * .54, SOURCE_MAP, "CHECKED SIGN", 62 * mm, 48 * mm)
            pill(c, "NEXT STAR DOOR", x + w * .66, y + h * .78, 48 * mm, PURPLE, 8 * mm)
        draw_cast_row(c, page.get("cast", []), x, y + 12 * mm, w)
        return
    if number in (4,):
        draw_sign(c, cx - 45 * mm, cy, SOURCE_MAP, "PICTURE PLAN", 70 * mm, 54 * mm)
        draw_arrow(c, cx - 7 * mm, cy, cx + 7 * mm, cy)
        draw_sign(c, cx + 45 * mm, cy, None, "SIGN TO REBUILD", 70 * mm, 54 * mm)
    elif number == 5:
        draw_character(c, "IVO", cx, cy, 1.8)
        pill(c, "ROUND MAGNIFYING LENS", cx - 70 * mm, cy + 26 * mm, 58 * mm, TEAL)
        pill(c, "CHECKERBOARD SATCHEL", cx + 12 * mm, cy + 26 * mm, 58 * mm, MOSS)
    elif number in (6, 7, 8):
        draw_sign(c, cx, cy + (5 * mm if number == 7 else 0), SOURCE_MAP, "SHOWN SOURCE PLAN", 82 * mm, 62 * mm, {"moon"} if number == 8 else set())
        if number == 7:
            draw_choice_row(c, ["sunflower", "bee", "watering can", "boot"], cx, y + 15 * mm)
    elif number in (9, 10):
        draw_sign(c, cx - 46 * mm, cy + 8 * mm, SOURCE_MAP, "SOURCE", 62 * mm, 48 * mm)
        draw_sign(c, cx + 46 * mm, cy + 8 * mm, None, "BLANK SIGN", 62 * mm, 48 * mm)
        draw_choice_row(c, ["sunflower", "bee", "watering can", "boot"], cx, y + 13 * mm)
    elif number == 11:
        draw_sign(c, cx, cy, SOURCE_MAP, "BUILT FROM SOURCE", 88 * mm, 66 * mm)
        pill(c, "ALL FOUR PICTURES USED ONCE", cx - 40 * mm, y + 24 * mm, 80 * mm, GREEN)
    elif number == 12:
        draw_sign(c, cx - 45 * mm, cy + 6 * mm, SOURCE_MAP, "SOURCE", 66 * mm, 52 * mm, covered=True)
        draw_sign(c, cx + 45 * mm, cy + 6 * mm, None, "FRESH SIGN", 66 * mm, 52 * mm)
    elif number == 13:
        draw_sign(c, cx - 45 * mm, cy + 4 * mm, SOURCE_MAP, "SOURCE", 66 * mm, 52 * mm, covered=True)
        draw_sign(c, cx + 45 * mm, cy + 4 * mm, FAILED_MAP, "SOL'S MEMORY REBUILD", 66 * mm, 52 * mm)
        draw_choice_row(c, ["match", "not-sure"], cx, y + 13 * mm, 86 * mm)
    elif number in (14, 15, 16):
        highlights = {"moon", "star"} if number == 16 else set()
        draw_sign(c, cx - 45 * mm, cy + 4 * mm, SOURCE_MAP, "SOURCE", 66 * mm, 52 * mm)
        draw_sign(c, cx + 45 * mm, cy + 4 * mm, FAILED_MAP, "FIRST REBUILD - KEEP", 66 * mm, 52 * mm, highlights)
        if number == 15:
            pill(c, "POINT TO EVERY DIFFERENCE", cx - 35 * mm, y + 24 * mm, 70 * mm, PURPLE)
    elif number in (17, 18, 19):
        draw_trace(c, cx, cy + 4 * mm, answer=number == 19)
        if number == 18:
            draw_choice_row(c, ["step-1", "step-2", "step-3", "step-4"], cx, y + 12 * mm)
    elif number in (20, 21, 22):
        draw_measurement(c, cx, cy + 7 * mm, "WIDTH", answer=number == 22)
        if number == 21:
            draw_choice_row(c, ["fits", "too-wide"], cx, y + 10 * mm, 86 * mm)
    elif number == 23:
        c.setFillColor(MOSS); c.setStrokeColor(GOLD); c.setLineWidth(2)
        c.rect(cx - 3 * mm, y + 7 * mm, 6 * mm, h - 14 * mm, fill=1, stroke=1)
        draw_sign(c, cx - 49 * mm, cy, SOURCE_MAP, "TEAM SIGN COVERED", 66 * mm, 52 * mm, covered=True)
        draw_sign(c, cx + 49 * mm, cy, SOURCE_MAP, "IVO'S FRESH CHECK", 66 * mm, 52 * mm)
    elif number in (24, 25):
        draw_sign(c, cx - 45 * mm, cy + 5 * mm, SOURCE_MAP, "TEAM SIGN", 66 * mm, 52 * mm)
        draw_sign(c, cx + 45 * mm, cy + 5 * mm, SOURCE_MAP, "IVO'S CHECK", 66 * mm, 52 * mm)
        if number == 24:
            draw_choice_row(c, ["confirm", "disagree"], cx, y + 10 * mm, 86 * mm)
        else:
            pill(c, "FOUR MATCHES - CONFIRMED", cx - 42 * mm, y + 24 * mm, 84 * mm, GREEN)
    elif number == 26:
        pill(c, "MIA'S CLAIM: WHOLE SIGN FITS", cx - 73 * mm, cy + 34 * mm, 68 * mm, PURPLE, 11 * mm)
        pill(c, "IVO'S CHECK: HEIGHT NOT CHECKED", cx + 5 * mm, cy + 34 * mm, 68 * mm, MOSS, 11 * mm)
        draw_measurement(c, cx, cy - 12 * mm, "WIDTH", answer=True)
        draw_choice_row(c, ["guess", "vote", "check-height"], cx, y + 10 * mm, 126 * mm)
    elif number == 27:
        draw_measurement(c, cx - 12 * mm, cy + 4 * mm, "HEIGHT", answer=True)
        pill(c, "MORE WORK ANSWERED THE MISSING QUESTION", cx - 54 * mm, y + 24 * mm, 108 * mm, GREEN)
    elif number in (28, 29, 30):
        draw_checkpoints(c, cx, cy + 8 * mm, complete=number == 30)
        if number == 29:
            draw_choice_row(c, ["source comparison", "width record", "height record", "friend check"], cx, y + 11 * mm, 158 * mm)
        elif number == 30:
            pill(c, "GATE OPEN", cx - 28 * mm, y + 24 * mm, 56 * mm, GREEN)
    elif number == 31:
        actions = (("OBSERVE", "bee"), ("KEEP TRY", "boot"), ("TRACE", "watering can"), ("MEASURE", "sunflower"))
        start = cx - 60 * mm
        for index, (label, item) in enumerate(actions):
            px = start + index * 40 * mm
            c.setFillColor(PAPER); c.setStrokeColor(GOLD); c.setLineWidth(2)
            c.roundRect(px - 16 * mm, cy - 18 * mm, 32 * mm, 36 * mm, 4 * mm, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont(base.font("bold"), 5.4); c.drawCentredString(px, cy + 11 * mm, label)
            draw_picture(c, item, px, cy - 3 * mm, .42)
        pill(c, "ASK A FRIEND BY A FRESH PATH", cx - 45 * mm, y + 24 * mm, 90 * mm, MOSS)
    elif number == 2:
        draw_sign(c, cx, cy, SOURCE_MAP, "LIVE REVIEW 1.0.0", 82 * mm, 62 * mm)
    else:
        draw_sign(c, cx, cy, SOURCE_MAP, "GARDEN WELCOME SIGN", 82 * mm, 62 * mm)

    # Keep touch choices, measurement edges and evidence cards completely clear.
    # The cast remains visible on the story and reveal pages surrounding these
    # interaction boards, so no character badge is allowed to cover a control.
    if number not in {7, 9, 10, 13, 18, 20, 21, 22, 24, 26, 29}:
        draw_cast_row(c, page.get("cast", []), x, y + 9 * mm, w)


def draw_cover(c: canvas.Canvas, page: dict) -> None:
    scene_backdrop(c, 0, 0, PAGE, PAGE, gate_open=False)
    c.setFillColor(colors.Color(.02, .05, .10, alpha=.40)); c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    pill(c, page["badge"], 18 * mm, PAGE - 24 * mm, 174 * mm, GOLD, 10 * mm)
    base.paragraph_in_box(c, page["text"], 14 * mm, 145 * mm, 182 * mm, 37 * mm, 35, 25, WHITE)
    base.paragraph_in_box(c, page["subtext"], 22 * mm, 130 * mm, 166 * mm, 13 * mm, 17, 11, GOLD, bold=False)
    draw_sign(c, PAGE / 2, 80 * mm, SOURCE_MAP, "GARDEN WELCOME SIGN", 94 * mm, 68 * mm)
    draw_cast_row(c, page.get("cast", []), 15 * mm, 22 * mm, PAGE - 30 * mm)
    c.setFillColor(WHITE); c.setFont(base.font("bold"), 8.5); c.drawString(16 * mm, 8 * mm, "Maria Smith - Review edition 1.0.0")


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']} - {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years checking story and activity book, review 1.0.0")
    c.setKeywords("Smithian Fold Theory, early years, trace, checking, measurement boundary, independent check")
    for page in book["pages"]:
        if page["kind"] == "cover":
            draw_cover(c, page)
        else:
            c.setFillColor(CREAM); c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
            badge_fill = GREEN if page["kind"] in ("reveal", "result", "summary", "end") else PURPLE if page["kind"] == "challenge" else TEAL
            pill(c, page["badge"], 15 * mm, PAGE - 23 * mm, 180 * mm, badge_fill, 10 * mm)
            if page["kind"] == "legal":
                base.paragraph_in_box(c, page["text"], 20 * mm, 145 * mm, 170 * mm, 42 * mm, 12, 8, INK, bold=False)
            else:
                base.paragraph_in_box(c, page["text"], 17 * mm, 148 * mm, 176 * mm, 38 * mm, 18.5, 11.2, INK)
            base.paragraph_in_box(c, page["subtext"], 21 * mm, 127 * mm, 168 * mm, 17 * mm, 10.5, 7, GREY, bold=False)
            x, y, w, h = 14 * mm, 15 * mm, 182 * mm, 108 * mm
            c.setFillColor(NAVY); c.roundRect(x - 1.5 * mm, y - 1.5 * mm, w + 3 * mm, h + 3 * mm, 7 * mm, fill=1, stroke=0)
            c.setFillColor(colors.HexColor("#204560")); c.roundRect(x, y, w, h, 5.8 * mm, fill=1, stroke=0)
            draw_page_diagram(c, page, x, y, w, h)
            draw_scene_labels(c, page.get("labels", []), x + 3 * mm, y + h - 9 * mm, w - 6 * mm)
            if page.get("code"):
                c.saveState(); c.translate(x + w - 15 * mm, y + 6 * mm); c.rotate(-6)
                c.setFillColor(CREAM); c.setFont(base.font("bold"), 4.2); c.drawCentredString(0, 0, page["code"]); c.restoreState()
            c.setFillColor(GREY); c.setFont(base.font("regular"), 7.5); c.drawRightString(PAGE - 7 * mm, 6 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 6, 9, 12, 15, 17, 20, 23, 26, 28, 31):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState(); c.setStrokeColor(colors.HexColor("#C5D3D8")); c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY); c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E04 Adult Guide - Review version 1.0.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}"); c.restoreState()


def render_adult() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=19 * mm, bottomMargin=20 * mm,
        title="Adult Guide - E04 - Review 1.0.0", author="Maria Smith",
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
        generate_accessible_e04.main()
    if not args.student_only:
        render_adult()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(generate_accessible_e04.OUTPUT)


if __name__ == "__main__":
    main()
