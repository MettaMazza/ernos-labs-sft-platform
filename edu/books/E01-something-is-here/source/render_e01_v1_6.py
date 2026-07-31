#!/usr/bin/env python3
"""Render the plain-language 3D-stage E01 review edition 1.6.0."""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, SimpleDocTemplate

import render_e01 as base


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v1.6.0.json"
GAME = ROOT / "edu" / "games" / "companion-adventures"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.6.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.6.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.6.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.6.0.html"
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
    "keyart": GAME / "public" / "art" / "world" / "e01-observatory-keyart-v1.png",
    "observatory": GAME / "public" / "art" / "stages" / "e01-stage-01-observatory-v1.png",
    "bell": GAME / "public" / "art" / "stages" / "e01-stage-02-bell-gallery-v1.png",
    "paper": GAME / "public" / "art" / "stages" / "e01-stage-03-paper-room-v1.png",
    "curtain": GAME / "public" / "art" / "stages" / "e01-stage-04-curtain-passage-v1.png",
    "doors": GAME / "public" / "art" / "stages" / "e01-stage-05-star-door-v1.png",
    "library": GAME / "public" / "art" / "stages" / "e01-stage-06-library-v1.png",
}

SPRITES = {name: GAME / "public" / "art" / "characters" / "individual" / ("mira-v1.png" if name == "mira" else f"{name}.png") for name in ("mira", "tavi", "sol", "nori")}
PROPS = {name: GAME / "public" / "art" / "props" / f"{name}.png" for name in ("box", "teddy", "bell", "card", "door", "empty-frame", "map")}
IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32:
        raise ValueError("E01 1.6.0 must contain exactly 32 pages")
    if [page["page"] for page in book["pages"]] != list(range(1, 33)):
        raise ValueError("E01 page sequence is not contiguous")
    return book


def rounded_label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill: colors.Color) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, 10 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY if fill != NAVY else WHITE)
    c.setFont(base.font("bold"), 8.2)
    c.drawCentredString(x + width / 2, y + 3.2 * mm, text)


def draw_note(c: canvas.Canvas, x: float, y: float, raised: bool) -> None:
    """Draw one unmistakable note beside Mia without adding decorative jargon."""
    c.saveState()
    c.translate(x, y)
    c.rotate(-5 if raised else 7)
    c.setFillColor(colors.HexColor("#FFFDF4"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    note_w, note_h = (18, 13) if raised else (20, 14)
    c.roundRect(0, 0, note_w * mm, note_h * mm, 2 * mm, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#6D4A91"))
    c.setLineWidth(1)
    for line_y, line_w in ((9, 13), (6.5, 14), (4, 10)):
        c.line(3 * mm, line_y * mm, line_w * mm, line_y * mm)
    c.restoreState()


def draw_folded_note(c: canvas.Canvas, x: float, y: float) -> None:
    """Draw the original note folded shut for the library ending."""
    c.saveState()
    c.translate(x, y)
    c.rotate(-5)
    c.setFillColor(colors.HexColor("#FFFDF4"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.roundRect(0, 0, 18 * mm, 11 * mm, 1.6 * mm, fill=1, stroke=1)
    c.setStrokeColor(PURPLE)
    c.line(1.5 * mm, 9.5 * mm, 9 * mm, 4.5 * mm)
    c.line(16.5 * mm, 9.5 * mm, 9 * mm, 4.5 * mm)
    c.restoreState()


def draw_star(c: canvas.Canvas, cx: float, cy: float, radius: float, lit: bool) -> None:
    """Draw a reliable five-point star without depending on a symbol font."""
    points: list[tuple[float, float]] = []
    for index in range(10):
        angle = math.radians(90 + index * 36)
        point_radius = radius if index % 2 == 0 else radius * .44
        points.append((cx + math.cos(angle) * point_radius, cy + math.sin(angle) * point_radius))
    path = c.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    path.close()
    c.setFillColor(GOLD if lit else NAVY)
    c.setStrokeColor(GOLD if lit else WHITE)
    c.setLineWidth(1.1)
    c.drawPath(path, fill=1, stroke=1)


def star_count(page_number: int) -> int:
    """Return the number of clues visibly completed on a story page."""
    if page_number < 9:
        return 0
    if page_number < 12:
        return 1
    if page_number < 15:
        return 2
    if page_number < 18:
        return 3
    if page_number < 21:
        return 4
    return 5


def draw_star_progress(c: canvas.Canvas, page_number: int, x: float, y: float, w: float, h: float) -> None:
    """Keep the five clue stars in one stable place and show only earned stars."""
    if page_number < 6 or page_number > 30:
        return
    completed = star_count(page_number)
    bar_w, bar_h = 58 * mm, 13 * mm
    bx, by = x + w - bar_w - 4 * mm, y + h - bar_h - 4 * mm
    c.setFillColor(colors.Color(.04, .08, .16, alpha=.92))
    c.setStrokeColor(WHITE)
    c.setLineWidth(.8)
    c.roundRect(bx, by, bar_w, bar_h, 6.5 * mm, fill=1, stroke=1)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 5.5)
    c.drawString(bx + 4 * mm, by + 5.1 * mm, "CLUES")
    for index in range(5):
        draw_star(c, bx + (20 + index * 8.2) * mm, by + 6.6 * mm, 3.2 * mm, index < completed)


def draw_letter_box(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Add the simple letter box required by the opening action."""
    lx, ly = x + .80 * w, y + .55 * h
    c.setFillColor(colors.HexColor("#E8B64F"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.1)
    c.roundRect(lx, ly, 25 * mm, 8 * mm, 2 * mm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#70431F"))
    c.roundRect(lx + 2.5 * mm, ly + 2.2 * mm, 20 * mm, 2.7 * mm, 1.1 * mm, fill=1, stroke=0)


def draw_hidden_wall_map(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Keep the five-star map hidden until it appears on page 6."""
    px, py, pw, ph = x + .37 * w, y + .52 * h, .225 * w, .31 * h
    c.setFillColor(colors.HexColor("#35244D"))
    c.setStrokeColor(colors.HexColor("#B98645"))
    c.setLineWidth(1.5)
    c.roundRect(px, py, pw, ph, 3 * mm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#1A2743"))
    c.roundRect(px + 3 * mm, py + 3 * mm, pw - 6 * mm, ph - 6 * mm, 2 * mm, fill=1, stroke=0)
    draw_star(c, px + pw / 2, py + ph / 2, 5 * mm, False)


def draw_closed_parcel(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Cover the background's open box with the closed first-clue parcel."""
    px, py, pw, ph = x + .31 * w, y + .09 * h, 38 * mm, 27 * mm
    c.setFillColor(colors.Color(.04, .08, .16, alpha=.82))
    c.ellipse(px - 4 * mm, py - 3 * mm, px + pw + 4 * mm, py + ph + 4 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#C88A49"))
    c.setStrokeColor(CREAM)
    c.setLineWidth(1.2)
    c.roundRect(px, py, pw, ph, 2.2 * mm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#F3D39B"))
    c.rect(px + 15.5 * mm, py, 7 * mm, ph, fill=1, stroke=0)
    c.rect(px, py + 10 * mm, pw, 5 * mm, fill=1, stroke=0)


def draw_parcel_arrow(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Point from the map area to the closed parcel without adding prose."""
    start_x, start_y = x + .55 * w, y + .61 * h
    end_x, end_y = x + .43 * w, y + .36 * h
    c.setStrokeColor(GOLD)
    c.setFillColor(GOLD)
    c.setLineWidth(3)
    c.line(start_x, start_y, end_x, end_y)
    angle = math.atan2(end_y - start_y, end_x - start_x)
    for offset in (-.55, .55):
        tip_x = end_x - math.cos(angle + offset) * 6 * mm
        tip_y = end_y - math.sin(angle + offset) * 6 * mm
        c.line(end_x, end_y, tip_x, tip_y)


def draw_teddy_box_state(c: canvas.Canvas, page_number: int, x: float, y: float, w: float, h: float) -> None:
    """Stage the teddy inside the box first, then clearly outside it."""
    library = page_number in (27, 28)
    box_x = x + (.37 if library else .30) * w
    box_y = y + (.06 if library else .05) * h
    box_size = 40 * mm
    c.setFillColor(colors.Color(.05, .09, .17, alpha=.76))
    c.ellipse(box_x - 5 * mm, box_y - 2 * mm, box_x + 70 * mm, box_y + 35 * mm, fill=1, stroke=0)
    if page_number == 7:
        teddy_x, teddy_y, teddy_size = box_x + 11 * mm, box_y + 18 * mm, 19 * mm
        c.drawImage(image(PROPS["teddy"]), teddy_x, teddy_y, width=teddy_size, height=teddy_size, preserveAspectRatio=True, anchor="c", mask="auto")
        c.drawImage(image(PROPS["box"]), box_x, box_y, width=box_size, height=box_size, preserveAspectRatio=True, anchor="c", mask="auto")
        return
    c.drawImage(image(PROPS["box"]), box_x, box_y, width=box_size, height=box_size, preserveAspectRatio=True, anchor="c", mask="auto")
    teddy_x = x + (.58 if library else .56) * w
    teddy_y = y + .07 * h
    teddy_size = 30 * mm
    c.drawImage(image(PROPS["teddy"]), teddy_x, teddy_y, width=teddy_size, height=teddy_size, preserveAspectRatio=True, anchor="c", mask="auto")


def draw_card_comparison(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Show exactly two cards: one marked and one blank."""
    board_x, board_y = x + .30 * w, y + .18 * h
    board_w, board_h = .41 * w, .48 * h
    c.setFillColor(colors.Color(.04, .08, .16, alpha=.94))
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.roundRect(board_x, board_y, board_w, board_h, 5 * mm, fill=1, stroke=1)
    card_size = 27 * mm
    left_x, right_x = x + .35 * w, x + .52 * w
    card_y = y + .29 * h
    for card_x in (left_x, right_x):
        c.drawImage(image(PROPS["card"]), card_x, card_y, width=card_size, height=card_size, preserveAspectRatio=True, anchor="c", mask="auto")
    c.setStrokeColor(PURPLE)
    c.setLineWidth(3)
    c.line(left_x + 7 * mm, card_y + 10 * mm, left_x + 20 * mm, card_y + 17 * mm)


def draw_dim_letter_tiles(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Keep the wall tiles dormant before they light on page 16."""
    c.setFillColor(colors.Color(.03, .06, .12, alpha=.80))
    c.setStrokeColor(colors.HexColor("#B98645"))
    c.setLineWidth(1)
    c.roundRect(x + .18 * w, y + .65 * h, .58 * w, .18 * h, 3 * mm, fill=1, stroke=1)


def draw_open_curtain(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Turn the static closed-curtain art into an unmistakable open reveal."""
    opening_x, opening_y = x + .37 * w, y + .26 * h
    opening_w, opening_h = .30 * w, .48 * h
    c.setFillColor(NAVY)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.roundRect(opening_x, opening_y, opening_w, opening_h, 5 * mm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#6E1830"))
    left = c.beginPath()
    left.moveTo(opening_x, opening_y)
    left.lineTo(opening_x + 9 * mm, opening_y + 7 * mm)
    left.lineTo(opening_x + 12 * mm, opening_y + opening_h)
    left.lineTo(opening_x, opening_y + opening_h)
    left.close()
    c.drawPath(left, fill=1, stroke=0)
    right = c.beginPath()
    right.moveTo(opening_x + opening_w, opening_y)
    right.lineTo(opening_x + opening_w - 9 * mm, opening_y + 7 * mm)
    right.lineTo(opening_x + opening_w - 12 * mm, opening_y + opening_h)
    right.lineTo(opening_x + opening_w, opening_y + opening_h)
    right.close()
    c.drawPath(right, fill=1, stroke=0)
    for sx, sy in ((.43, .66), (.51, .60), (.58, .68), (.48, .48)):
        draw_star(c, x + sx * w, y + sy * h, 1.4 * mm, True)
    teddy_size = 27 * mm
    c.drawImage(image(PROPS["teddy"]), x + .47 * w, y + .28 * h, width=teddy_size, height=teddy_size, preserveAspectRatio=True, anchor="c", mask="auto")


def draw_open_star_door(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Make the large Star Door read as an open portal behind the two small doors."""
    px, py = x + .40 * w, y + .48 * h
    pw, ph = .22 * w, .39 * h
    c.setFillColor(colors.HexColor("#07142F"))
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.ellipse(px, py, px + pw, py + ph, fill=1, stroke=1)
    for sx, sy in ((.44, .70), (.49, .79), (.55, .67), (.51, .59)):
        draw_star(c, x + sx * w, y + sy * h, 1.3 * mm, True)


def draw_open_small_doors(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Show the two shelves behind Door A and Door B."""
    for index, left_fraction in enumerate((.28, .57)):
        ax, ay = x + left_fraction * w, y + .18 * h
        aw, ah = .16 * w, .37 * h
        c.setFillColor(colors.HexColor("#111D38"))
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.6)
        c.roundRect(ax, ay, aw, ah, 5 * mm, fill=1, stroke=1)
        c.setStrokeColor(colors.HexColor("#B98645"))
        c.setLineWidth(2.2)
        c.line(ax + 2 * mm, ay + 12 * mm, ax + aw - 2 * mm, ay + 12 * mm)
        c.setFillColor(colors.HexColor("#334B79"))
        panel = c.beginPath()
        if index == 0:
            panel.moveTo(ax, ay + 1 * mm)
            panel.lineTo(ax - 8 * mm, ay + 5 * mm)
            panel.lineTo(ax - 6 * mm, ay + ah - 4 * mm)
            panel.lineTo(ax, ay + ah)
        else:
            panel.moveTo(ax + aw, ay + 1 * mm)
            panel.lineTo(ax + aw + 8 * mm, ay + 5 * mm)
            panel.lineTo(ax + aw + 6 * mm, ay + ah - 4 * mm)
            panel.lineTo(ax + aw, ay + ah)
        panel.close()
        c.drawPath(panel, fill=1, stroke=0)
        if index == 0:
            c.drawImage(image(PROPS["card"]), ax + 6 * mm, ay + 12 * mm, width=16 * mm, height=16 * mm, preserveAspectRatio=True, anchor="c", mask="auto")


def draw_empty_map_stand(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Hide the background map until Mia files it on page 29."""
    px, py, pw, ph = x + .455 * w, y + .43 * h, .205 * w, .29 * h
    c.setFillColor(colors.HexColor("#53331F"))
    c.setStrokeColor(colors.HexColor("#C4924E"))
    c.setLineWidth(1.4)
    c.roundRect(px, py, pw, ph, 3 * mm, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#15213A"))
    c.roundRect(px + 3 * mm, py + 3 * mm, pw - 6 * mm, ph - 6 * mm, 2 * mm, fill=1, stroke=0)
    draw_star(c, px + pw / 2, py + ph / 2, 5 * mm, False)


def draw_closed_mail_hatch(c: canvas.Canvas, x: float, y: float, w: float, h: float) -> None:
    """Hide the next parcel until its page-31 arrival."""
    px, py, pw, ph = x + .79 * w, y + .17 * h, .17 * w, .30 * h
    c.setFillColor(colors.HexColor("#172544"))
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.roundRect(px, py, pw, ph, 5 * mm, fill=1, stroke=1)
    draw_star(c, px + pw / 2, py + ph / 2, 5 * mm, False)


def draw_library_state(c: canvas.Canvas, page_number: int, x: float, y: float, w: float, h: float) -> None:
    if page_number in (2, 27, 28):
        draw_empty_map_stand(c, x, y, w, h)
    if page_number <= 30:
        draw_closed_mail_hatch(c, x, y, w, h)
    if page_number == 29:
        draw_folded_note(c, x + .48 * w, y + .37 * h)
        c.drawImage(image(PROPS["bell"]), x + .73 * w, y + .13 * h, width=18 * mm, height=18 * mm, preserveAspectRatio=True, anchor="c", mask="auto")


def draw_scene_state(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    """Apply the visible before-and-after state promised by the page text."""
    page_number = page["page"]
    if page["art"] == "observatory" and 3 <= page_number <= 6:
        draw_letter_box(c, x, y, w, h)
    if page["art"] == "observatory" and 3 <= page_number <= 5:
        draw_hidden_wall_map(c, x, y, w, h)
    if 3 <= page_number <= 6:
        draw_closed_parcel(c, x, y, w, h)
    if page_number == 6:
        draw_parcel_arrow(c, x, y, w, h)
    if page_number in (7, 8, 9, 27, 28):
        draw_teddy_box_state(c, page_number, x, y, w, h)
    if page_number == 15:
        draw_card_comparison(c, x, y, w, h)
    if page["art"] == "paper" and 13 <= page_number <= 15:
        draw_dim_letter_tiles(c, x, y, w, h)
    if page_number in (19, 21):
        draw_open_curtain(c, x, y, w, h)
    if 22 <= page_number <= 26:
        draw_open_star_door(c, x, y, w, h)
    if page_number in (23, 24, 25):
        draw_open_small_doors(c, x, y, w, h)
    if page["art"] == "library":
        draw_library_state(c, page_number, x, y, w, h)


LABEL_CALLOUTS = {
    4: {"LETTER BOX": (.87, .59, .70, .79), "NOTE": (.20, .17, .10, .39)},
    6: {"FIVE PALE STARS": (.83, .91, .54, .75), "ARROW TO PARCEL": (.42, .35, .18, .52)},
    9: {"EMPTY BOX": (.39, .22, .19, .49), "TEDDY OUTSIDE": (.64, .22, .66, .51)},
    12: {"NORI LISTENED": (.83, .23, .74, .49), "QUIET BELL STILL HERE": (.50, .56, .35, .80)},
    15: {"MARK AND CARD": (.42, .42, .22, .72), "BLANK CARD": (.59, .42, .72, .72)},
    18: {"WRITTEN WORD": (.50, .72, .23, .88), "SEVEN LETTERS": (.50, .67, .22, .53)},
    21: {"CURTAIN OPEN": (.50, .63, .22, .83), "TEDDY VISIBLE AGAIN": (.54, .38, .74, .59)},
    22: {"FIVE STARS LIT": (.83, .91, .55, .76), "STAR DOOR OPEN": (.51, .68, .25, .77)},
    24: {"A · CARD ON SHELF": (.36, .34, .20, .67), "B · EMPTY SHELF": (.65, .34, .76, .67)},
    25: {"NO OBJECT CALLED NOTHING": (.51, .36, .50, .72)},
    28: {"EMPTY BOX": (.46, .22, .26, .50), "TEDDY OUTSIDE": (.66, .22, .73, .50)},
    29: {"NOTE FOLDED": (.53, .44, .28, .61), "MAP PUT AWAY": (.56, .62, .73, .79)},
}


def draw_callout(c: canvas.Canvas, label: str, target: tuple[float, float], label_at: tuple[float, float], x: float, y: float, w: float, h: float) -> None:
    """Attach a compact label to the named object with a visible leader line."""
    tx, ty = x + target[0] * w, y + target[1] * h
    cx, cy = x + label_at[0] * w, y + label_at[1] * h
    label_w = max(25 * mm, min(58 * mm, stringWidth(label, base.font("bold"), 7) + 8 * mm))
    label_h = 8 * mm
    lx = max(x + 2 * mm, min(cx - label_w / 2, x + w - label_w - 2 * mm))
    ly = max(y + 2 * mm, min(cy - label_h / 2, y + h - label_h - 2 * mm))
    connector_y = ly if ty < ly else ly + label_h
    c.setStrokeColor(WHITE)
    c.setLineWidth(3)
    c.line(lx + label_w / 2, connector_y, tx, ty)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.3)
    c.line(lx + label_w / 2, connector_y, tx, ty)
    c.setFillColor(GOLD)
    c.setStrokeColor(NAVY)
    c.circle(tx, ty, 1.8 * mm, fill=1, stroke=1)
    c.setFillColor(CREAM)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.roundRect(lx, ly, label_w, label_h, 4 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(base.font("bold"), 7)
    c.drawCentredString(lx + label_w / 2, ly + 2.6 * mm, label)


def draw_object_labels(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    callouts = LABEL_CALLOUTS.get(page["page"], {})
    for index, label in enumerate(page.get("labels", [])):
        if label in callouts:
            target_x, target_y, label_x, label_y = callouts[label]
            draw_callout(c, label, (target_x, target_y), (label_x, label_y), x, y, w, h)
            continue
        fallback_y = .82 - index * .12
        draw_callout(c, label, (.50, .50), (.25, fallback_y), x, y, w, h)


def cast_positions(page_number: int, cast_count: int) -> list[float]:
    positions = {1: [.12], 2: [.08, .69], 3: [.03, .38, .73], 4: [.01, .25, .50, .74]}.get(cast_count, [])
    if page_number in (3, 4, 5, 6, 7, 8, 9) and cast_count == 3:
        return [.01, .68, .83]
    if page_number in (15, 19, 20, 21, 23, 24, 25, 27, 28) and cast_count == 4:
        return [.01, .23, .68, .83]
    if page_number in (29, 30, 31, 32) and cast_count == 4:
        return [.01, .22, .47, .65]
    return positions


def draw_stage(c: canvas.Canvas, page: dict) -> None:
    x, y, w, h = 14 * mm, 18 * mm, 182 * mm, 102 * mm
    c.setFillColor(NAVY)
    c.roundRect(x - 1.5 * mm, y - 1.5 * mm, w + 3 * mm, h + 3 * mm, 7 * mm, fill=1, stroke=0)
    c.saveState()
    path = c.beginPath()
    path.roundRect(x, y, w, h, 5.8 * mm)
    c.clipPath(path, stroke=0, fill=0)
    c.drawImage(image(ART[page["art"]]), x, y, width=w, height=h, preserveAspectRatio=True, anchor="c", mask="auto")
    c.saveState()
    c.setFillColor(colors.Color(0.02, 0.05, 0.11, alpha=.18))
    c.rect(x, y, w, h, fill=1, stroke=0)
    c.restoreState()

    draw_scene_state(c, page, x, y, w, h)
    draw_star_progress(c, page["page"], x, y, w, h)

    cast = page.get("cast", [])
    positions = cast_positions(page["page"], len(cast))
    for position, name in zip(positions, cast):
        sprite_w = (43 if name == "mira" else 31) * mm
        c.drawImage(image(SPRITES[name]), x + position * w, y + 4 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")

    if page["page"] in (4, 5, 26):
        raised = page["page"] in (5, 26)
        draw_note(c, x + (30 if raised else 27) * mm, y + (25 if raised else 6) * mm, raised)

    if page.get("letters"):
        letters = page["letters"]
        tile_w = 19 * mm
        start_x = PAGE / 2 - len(letters) * tile_w / 2
        for index, letter in enumerate(letters):
            tx = start_x + index * tile_w
            c.setFillColor((PURPLE, BLUE, GREEN, GOLD, colors.HexColor("#EF816D"), BLUE, PURPLE)[index])
            c.setStrokeColor(WHITE)
            c.setLineWidth(1.2)
            c.roundRect(tx + 1 * mm, y + 65 * mm, 16 * mm, 16 * mm, 3 * mm, fill=1, stroke=1)
            c.setFillColor(NAVY)
            c.setFont(base.font("bold"), 16)
            c.drawCentredString(tx + 9 * mm, y + 70 * mm, letter)

    draw_object_labels(c, page, x, y, w, h)

    code = page.get("code")
    if code:
        c.saveState()
        c.translate(x + w - 14 * mm, y + 9 * mm)
        c.rotate(-7 + (page["page"] % 3) * 5)
        c.setFillColor(CREAM)
        c.setFont(base.font("bold"), 4.2)
        c.drawCentredString(0, 0, code)
        c.restoreState()
    c.restoreState()


def draw_cover(c: canvas.Canvas, page: dict) -> None:
    # Use the character-free room plate. The separate canonical sprites below
    # are the only cast shown on the cover.
    c.drawImage(image(ART["observatory"]), 0, 0, width=PAGE, height=PAGE, preserveAspectRatio=False, mask="auto")
    # The supplied key art contains an older ensemble. Keep its world and lighting,
    # but veil those figures so the four canonical cast sprites are unambiguous.
    c.setFillColor(colors.Color(0.02, .04, .10, alpha=.82))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(colors.Color(.02, .04, .10, alpha=.94))
    c.rect(0, 0, PAGE, 125 * mm, fill=1, stroke=0)
    for position, name in zip((0.06, 0.29, 0.52, 0.75), ("mira", "tavi", "sol", "nori")):
        sprite_w = (52 if name == "mira" else 42) * mm
        c.drawImage(image(SPRITES[name]), position * PAGE, 28 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")
    rounded_label(c, page["badge"], 18 * mm, PAGE - 25 * mm, 174 * mm, GOLD)
    base.paragraph_in_box(c, page["text"], 17 * mm, 139 * mm, 176 * mm, 40 * mm, 38, 27, WHITE)
    base.paragraph_in_box(c, page["subtext"], 19 * mm, 122 * mm, 172 * mm, 15 * mm, 18, 12, colors.HexColor("#FFE8A1"), bold=False)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 9)
    c.drawString(18 * mm, 14 * mm, "Maria Smith · Review edition 1.6.0")


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']} · {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years plain-language 3D story adventure, review 1.6.0")
    c.setKeywords("Smithian Fold Theory, early years, story, observation, nothing")
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
    ACCESSIBLE_HTML.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])} · accessible 1.6.0</title><style>body{{font:1.15rem/1.65 system-ui,sans-serif;max-width:52rem;margin:auto;padding:2rem;color:#20314a;background:#fff9ea}}section{{padding:2rem 0;border-bottom:2px solid #c9b98d}}figure{{margin:1rem 0;padding:1rem;border-left:.35rem solid #2f8f76;background:#fff}}h1,h2{{line-height:1.15}}nav a{{margin-right:.7rem}}</style></head><body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])} · Review 1.6.0</p></header><nav aria-label="Page links">{''.join(f'<a href="#page-{n}">{n}</a>' for n in range(1,33))}</nav><main>{''.join(sections)}</main></body></html>''', encoding="utf-8")


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide · Review version 1.6.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult() -> None:
    doc = SimpleDocTemplate(str(ADULT_PDF), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=19*mm, bottomMargin=20*mm, title="Adult Guide · E01 · Review 1.6.0", author="Maria Smith")
    story = base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    for flowable in story:
        style = getattr(flowable, "style", None)
        if getattr(style, "name", "") in ("SFTH1", "SFTH2", "SFTH3"):
            style.keepWithNext = 1
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
