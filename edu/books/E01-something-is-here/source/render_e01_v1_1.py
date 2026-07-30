#!/usr/bin/env python3
"""Render E01 version 1.1.0 as a discovery-led game story."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate

import render_e01 as base


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE_JSON = BOOK_DIR / "source" / "book-v1.1.0.json"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.1.0.html"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.1.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.1.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.1.0.pdf"

PAGE = base.PAGE
NAVY = base.NAVY
INK = base.INK
CREAM = base.CREAM
SKY = base.SKY
BLUE = base.BLUE
ORANGE = base.ORANGE
YELLOW = base.YELLOW
GREEN = base.GREEN
CORAL = base.CORAL
PALE_GREEN = base.PALE_GREEN
WHITE = base.WHITE
GREY = base.GREY
PURPLE = colors.HexColor("#7D6AA5")
LILAC = colors.HexColor("#EEE9F7")


def label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill=WHITE, ink=INK, size=8) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.6)
    c.roundRect(x, y, width, 10 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(ink)
    c.setFont(base.font("bold"), size)
    c.drawCentredString(x + width / 2, y + 3.3 * mm, text)


def marker(c: canvas.Canvas, number: int, x: float, y: float, fill=YELLOW) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.8)
    c.circle(x, y, 6 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(base.font("bold"), 11)
    c.drawCentredString(x, y - 1.4 * mm, str(number))


def star(c: canvas.Canvas, x: float, y: float, radius: float = 9 * mm, fill=YELLOW) -> None:
    import math

    path = c.beginPath()
    for index in range(10):
        angle = math.radians(90 + index * 36)
        r = radius if index % 2 == 0 else radius * 0.43
        px = x + r * math.cos(angle)
        py = y + r * math.sin(angle)
        if index == 0:
            path.moveTo(px, py)
        else:
            path.lineTo(px, py)
    path.close()
    c.setFillColor(fill)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.6)
    c.drawPath(path, fill=1, stroke=1)


def draw_bell(c: canvas.Canvas, x: float, y: float, scale: float = 1.0, crossed: bool = False) -> None:
    c.setFillColor(YELLOW)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.wedge(x - 17 * mm * scale, y - 11 * mm * scale, x + 17 * mm * scale, y + 23 * mm * scale, 0, 180, fill=1, stroke=1)
    c.line(x - 18 * mm * scale, y - 10 * mm * scale, x + 18 * mm * scale, y - 10 * mm * scale)
    c.circle(x, y - 14 * mm * scale, 3 * mm * scale, fill=1, stroke=1)
    if crossed:
        c.setStrokeColor(CORAL)
        c.setLineWidth(4)
        c.line(x + 22 * mm * scale, y + 4 * mm * scale, x + 35 * mm * scale, y + 18 * mm * scale)
        c.line(x + 35 * mm * scale, y + 4 * mm * scale, x + 22 * mm * scale, y + 18 * mm * scale)


def draw_card(c: canvas.Canvas, x: float, y: float, w: float = 62 * mm, h: float = 42 * mm, mark: str | None = None) -> None:
    c.setFillColor(CREAM)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.roundRect(x - w / 2, y - h / 2, w, h, 4 * mm, fill=1, stroke=1)
    if mark:
        c.setFillColor(CORAL)
        c.setFont(base.font("bold"), 26)
        c.drawCentredString(x, y - 3 * mm, mark)


def draw_curtain(c: canvas.Canvas, x: float, y: float, w: float = 74 * mm, h: float = 78 * mm) -> None:
    c.setFillColor(PURPLE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.roundRect(x - w / 2, y - h / 2, w, h, 5 * mm, fill=1, stroke=1)
    c.setStrokeColor(LILAC)
    for offset in (-24, -8, 8, 24):
        c.line(x + offset * mm, y - h / 2 + 4 * mm, x + offset * mm, y + h / 2 - 4 * mm)
    c.setFillColor(ORANGE)
    c.circle(x - 15 * mm, y - h / 2 + 3 * mm, 8 * mm, fill=1, stroke=1)
    c.setFillColor(BLUE)
    c.circle(x + 17 * mm, y - h / 2 + 5 * mm, 10 * mm, fill=1, stroke=1)


def draw_map(c: canvas.Canvas, x: float, y: float, stars: int = 0, doors: bool = False) -> None:
    c.setFillColor(colors.HexColor("#F5D89A"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.roundRect(x - 58 * mm, y - 36 * mm, 116 * mm, 72 * mm, 7 * mm, fill=1, stroke=1)
    c.setStrokeColor(CORAL)
    c.setDash(5, 4)
    c.line(x - 43 * mm, y + 20 * mm, x + 38 * mm, y - 12 * mm)
    c.setDash()
    for index in range(5):
        sx = x - 42 * mm + index * 21 * mm
        star(c, sx, y + 25 * mm, 5 * mm, YELLOW if index < stars else WHITE)
    if doors:
        for dx, letter in ((-27, "A"), (27, "B")):
            c.setFillColor(BLUE if letter == "A" else PURPLE)
            c.setStrokeColor(NAVY)
            c.roundRect(x + dx * mm - 15 * mm, y - 27 * mm, 30 * mm, 39 * mm, 4 * mm, fill=1, stroke=1)
            c.setFillColor(WHITE)
            c.setFont(base.font("bold"), 19)
            c.drawCentredString(x + dx * mm, y - 9 * mm, letter)


def draw_room(c: canvas.Canvas, reveal: bool = False, final: bool = False) -> None:
    cx = PAGE / 2
    cy = 125 * mm
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.line(26 * mm, 81 * mm, PAGE - 26 * mm, 81 * mm)
    c.setFillColor(colors.HexColor("#E7C99B"))
    c.rect(48 * mm, 83 * mm, 108 * mm, 25 * mm, fill=1, stroke=1)
    c.setFillColor(SKY)
    for index in range(6):
        c.rect(57 * mm + index * 15 * mm, 85 * mm, 10 * mm, 21 * mm, fill=1, stroke=0)
    base.draw_mira(c, 44 * mm, cy - 5 * mm, 1.3)
    base.draw_pip(c, 163 * mm, cy + 2 * mm, 1.2)
    base.draw_box(c, 91 * mm, cy - 18 * mm, 0.66)
    draw_bell(c, 129 * mm, cy - 11 * mm, 0.55)
    c.setFillColor(YELLOW)
    c.setStrokeColor(NAVY)
    c.rect(24 * mm, 135 * mm, 13 * mm, 35 * mm, fill=1, stroke=1)
    c.setFillColor(WHITE)
    c.circle(30.5 * mm, 173 * mm, 10 * mm, fill=1, stroke=1)
    draw_card(c, 178 * mm, 153 * mm, 22 * mm, 25 * mm, "?")
    star(c, 111 * mm, 88 * mm, 4 * mm)
    if reveal:
        for number, x, y in ((1, 44, 158), (2, 163, 145), (3, 91, 114), (4, 129, 126), (5, 103, 94)):
            marker(c, number, x * mm, y * mm)
    if final:
        draw_card(c, 67 * mm, 164 * mm, 35 * mm, 25 * mm)
        draw_curtain(c, 165 * mm, 124 * mm, 35 * mm, 61 * mm)


def draw_two_doors(c: canvas.Canvas, reveal: str | None = None) -> None:
    cx = PAGE / 2
    cy = 128 * mm
    for x, letter, fill in ((62 * mm, "A", BLUE), (148 * mm, "B", PURPLE)):
        c.setFillColor(fill)
        c.setStrokeColor(NAVY)
        c.setLineWidth(2.5)
        c.roundRect(x - 27 * mm, cy - 43 * mm, 54 * mm, 86 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(WHITE)
        c.setFont(base.font("bold"), 30)
        c.drawCentredString(x, cy + 22 * mm, letter)
    if reveal != "A":
        draw_card(c, 62 * mm, cy - 8 * mm, 28 * mm, 23 * mm, "*")
    c.setStrokeColor(WHITE)
    c.setDash(5, 4)
    c.roundRect(148 * mm - 15 * mm, cy - 20 * mm, 30 * mm, 28 * mm, 3 * mm, fill=0, stroke=1)
    c.setDash()
    if reveal == "A":
        base.draw_mira(c, 108 * mm, 95 * mm, 1.0)
        draw_card(c, 92 * mm, 127 * mm, 27 * mm, 22 * mm, "*")
        c.setStrokeColor(GREEN)
        c.setLineWidth(4)
        c.line(68 * mm, 127 * mm, 77 * mm, 127 * mm)
        c.line(74 * mm, 131 * mm, 78 * mm, 127 * mm)
        c.line(74 * mm, 123 * mm, 78 * mm, 127 * mm)
        for number, x, y in ((1, 92, 127), (2, 75, 141), (3, 108, 151)):
            marker(c, number, x * mm, y * mm)
    elif reveal == "B":
        base.draw_mira(c, 112 * mm, 94 * mm, 1.0)
        label(c, "NO EXAMPLE GIVEN", 119 * mm, 155 * mm, 58 * mm, WHITE, PURPLE, 7)


def draw_scene(c: canvas.Canvas, art: str) -> None:
    cx = PAGE / 2
    cy = 129 * mm
    if art == "game_cover":
        draw_map(c, cx, 104 * mm, 2)
        base.draw_mira(c, 38 * mm, 107 * mm, 1.25)
        base.draw_pip(c, 171 * mm, 116 * mm, 1.25)
        base.draw_box(c, 63 * mm, 77 * mm, 0.48)
        draw_bell(c, 95 * mm, 78 * mm, 0.35)
        draw_card(c, 125 * mm, 78 * mm, 28 * mm, 20 * mm)
        draw_curtain(c, 159 * mm, 84 * mm, 24 * mm, 35 * mm)
    elif art == "review_stamp":
        base.icon_card(c, cx - 35 * mm, cy, "open book", "<> ", SKY)
        c.setFillColor(PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.setLineWidth(3)
        c.circle(cx + 42 * mm, cy, 25 * mm, fill=1, stroke=1)
        c.setFillColor(GREEN)
        c.setFont(base.font("bold"), 18)
        c.drawCentredString(cx + 42 * mm, cy + 3 * mm, "1.1.0")
        c.setFont(base.font("bold"), 8)
        c.drawCentredString(cx + 42 * mm, cy - 8 * mm, "REVIEW")
    elif art == "mystery_map":
        draw_map(c, cx + 12 * mm, cy, 0)
        base.draw_mira(c, 35 * mm, 104 * mm, 1.25)
        base.draw_pip(c, 170 * mm, 118 * mm, 1.3)
        label(c, "FIND NOTHING", 75 * mm, 126 * mm, 60 * mm, WHITE, CORAL, 10)
    elif art == "game_rules":
        for index, (symbol, word, fill) in enumerate((("EYE", "SPOT", SKY), ("?", "SAY", LILAC), ("OK", "CHECK", PALE_GREEN))):
            x = 47 * mm + index * 58 * mm
            base.icon_card(c, x, cy, word, symbol, fill)
        base.draw_pip(c, 38 * mm, 91 * mm, 0.9)
    elif art == "room_spot":
        draw_room(c)
    elif art == "room_reveal":
        draw_room(c, reveal=True)
    elif art in ("box_challenge", "box_reveal"):
        base.draw_box(c, cx, cy - 8 * mm, 1.25)
        base.draw_mira(c, 38 * mm, cy - 20 * mm, 1.25)
        base.draw_pip(c, 169 * mm, cy - 12 * mm, 1.2)
        if art == "box_reveal":
            label(c, "BOX HERE", 72 * mm, 169 * mm, 66 * mm, PALE_GREEN, GREEN)
            label(c, "NO TOY INSIDE", 72 * mm, 86 * mm, 66 * mm, WHITE, CORAL)
            c.setStrokeColor(GREEN)
            c.setDash(3, 3)
            c.line(53 * mm, 146 * mm, 84 * mm, 132 * mm)
            c.setDash()
    elif art == "star_one":
        draw_map(c, cx, cy, 1)
        base.draw_pip(c, 163 * mm, 105 * mm, 1.25)
        base.draw_box(c, 44 * mm, 99 * mm, 0.42)
    elif art in ("bell_challenge", "bell_reveal"):
        base.draw_mira(c, 48 * mm, cy - 15 * mm, 1.35)
        base.draw_pip(c, 163 * mm, cy - 8 * mm, 1.25)
        draw_bell(c, 108 * mm, cy + 8 * mm, 1.0, crossed=art == "bell_reveal")
        if art == "bell_challenge":
            for index in range(3):
                c.setFillColor(BLUE)
                c.circle(79 * mm + index * 12 * mm, 91 * mm, 2.3 * mm, fill=1, stroke=0)
        else:
            for number, x, y in ((1, 48, 158), (2, 163, 148), (3, 108, 147)):
                marker(c, number, x * mm, y * mm)
    elif art in ("blank_challenge", "blank_reveal"):
        draw_card(c, cx, cy, 105 * mm, 67 * mm)
        c.setFillColor(ORANGE)
        c.setStrokeColor(NAVY)
        c.wedge(64 * mm, 112 * mm, 82 * mm, 130 * mm, 20, 130, fill=1, stroke=1)
        c.setStrokeColor(BLUE)
        c.setLineWidth(5)
        c.circle(147 * mm, 153 * mm, 11 * mm, fill=0, stroke=1)
        c.line(154 * mm, 145 * mm, 168 * mm, 130 * mm)
        if art == "blank_reveal":
            for number, x, y in ((1, 105, 129), (2, 56, 129), (3, 74, 121), (4, 148, 153)):
                marker(c, number, x * mm, y * mm)
    elif art in ("word_hunt", "word_reveal"):
        letters = "NOTHING"
        for index, letter in enumerate(letters):
            x = 37 * mm + index * 23 * mm
            c.setFillColor((SKY, YELLOW, PALE_GREEN, LILAC, colors.HexColor("#FAD7CB"), SKY, YELLOW)[index])
            c.setStrokeColor(NAVY)
            c.rect(x - 9 * mm, cy - 9 * mm, 18 * mm, 18 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(base.font("bold"), 18)
            c.drawCentredString(x, cy - 4 * mm, letter)
        for x, y in ((42, 164), (165, 161), (28, 102), (180, 102)):
            star(c, x * mm, y * mm, 5 * mm, WHITE)
        if art == "word_reveal":
            c.setStrokeColor(GREEN)
            c.setLineWidth(4)
            c.roundRect(22 * mm, cy - 15 * mm, 166 * mm, 30 * mm, 5 * mm, fill=0, stroke=1)
            base.draw_mira(c, 43 * mm, 88 * mm, 0.9)
            base.draw_pip(c, 169 * mm, 94 * mm, 0.9)
    elif art in ("curtain_challenge", "curtain_reveal"):
        draw_curtain(c, cx, cy)
        base.draw_mira(c, 43 * mm, 105 * mm, 1.2)
        base.draw_pip(c, 169 * mm, 116 * mm, 1.1)
        if art == "curtain_reveal":
            label(c, "CURTAIN", 75 * mm, 171 * mm, 60 * mm, WHITE, PURPLE)
            label(c, "TOYS HIDDEN", 75 * mm, 84 * mm, 60 * mm, WHITE, CORAL)
    elif art == "map_opens":
        draw_map(c, cx, cy, 5, doors=True)
        base.draw_mira(c, 34 * mm, 101 * mm, 1.0)
        base.draw_pip(c, 177 * mm, 111 * mm, 1.0)
    elif art == "doors_challenge":
        draw_two_doors(c)
    elif art == "door_a_reveal":
        draw_two_doors(c, "A")
    elif art == "door_b_reveal":
        draw_two_doors(c, "B")
    elif art in ("draw_challenge", "draw_reveal"):
        if art == "draw_challenge":
            draw_card(c, cx, cy, 80 * mm, 55 * mm)
            c.setFillColor(ORANGE)
            c.setStrokeColor(NAVY)
            c.setLineWidth(2)
            c.roundRect(151 * mm, 105 * mm, 10 * mm, 58 * mm, 3 * mm, fill=1, stroke=1)
            label(c, "MAKE A MARK", 30 * mm, 87 * mm, 62 * mm, SKY)
            label(c, "MAKE NO MARK", 118 * mm, 87 * mm, 62 * mm, LILAC)
        else:
            draw_card(c, 69 * mm, cy, 62 * mm, 47 * mm, "@")
            draw_card(c, 141 * mm, cy, 62 * mm, 47 * mm)
            label(c, "MARK HERE", 42 * mm, 91 * mm, 54 * mm, PALE_GREEN, GREEN)
            label(c, "CARD HERE", 114 * mm, 91 * mm, 54 * mm, PALE_GREEN, GREEN)
    elif art == "detective_rule":
        c.setFillColor(colors.HexColor("#E8D5B7"))
        c.setStrokeColor(NAVY)
        c.rect(28 * mm, 91 * mm, 154 * mm, 79 * mm, fill=1, stroke=1)
        draw_card(c, 68 * mm, 134 * mm, 44 * mm, 32 * mm, "*")
        c.setStrokeColor(GREEN)
        c.setLineWidth(4)
        c.line(91 * mm, 134 * mm, 116 * mm, 134 * mm)
        label(c, "SOMETHING", 119 * mm, 129 * mm, 50 * mm, PALE_GREEN, GREEN)
        c.setStrokeColor(PURPLE)
        c.setDash(5, 4)
        c.roundRect(47 * mm, 99 * mm, 42 * mm, 24 * mm, 4 * mm, fill=0, stroke=1)
        c.setDash()
        label(c, "NO EXAMPLE TO USE", 105 * mm, 104 * mm, 68 * mm, WHITE, PURPLE, 7)
        base.draw_mira(c, 27 * mm, 101 * mm, 0.8)
    elif art == "treasure_reveal":
        c.setFillColor(colors.HexColor("#A56C42"))
        c.setStrokeColor(NAVY)
        c.setLineWidth(3)
        c.roundRect(57 * mm, 153 * mm, 96 * mm, 21 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#8B5A37"))
        c.setStrokeColor(NAVY)
        c.setLineWidth(3)
        c.roundRect(54 * mm, 96 * mm, 102 * mm, 61 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(YELLOW)
        c.roundRect(66 * mm, 114 * mm, 78 * mm, 30 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(base.font("bold"), 11)
        c.drawCentredString(cx, 129 * mm, "THERE IS NO NOTHING")
        for index in range(5):
            star(c, 62 * mm + index * 22 * mm, 169 * mm, 5 * mm)
        base.draw_mira(c, 35 * mm, 91 * mm, 0.9)
        base.draw_pip(c, 174 * mm, 103 * mm, 0.9)
    elif art == "fair_play":
        c.setFillColor(PALE_GREEN)
        c.setStrokeColor(GREEN)
        c.setLineWidth(3)
        c.roundRect(28 * mm, 91 * mm, 112 * mm, 78 * mm, 10 * mm, fill=1, stroke=1)
        for index, word in enumerate(("SHOW", "SAY", "DRAW", "RECORD")):
            x = 50 * mm + (index % 2) * 60 * mm
            y = 143 * mm - (index // 2) * 35 * mm
            label(c, word, x - 20 * mm, y - 5 * mm, 40 * mm, WHITE, INK, 7)
        c.setStrokeColor(GREY)
        c.setDash(6, 4)
        c.line(151 * mm, 86 * mm, 151 * mm, 176 * mm)
        c.setDash()
        label(c, "NO MADE-UP EXAMPLE", 156 * mm, 126 * mm, 43 * mm, WHITE, GREY, 6)
    elif art == "final_spot":
        draw_room(c, final=True)
    elif art == "final_answers":
        draw_room(c, final=True)
        for number, x, y in ((1, 91, 114), (2, 129, 130), (3, 67, 164), (4, 165, 145)):
            marker(c, number, x * mm, y * mm)
    elif art in ("sort_challenge", "sort_answers"):
        items = (("BOX", 34), ("BELL", 79), ("CARD", 124), ("NO EXAMPLE", 169))
        for word, x in items:
            label(c, word, (x - 19) * mm, 157 * mm, 38 * mm, SKY if word != "NO EXAMPLE" else LILAC, INK, 6.5)
        base.draw_box(c, 34 * mm, 133 * mm, 0.28)
        draw_bell(c, 79 * mm, 134 * mm, 0.25)
        draw_card(c, 124 * mm, 134 * mm, 26 * mm, 20 * mm)
        c.setStrokeColor(PURPLE)
        c.setDash(4, 3)
        c.roundRect(156 * mm, 124 * mm, 26 * mm, 20 * mm, 3 * mm, fill=0, stroke=1)
        c.setDash()
        if art == "sort_answers":
            c.setStrokeColor(GREEN)
            c.setLineWidth(3)
            for x in (34, 79, 124):
                c.line(x * mm, 121 * mm, 66 * mm, 108 * mm)
            c.setStrokeColor(PURPLE)
            c.line(169 * mm, 121 * mm, 152 * mm, 108 * mm)
        label(c, "SOMETHING TO CHECK", 25 * mm, 93 * mm, 83 * mm, PALE_GREEN, GREEN, 7)
        label(c, "NO EXAMPLE GIVEN", 119 * mm, 93 * mm, 66 * mm, WHITE, PURPLE, 7)
    elif art == "certificate":
        c.setFillColor(WHITE)
        c.setStrokeColor(GREEN)
        c.setLineWidth(4)
        c.roundRect(41 * mm, 91 * mm, 128 * mm, 76 * mm, 8 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(base.font("bold"), 14)
        c.drawCentredString(cx, 151 * mm, "NOTHING-HUNT DETECTIVE")
        c.setStrokeColor(GREY)
        c.line(65 * mm, 122 * mm, 145 * mm, 122 * mm)
        c.setFont(base.font("regular"), 8)
        c.drawCentredString(cx, 113 * mm, "NAME, MARK OR STICKER")
        for index in range(5):
            star(c, 57 * mm + index * 24 * mm, 99 * mm, 5 * mm)
        base.draw_mira(c, 31 * mm, 102 * mm, 0.8)
        base.draw_pip(c, 180 * mm, 111 * mm, 0.8)
    elif art == "game_end":
        base.draw_mira(c, 42 * mm, 104 * mm, 1.2)
        base.draw_pip(c, 166 * mm, 114 * mm, 1.1)
        c.setFillColor(YELLOW)
        c.setStrokeColor(WHITE)
        c.setLineWidth(3)
        c.circle(cx, 129 * mm, 37 * mm, fill=1, stroke=1)
        c.setStrokeColor(NAVY)
        c.line(cx, 92 * mm, cx, 166 * mm)
        c.line(68 * mm, 129 * mm, 142 * mm, 129 * mm)
        c.setFillColor(NAVY)
        c.setFont(base.font("bold"), 24)
        c.drawCentredString(cx, 124 * mm, "ONE")


def page_background(c: canvas.Canvas, kind: str) -> None:
    palette = {
        "cover": NAVY,
        "legal": CREAM,
        "story": CREAM,
        "challenge": colors.HexColor("#FFF1CC"),
        "reveal": PALE_GREEN,
        "reward": LILAC,
        "result": SKY,
        "boundary": colors.HexColor("#F2EFE8"),
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
    c.setSubject("SFT Early Years discovery-led game story")
    c.setKeywords("Smithian Fold Theory, early years, game story, presence, checking")
    for page in book["pages"]:
        kind = page["kind"]
        page_background(c, kind)
        badge_fill = ORANGE if kind in ("cover", "end") else (GREEN if kind in ("reveal", "result") else BLUE)
        base.rounded_label(c, page["badge"], 20 * mm, PAGE - 22 * mm, PAGE - 40 * mm, badge_fill)
        if kind == "cover":
            base.paragraph_in_box(c, page["text"], 18 * mm, PAGE - 75 * mm, PAGE - 36 * mm, 36 * mm, 38, 28, WHITE)
            draw_scene(c, page["art"])
            base.paragraph_in_box(c, page["subtext"], 26 * mm, 20 * mm, PAGE - 52 * mm, 18 * mm, 16, 12, WHITE, bold=False)
        elif kind == "legal":
            draw_scene(c, page["art"])
            base.paragraph_in_box(c, page["text"], 28 * mm, 22 * mm, PAGE - 56 * mm, 70 * mm, 12, 9, INK, bold=False)
            base.paragraph_in_box(c, page["subtext"], 26 * mm, 8 * mm, PAGE - 52 * mm, 13 * mm, 10, 8, GREY, bold=False)
        else:
            draw_scene(c, page["art"])
            main_color = WHITE if kind == "end" else INK
            base.paragraph_in_box(c, page["text"], 18 * mm, 24 * mm, PAGE - 36 * mm, 48 * mm, 23, 16, main_color)
            base.paragraph_in_box(c, page["subtext"], 24 * mm, 9 * mm, PAGE - 48 * mm, 14 * mm, 10, 8, WHITE if kind == "end" else GREY, bold=False)
        if page["page"] > 2:
            c.setFillColor(WHITE if kind in ("cover", "end") else GREY)
            c.setFont(base.font("regular"), 8)
            c.drawRightString(PAGE - 9 * mm, 7 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 7, 10, 12, 14, 16, 18, 24, 27, 31):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def generate_accessible_html(book: dict) -> None:
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    parts = [
        "<!doctype html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(book['title'])} - accessible review edition</title>",
        "<style>",
        ":root{--ink:#173042;--navy:#18324a;--sky:#ddf3f7;--cream:#fff9ed;--orange:#c95f17;}",
        "body{margin:0;font-family:system-ui,-apple-system,sans-serif;color:var(--ink);background:#f4f6f7;line-height:1.65;}",
        "header,main,footer{max-width:54rem;margin:auto;padding:1.5rem;}header{background:var(--navy);color:white;}",
        "h1{font-size:clamp(2.2rem,7vw,4rem);line-height:1.05;margin:.3rem 0;}.page{background:white;margin:1.5rem 0;padding:1.5rem;border-radius:1rem;border:.15rem solid #aac2cc;}",
        ".badge{display:inline-block;font-weight:800;background:var(--sky);padding:.35rem .7rem;border-radius:2rem;}.story{font-size:clamp(1.4rem,4vw,2.1rem);font-weight:750;line-height:1.25;white-space:pre-line;}",
        ".subtext{font-size:1.15rem;}.art{border-left:.35rem solid var(--orange);padding:.6rem 1rem;background:var(--cream);}",
        "@media print{.page{break-after:page;}}", "</style></head><body>", "<header>",
        f"<p>{html.escape(book['stage'])} - Book E01 - Review version {html.escape(book['version'])}</p>",
        f"<h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])}</p>",
        "<p>Written by Maria Smith. This semantic edition includes every challenge, reveal and illustration description.</p>",
        "</header><main>",
    ]
    for page in book["pages"]:
        parts.extend([
            f'<section class="page" aria-labelledby="page-{page["page"]}">',
            f'<p class="badge">{html.escape(page["badge"])}</p>',
            f'<h2 id="page-{page["page"]}">Page {page["page"]}</h2>',
            f'<p class="story">{html.escape(page["text"])}</p>',
            f'<p class="subtext">{html.escape(page["subtext"])}</p>',
            f'<figure class="art" role="img" aria-label="{html.escape(page["alt"], quote=True)}"><figcaption><strong>Illustration description:</strong> {html.escape(page["alt"])}</figcaption></figure>',
            "</section>",
        ])
    parts.extend([
        "</main><footer>",
        "<p>Scientific source: SFT-ROOT-THERE-IS-NO-NOTHING. The child experiences examples before the adult-facing formal account. The result remains limited to what can be presented, stated, recorded or checked.</p>",
        "<p>Review version awaiting Maria Smith's final-publication approval. Copyright 2026 Maria Smith. Licensed CC BY 4.0.</p>",
        "</footer></body></html>",
    ])
    ACCESSIBLE_HTML.write_text("\n".join(parts), encoding="utf-8")


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide - Review version 1.1.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult_guide() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=19 * mm, bottomMargin=20 * mm,
        title="Adult Guide - E01 Something Is Here - Review 1.1.0",
        author="Maria Smith", subject="Adult guidance and answers for E01 review edition 1.1.0",
    )
    doc.build(base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8")), onFirstPage=adult_footer, onLaterPages=adult_footer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-only", action="store_true")
    parser.add_argument("--adult-only", action="store_true")
    args = parser.parse_args()
    base.register_fonts()
    book = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32:
        raise ValueError("E01 version 1.1.0 must contain exactly 32 canonical pages")
    if [page["page"] for page in book["pages"]] != list(range(1, 33)):
        raise ValueError("E01 version 1.1.0 page numbers must be continuous")
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
