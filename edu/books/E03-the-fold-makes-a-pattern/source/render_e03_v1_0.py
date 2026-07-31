#!/usr/bin/env python3
"""Render the plain-language 3D-stage E03 review edition 1.0.0."""

from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, SimpleDocTemplate

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "E01-something-is-here" / "source"))
import render_e01 as base


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.0.0.json"
GAME = ROOT / "edu" / "games" / "companion-adventures"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E03-THE-FOLD-MAKES-A-PATTERN" / "1.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E03-The-Fold-Makes-A-Pattern-v1.0.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E03-Adult-Guide-v1.0.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.0.0.html"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"

PAGE = 210 * mm
NAVY = colors.HexColor("#12203B")
INK = colors.HexColor("#20314A")
CREAM = colors.HexColor("#FFF9EA")
GOLD = colors.HexColor("#FFD35C")
GREEN = colors.HexColor("#2C765C")
BLUE = colors.HexColor("#70D5D3")
PURPLE = colors.HexColor("#6D4A91")
GREY = colors.HexColor("#5B6678")
WHITE = colors.white

ART = {
    "balcony": GAME / "public" / "art" / "stages" / "e02-stage-08-balcony-v1.png",
    "e03-keyart": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "trail-station": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "stopped-trail": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "light-row": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "tile-table": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-02-turn-gate-v1.png",
    "first-gate": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-02-turn-gate-v1.png",
    "second-gate": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-02-turn-gate-v1.png",
    "two-gates": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-02-turn-gate-v1.png",
    "broken-trail": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "repaired-trail": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-01-trail-station-v1.png",
    "over-under-bridge": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-03-over-under-bridge-v1.png",
    "route-choice": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-04-sunrise-arch-v1.png",
    "sunrise-arch": GAME / "public" / "art" / "stages" / "e03-source" / "e03-stage-04-sunrise-arch-v1.png",
}

SPRITES = {name: GAME / "public" / "art" / "characters" / "individual" / (f"{name}-v1.png" if name == "mira" else f"{name}.png") for name in ("mira", "tavi", "sol", "vee")}
IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32:
        raise ValueError("E03 1.0.0 must contain exactly 32 pages")
    if [page["page"] for page in book["pages"]] != list(range(1, 33)):
        raise ValueError("E03 page sequence is not contiguous")
    return book


def rounded_label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill: colors.Color) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, 10 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY if fill != NAVY else WHITE)
    c.setFont(base.font("bold"), 8.2)
    c.drawCentredString(x + width / 2, y + 3.2 * mm, text)


MOON_BLUE = colors.HexColor("#58C7ED")
SUN_GOLD = colors.HexColor("#FFD35C")
LEAF_GREEN = colors.HexColor("#72C77B")


def draw_role(c: canvas.Canvas, cx: float, cy: float, role: str, radius: float = 10 * mm, dim: bool = False) -> None:
    fill = {"moon": MOON_BLUE, "sun": SUN_GOLD, "star": PURPLE, "leaf": LEAF_GREEN}[role]
    c.saveState()
    c.setFillColor(colors.Color(fill.red, fill.green, fill.blue, alpha=.48 if dim else 1))
    c.setStrokeColor(WHITE)
    c.setLineWidth(2)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    c.setFillColor(WHITE)
    c.setStrokeColor(WHITE)
    if role == "moon":
        c.circle(cx - radius * .08, cy, radius * .55, fill=1, stroke=0)
        c.setFillColor(fill)
        c.circle(cx + radius * .18, cy + radius * .08, radius * .50, fill=1, stroke=0)
    elif role == "sun":
        c.circle(cx, cy, radius * .34, fill=1, stroke=0)
        c.setLineWidth(2)
        for angle in range(0, 360, 45):
            a = math.radians(angle)
            c.line(cx + math.cos(a) * radius * .48, cy + math.sin(a) * radius * .48,
                   cx + math.cos(a) * radius * .72, cy + math.sin(a) * radius * .72)
    elif role == "star":
        path = c.beginPath()
        for index in range(10):
            a = math.radians(90 + index * 36)
            r = radius * (.68 if index % 2 == 0 else .30)
            px, py = cx + math.cos(a) * r, cy + math.sin(a) * r
            path.moveTo(px, py) if index == 0 else path.lineTo(px, py)
        path.close(); c.drawPath(path, fill=1, stroke=0)
    else:
        path = c.beginPath()
        path.moveTo(cx, cy + radius * .66)
        path.curveTo(cx + radius * .58, cy + radius * .28, cx + radius * .52, cy - radius * .38, cx, cy - radius * .66)
        path.curveTo(cx - radius * .52, cy - radius * .38, cx - radius * .58, cy + radius * .28, cx, cy + radius * .66)
        path.close(); c.drawPath(path, fill=1, stroke=0)
        c.setStrokeColor(fill); c.setLineWidth(1.2); c.line(cx, cy - radius * .45, cx, cy + radius * .42)
    c.restoreState()


def draw_sequence(
    c: canvas.Canvas,
    roles: list[str],
    x: float,
    y: float,
    gap: float = 28 * mm,
    mark: int | None = None,
    radius: float = 9 * mm,
    labels: list[str] | None = None,
) -> None:
    for index, role in enumerate(roles):
        cx = x + index * gap
        if role == "unknown":
            draw_unknown(c, cx, y, radius)
        elif role == "dark":
            draw_dark_stone(c, cx, y, radius)
        else:
            draw_role(c, cx, y, role, radius)
        if labels:
            c.setFillColor(CREAM)
            c.setFont(base.font("bold"), 5.6 if radius < 8 * mm else 6.2)
            c.drawCentredString(cx, y + radius + 3 * mm, labels[index])
        if index + 1 < len(roles):
            c.setStrokeColor(WHITE); c.setLineWidth(2)
            c.line(cx + radius + 1 * mm, y, cx + gap - radius - 1 * mm, y)
        if mark == index:
            c.setStrokeColor(colors.HexColor("#EF6F61")); c.setLineWidth(4)
            c.circle(cx, y, radius + 3 * mm, fill=0, stroke=1)


def draw_unknown(c: canvas.Canvas, cx: float, cy: float, radius: float = 9 * mm) -> None:
    c.setFillColor(CREAM); c.setStrokeColor(WHITE); c.setLineWidth(2)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    c.setFillColor(NAVY); c.setFont(base.font("bold"), 20)
    c.drawCentredString(cx, cy - 2.5 * mm, "?")


def draw_dark_stone(c: canvas.Canvas, cx: float, cy: float, radius: float = 9 * mm) -> None:
    """Draw an unmistakably unlit trail stone rather than an abstract blank."""
    c.saveState()
    c.setFillColor(colors.HexColor("#202A3E"))
    c.setStrokeColor(CREAM)
    c.setLineWidth(2)
    c.circle(cx, cy, radius, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#7F8AA0"))
    c.setLineWidth(1.2)
    c.line(cx - radius * .42, cy - radius * .42, cx + radius * .42, cy + radius * .42)
    c.line(cx - radius * .42, cy + radius * .42, cx + radius * .42, cy - radius * .42)
    c.restoreState()


def draw_arrow(c: canvas.Canvas, x1: float, x2: float, cy: float, fill: colors.Color = WHITE) -> None:
    c.saveState()
    c.setStrokeColor(fill)
    c.setFillColor(fill)
    c.setLineWidth(2.2)
    c.line(x1, cy, x2 - 3 * mm, cy)
    arrow = c.beginPath()
    arrow.moveTo(x2, cy)
    arrow.lineTo(x2 - 4 * mm, cy + 3 * mm)
    arrow.lineTo(x2 - 4 * mm, cy - 3 * mm)
    arrow.close()
    c.drawPath(arrow, fill=1, stroke=0)
    c.restoreState()


LANTERN_PART_COLORS = (BLUE, GOLD, PURPLE, colors.HexColor("#EF816D"))


def draw_whole_lantern(c: canvas.Canvas, cx: float, cy: float, radius: float = 14 * mm) -> None:
    """Reuse E02's recognisable four-part round Moon Lantern design."""
    c.saveState()
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.5)
    for fill, angle in zip(LANTERN_PART_COLORS, (0, 90, 180, 270)):
        c.setFillColor(fill)
        c.wedge(cx - radius, cy - radius, cx + radius, cy + radius, angle, 90, fill=1, stroke=1)
    c.setFillColor(colors.Color(1, 1, 1, alpha=.14))
    c.circle(cx, cy, radius * .58, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.4)
    c.circle(cx, cy, radius, fill=0, stroke=1)
    c.setFillColor(GOLD)
    c.rect(cx - radius * .45, cy + radius + 1 * mm, radius * .9, 3 * mm, fill=1, stroke=0)
    c.restoreState()


def draw_role_card(
    c: canvas.Canvas,
    cx: float,
    cy: float,
    role: str,
    label: str,
    width: float = 36 * mm,
    height: float = 34 * mm,
    dim: bool = False,
) -> None:
    """Keep each word attached above its recognisable moon or sun picture."""
    c.saveState()
    c.setFillColor(colors.Color(.04, .09, .18, alpha=.90))
    c.setStrokeColor(GOLD if not dim else colors.HexColor("#A7AFC0"))
    c.setLineWidth(2)
    c.roundRect(cx - width / 2, cy - height / 2, width, height, 4 * mm, fill=1, stroke=1)
    c.setFillColor(CREAM)
    c.setFont(base.font("bold"), 5.8)
    c.drawCentredString(cx, cy + height / 2 - 6 * mm, label)
    draw_role(c, cx, cy - 3 * mm, role, min(width, height) * .24, dim=dim)
    c.restoreState()


def draw_turn_transition(
    c: canvas.Canvas,
    x: float,
    y: float,
    before: str,
    after: str | None,
    gate_label: str,
) -> None:
    """Show one physical before/turn/after action inside the round gate scene."""
    cy = y + 58 * mm
    left = x + 64 * mm
    right = x + 124 * mm
    rounded_label(c, gate_label, x + 65 * mm, y + 84 * mm, 52 * mm, NAVY)
    draw_role_card(c, left, cy, before, f"BEFORE · {role_name(before)}")
    draw_arrow(c, left + 20 * mm, right - 20 * mm, cy)
    c.setFillColor(CREAM)
    c.setFont(base.font("bold"), 6)
    c.drawCentredString((left + right) / 2, cy + 6 * mm, "ONE TURN")
    if after is None:
        c.saveState()
        c.setFillColor(colors.Color(.04, .09, .18, alpha=.90))
        c.setStrokeColor(WHITE)
        c.setLineWidth(2)
        c.roundRect(right - 18 * mm, cy - 17 * mm, 36 * mm, 34 * mm, 4 * mm, fill=1, stroke=1)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 5.8)
        c.drawCentredString(right, cy + 11 * mm, "AFTER · WHICH SIDE?")
        draw_unknown(c, right, cy - 3 * mm, 8 * mm)
        c.restoreState()
    else:
        draw_role_card(c, right, cy, after, f"AFTER · {role_name(after)}")


def role_name(role: str) -> str:
    return {"moon": "BLUE MOON", "sun": "GOLD SUN", "star": "STAR", "leaf": "LEAF"}[role]


def draw_small_arch(c: canvas.Canvas, cx: float, cy: float, label: str) -> None:
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(cx - 5 * mm, cy - 6 * mm, cx - 5 * mm, cy)
    c.line(cx + 5 * mm, cy - 6 * mm, cx + 5 * mm, cy)
    c.arc(cx - 5 * mm, cy - 5 * mm, cx + 5 * mm, cy + 5 * mm, 0, 180)
    c.setFillColor(CREAM)
    c.setFont(base.font("bold"), 4.8)
    c.drawCentredString(cx, cy + 7 * mm, label)
    c.restoreState()


def draw_garden_gate(c: canvas.Canvas, cx: float, cy: float) -> None:
    """Place the next destination visibly beyond the lit Sunrise Arch."""
    width, height = 54 * mm, 38 * mm
    c.saveState()
    c.setFillColor(colors.Color(.05, .11, .20, alpha=.84))
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.4)
    c.roundRect(cx - width / 2, cy - height / 2, width, height, 5 * mm, fill=1, stroke=1)
    for post in range(7):
        px = cx - 21 * mm + post * 7 * mm
        c.line(px, cy - 12 * mm, px, cy + 10 * mm)
        picket = c.beginPath()
        picket.moveTo(px - 2.3 * mm, cy + 10 * mm)
        picket.lineTo(px, cy + 15 * mm)
        picket.lineTo(px + 2.3 * mm, cy + 10 * mm)
        picket.close()
        c.drawPath(picket, fill=0, stroke=1)
    c.line(cx - 23 * mm, cy - 5 * mm, cx + 23 * mm, cy - 5 * mm)
    c.setFillColor(GOLD)
    c.roundRect(cx - 20 * mm, cy + 18 * mm, 40 * mm, 9 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont(base.font("bold"), 7)
    c.drawCentredString(cx, cy + 21 * mm, "GARDEN GATE")
    c.restoreState()


def draw_page_diagram(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    number = page["page"]
    cy = y + 61 * mm
    if number == 3:
        c.setFillColor(colors.Color(.04, .09, .18, alpha=.88))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(x + 20 * mm, y + 39 * mm, 142 * mm, 54 * mm, 6 * mm, fill=1, stroke=1)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 6.2)
        c.drawCentredString(x + 48 * mm, y + 82 * mm, "SAME WHOLE LANTERN")
        draw_whole_lantern(c, x + 48 * mm, y + 60 * mm, 14 * mm)
        draw_arrow(c, x + 65 * mm, x + 79 * mm, y + 60 * mm)
        draw_sequence(
            c,
            ["moon", "sun", "moon"],
            x + 91 * mm,
            y + 60 * mm,
            gap=27 * mm,
            radius=7 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON"],
        )
    elif number in (4, 5):
        c.setFillColor(colors.Color(.04, .09, .18, alpha=.88))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(x + 24 * mm, y + 40 * mm, 137 * mm, 50 * mm, 6 * mm, fill=1, stroke=1)
        draw_sequence(
            c,
            ["moon", "sun", "moon", "dark"],
            x + 45 * mm,
            y + 60 * mm,
            gap=35 * mm,
            radius=8 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON", "NO LIGHT"],
        )
        c.setFillColor(GOLD)
        c.setFont(base.font("bold"), 6.5)
        c.drawCentredString(x + 150 * mm, y + 82 * mm, "TRAIL STOPS")
    elif number == 6:
        c.setFillColor(colors.Color(.04, .09, .18, alpha=.88))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(x + 35 * mm, y + 39 * mm, 114 * mm, 54 * mm, 6 * mm, fill=1, stroke=1)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 7)
        c.drawCentredString(x + 92 * mm, y + 84 * mm, "ONE TILE · TWO SIDES")
        draw_role_card(c, x + 67 * mm, y + 59 * mm, "moon", "BLUE MOON SIDE", 42 * mm, 34 * mm)
        draw_role_card(c, x + 117 * mm, y + 59 * mm, "sun", "GOLD SUN SIDE", 42 * mm, 34 * mm)
    elif number == 7:
        draw_role_card(c, x + 58 * mm, y + 59 * mm, "moon", "TILE SHOWING NOW", 42 * mm, 38 * mm)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 6.2)
        c.drawCentredString(x + 129 * mm, y + 83 * mm, "POINT TO ONE PICTURE")
        draw_role_card(c, x + 112 * mm, y + 58 * mm, "moon", "BLUE MOON", 31 * mm, 31 * mm)
        draw_role_card(c, x + 148 * mm, y + 58 * mm, "sun", "GOLD SUN", 31 * mm, 31 * mm)
    elif number == 8:
        c.setFillColor(colors.Color(.04, .09, .18, alpha=.88))
        c.setStrokeColor(GOLD)
        c.setLineWidth(2)
        c.roundRect(x + 35 * mm, y + 39 * mm, 114 * mm, 54 * mm, 6 * mm, fill=1, stroke=1)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 7)
        c.drawCentredString(x + 92 * mm, y + 84 * mm, "THE SAME TILE")
        draw_role_card(c, x + 67 * mm, y + 59 * mm, "moon", "SHOWING · BLUE MOON", 44 * mm, 34 * mm)
        draw_role_card(c, x + 119 * mm, y + 59 * mm, "sun", "UNDER · GOLD SUN", 44 * mm, 34 * mm, dim=True)
    elif number in (9, 10):
        draw_turn_transition(c, x, y, "moon", None, "FIRST GATE")
    elif number == 11:
        draw_turn_transition(c, x, y, "moon", "sun", "FIRST GATE")
    elif number == 12:
        draw_turn_transition(c, x, y, "sun", None, "SECOND GATE")
    elif number == 13:
        draw_turn_transition(c, x, y, "sun", "moon", "SECOND GATE")
    elif number == 14:
        rounded_label(c, "THE FOLD RULE", x + 66 * mm, y + 86 * mm, 52 * mm, NAVY)
        states = ((x + 48 * mm, "moon", "START · BLUE MOON"),
                  (x + 94 * mm, "sun", "1 TURN · GOLD SUN"),
                  (x + 140 * mm, "moon", "RETURN · BLUE MOON"))
        for sx, role, label in states:
            draw_role_card(c, sx, y + 59 * mm, role, label, 34 * mm, 34 * mm)
        draw_arrow(c, x + 66 * mm, x + 76 * mm, y + 59 * mm)
        draw_arrow(c, x + 112 * mm, x + 122 * mm, y + 59 * mm)
    elif number == 15:
        draw_sequence(
            c,
            ["moon", "sun", "moon", "sun"],
            x + 40 * mm,
            cy,
            gap=34 * mm,
            radius=8 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON", "GOLD SUN"],
        )
    elif number == 16:
        draw_sequence(
            c,
            ["moon", "sun", "moon", "sun", "unknown"],
            x + 33 * mm,
            cy,
            gap=30 * mm,
            radius=8 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON", "GOLD SUN", "WHAT NEXT?"],
        )
    elif number == 17:
        draw_sequence(
            c,
            ["moon", "sun", "moon", "sun", "moon"],
            x + 33 * mm,
            cy,
            gap=30 * mm,
            radius=8 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON", "GOLD SUN", "NEXT · BLUE"],
        )
    elif number in (18, 19, 20):
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 7)
        c.drawCentredString(x + 92 * mm, y + 84 * mm, "SOL'S FIRST TRY")
        draw_sequence(
            c,
            ["moon", "sun", "moon", "moon"],
            x + 40 * mm,
            cy,
            gap=34 * mm,
            mark=3 if number == 20 else None,
            radius=8 * mm,
            labels=["BLUE MOON", "GOLD SUN", "BLUE MOON", "BLUE MOON"],
        )
    elif number == 21:
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 5.8)
        c.drawCentredString(x + 92 * mm, y + 91 * mm, "FIRST TRY KEPT")
        draw_sequence(c, ["moon", "sun", "moon", "moon"], x + 65 * mm, y + 78 * mm, gap=18 * mm, radius=5 * mm)
        c.setFont(base.font("bold"), 6.5)
        c.drawCentredString(x + 92 * mm, y + 67 * mm, "REPAIRED TRAIL")
        draw_sequence(
            c,
            ["moon", "sun", "moon", "sun"],
            x + 42 * mm,
            y + 51 * mm,
            gap=33 * mm,
            radius=7.5 * mm,
        )
    elif number == 22:
        rounded_label(c, "FIRST · OVER", x + 66 * mm, y + 82 * mm, 52 * mm, GOLD)
        draw_arrow(c, x + 62 * mm, x + 123 * mm, y + 75 * mm, GOLD)
        rounded_label(c, "NEXT · UNDER", x + 66 * mm, y + 57 * mm, 52 * mm, BLUE)
        draw_arrow(c, x + 62 * mm, x + 123 * mm, y + 50 * mm, BLUE)
    elif number in (23, 24):
        roles = ["OVER", "UNDER", "OVER", "UNDER" if number == 24 else "?"]
        for index, label in enumerate(roles):
            cx = x + (42 + index * 34) * mm
            c.setFillColor(GOLD if number == 24 and index == 3 else CREAM)
            c.setStrokeColor(WHITE)
            c.setLineWidth(2)
            c.roundRect(cx - 14 * mm, cy - 9 * mm, 28 * mm, 18 * mm, 5 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(base.font("bold"), 9 if label != "?" else 14)
            c.drawCentredString(cx, cy - (2 if label != "?" else 2.8) * mm, label)
    elif number in (25, 26, 27):
        route_roles = (("A", ["moon", "sun", "moon"]),
                       ("B", ["moon", "sun", "sun", "moon"]),
                       ("C", ["moon", "sun", "moon", "sun"]))
        for index, (label, roles) in enumerate(route_roles):
            ry = y + (88 - index * 19) * mm
            chosen = number == 27 and label == "C"
            rounded_label(c, f"ROUTE {label}", x + 48 * mm, ry - 5 * mm, 30 * mm, GOLD if chosen else CREAM)
            for role_index, role in enumerate(roles):
                draw_role(c, x + (88 + role_index * 18) * mm, ry, role, 5.4 * mm)
            if label == "A":
                c.setStrokeColor(CREAM)
                c.setLineWidth(2.2)
                c.line(x + 148 * mm, ry - 7 * mm, x + 148 * mm, ry + 7 * mm)
                c.setFillColor(CREAM)
                c.setFont(base.font("bold"), 4.8)
                c.drawCentredString(x + 148 * mm, ry + 9 * mm, "STOPS")
            else:
                draw_small_arch(c, x + 164 * mm, ry, "ARCH")
            if chosen:
                c.setStrokeColor(GOLD); c.setLineWidth(3)
                c.roundRect(x + 84 * mm, ry - 8 * mm, 80 * mm, 16 * mm, 8 * mm, fill=0, stroke=1)
    elif number == 28:
        draw_turn_transition(c, x, y, "moon", None, "THE ARCH REMEMBERS")
    elif number == 29:
        draw_turn_transition(c, x, y, "moon", "sun", "REMEMBERED")
    elif number == 30:
        draw_sequence(
            c,
            ["star", "leaf", "star", "unknown"],
            x + 44 * mm,
            cy,
            gap=34 * mm,
            radius=8 * mm,
            labels=["STAR", "LEAF", "STAR", "WHAT NEXT?"],
        )
    elif number == 31:
        draw_sequence(
            c,
            ["star", "leaf", "star", "leaf"],
            x + 44 * mm,
            cy,
            gap=34 * mm,
            radius=8 * mm,
            labels=["STAR", "LEAF", "STAR", "NEXT · LEAF"],
        )
    elif number == 32:
        draw_garden_gate(c, x + 92 * mm, y + 63 * mm)


def draw_stage(c: canvas.Canvas, page: dict) -> None:
    x, y, w, h = 14 * mm, 18 * mm, 182 * mm, 102 * mm
    c.setFillColor(NAVY)
    c.roundRect(x - 1.5 * mm, y - 1.5 * mm, w + 3 * mm, h + 3 * mm, 7 * mm, fill=1, stroke=0)
    c.saveState()
    path = c.beginPath()
    path.roundRect(x, y, w, h, 5.8 * mm)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(image(ART[page["art"]]), x, y, width=w, height=h, preserveAspectRatio=True, anchor="c", mask="auto")
    c.setFillColor(colors.Color(0.02, 0.05, 0.11, alpha=.18))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.restoreState()

    draw_page_diagram(c, page, x, y, w, h)

    cast = page.get("cast", [])
    positions = {1: [0.12], 2: [0.08, 0.69], 3: [0.02, 0.39, 0.74], 4: [0.00, 0.24, 0.49, 0.74]}.get(len(cast), [])
    for position, name in zip(positions, cast):
        sprite_w = (42 if name == "mira" else 30 if name in ("tavi", "sol") else 34) * mm
        c.drawImage(image(SPRITES[name]), x + position * w, y + 4 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")

    labels = page.get("labels", [])
    if labels:
        gap = 4 * mm
        available = w - gap * (len(labels) - 1)
        label_w = min(74 * mm, available / len(labels))
        total = label_w * len(labels) + gap * (len(labels) - 1)
        lx = PAGE / 2 - total / 2
        for label in labels:
            rounded_label(c, label, lx, y + h + 2 * mm, label_w, GOLD)
            lx += label_w + gap

    code = page.get("code")
    if code:
        c.saveState()
        c.translate(x + w - 14 * mm, y + 9 * mm)
        c.rotate(-7 + (page["page"] % 3) * 5)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 4.2)
        c.drawCentredString(0, 0, code)
        c.restoreState()


def draw_cover(c: canvas.Canvas, page: dict) -> None:
    c.drawImage(image(ART["e03-keyart"]), 0, 0, width=PAGE, height=PAGE, preserveAspectRatio=False, mask="auto")
    c.setFillColor(colors.Color(0.02, .04, .10, alpha=.68))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    for position, name in zip((0.04, 0.27, 0.50, 0.73), ("mira", "tavi", "sol", "vee")):
        sprite_w = (51 if name == "mira" else 40 if name in ("tavi", "sol") else 46) * mm
        c.drawImage(image(SPRITES[name]), position * PAGE, 28 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")
    rounded_label(c, page["badge"], 18 * mm, PAGE - 25 * mm, 174 * mm, GOLD)
    base.paragraph_in_box(c, page["text"], 17 * mm, 139 * mm, 176 * mm, 40 * mm, 38, 27, WHITE)
    base.paragraph_in_box(c, page["subtext"], 19 * mm, 122 * mm, 172 * mm, 15 * mm, 18, 12, colors.HexColor("#FFE8A1"), bold=False)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 9)
    c.drawString(18 * mm, 14 * mm, "Maria Smith · Review edition 1.0.0")


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']} · {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years plain-language 3D story adventure, review 1.0.0")
    c.setKeywords("Smithian Fold Theory, early years, Fold, pattern, turn, return")
    for page in book["pages"]:
        if page["kind"] == "cover":
            draw_cover(c, page)
        else:
            c.setFillColor(CREAM)
            c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
            rounded_label(c, page["badge"], 15 * mm, PAGE - 23 * mm, 180 * mm, GREEN if page["kind"] in ("reveal", "result") else BLUE)
            if page["kind"] == "legal":
                base.paragraph_in_box(c, page["text"], 21 * mm, 147 * mm, 168 * mm, 42 * mm, 12, 8, INK, bold=False)
                base.paragraph_in_box(c, page["subtext"], 22 * mm, 132 * mm, 166 * mm, 12 * mm, 10, 7, GREY, bold=False)
            else:
                base.paragraph_in_box(c, page["text"], 17 * mm, 150 * mm, 176 * mm, 34 * mm, 20.5, 13.5, INK)
                base.paragraph_in_box(c, page["subtext"], 20 * mm, 132 * mm, 170 * mm, 14 * mm, 10.5, 7.5, GREY, bold=False)
            draw_stage(c, page)
            c.setFillColor(GREY)
            c.setFont(base.font("regular"), 8)
            c.drawRightString(PAGE - 8 * mm, 7 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 7, 10, 13, 16, 19, 22, 27, 31):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def render_accessible(book: dict) -> None:
    sections = []
    for page in book["pages"]:
        lines = "".join(f"<p>{html.escape(line)}</p>" for line in page["text"].split("\n") if line)
        code = f"<p><strong>Optional picture code:</strong> {html.escape(page['code'])}</p>" if page.get("code") else ""
        description = html.escape(page["alt"])
        sections.append(f'''<section class="page" id="page-{page['page']}" aria-labelledby="page-{page['page']}-title"><h2 id="page-{page['page']}-title">Page {page['page']}: {html.escape(page['badge'])}</h2>{lines}<p>{html.escape(page['subtext'])}</p><figure role="img" aria-label="{description}"><figcaption><strong>Picture description:</strong> {description}</figcaption></figure>{code}</section>''')
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    ACCESSIBLE_HTML.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])} · accessible 1.0.0</title><style>body{{font:1.15rem/1.65 system-ui,sans-serif;max-width:52rem;margin:auto;padding:2rem;color:#20314a;background:#fff9ea}}section{{padding:2rem 0;border-bottom:2px solid #c9b98d}}figure{{margin:1rem 0;padding:1rem;border-left:.35rem solid #2f8f76;background:#fff}}h1,h2{{line-height:1.15}}nav a{{margin-right:.7rem}}</style></head><body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])} · Review 1.0.0</p></header><nav aria-label="Page links">{''.join(f'<a href="#page-{n}">{n}</a>' for n in range(1,33))}</nav><main>{''.join(sections)}</main></body></html>''', encoding="utf-8")


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E03 Adult Guide · Review version 1.0.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult() -> None:
    doc = SimpleDocTemplate(str(ADULT_PDF), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=19*mm, bottomMargin=20*mm, title="Adult Guide · E03 · Review 1.0.0", author="Maria Smith")
    story = base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    for index, flowable in enumerate(story):
        if getattr(flowable, "getPlainText", lambda: "")() == "Answer and reveal table":
            story.insert(index, PageBreak())
            break
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
        render_accessible(book)
    if not args.student_only:
        render_adult()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
