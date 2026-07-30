#!/usr/bin/env python3
"""Render E01 1.2.0 with clear OpenMoji scenes and labelled reveals."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import PageBreak, SimpleDocTemplate
from svglib.svglib import svg2rlg

import render_e01 as base
import render_e01_v1_1 as game


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
OVERLAY_SOURCE = BOOK_DIR / "source" / "book-v1.2.0.json"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.2.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.2.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.2.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.2.0.html"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"
OPENMOJI = ROOT / "edu" / "games" / "companion-adventures" / "node_modules" / "openmoji" / "color" / "svg"

PAGE = base.PAGE
NAVY = base.NAVY
INK = base.INK
WHITE = base.WHITE
CREAM = base.CREAM
SKY = base.SKY
GREEN = base.GREEN
PALE_GREEN = base.PALE_GREEN
YELLOW = base.YELLOW
CORAL = base.CORAL
PURPLE = game.PURPLE

EMOJI = {
    "mira": "1F467",
    "pip": "1F426",
    "map": "1F5FA",
    "star": "2B50",
    "eye": "1F440",
    "speech": "1F4AC",
    "book": "1F4D6",
    "check": "2705",
    "bed": "1F6CF",
    "window": "1FA9F",
    "books": "1F4DA",
    "lamp": "1F4A1",
    "box": "1F4E6",
    "bell": "1F514",
    "teddy": "1F9F8",
    "card": "1F4C4",
    "feather": "1FAB6",
    "magnifier": "1F50D",
    "ear": "1F442",
    "door": "1F6AA",
    "home": "1F3E0",
    "pencil": "270F",
    "gift": "1F381",
    "medal": "1F3C5",
    "question": "2753",
    "stop": "1F6D1",
}

_DRAWINGS: dict[str, object] = {}


def load_book() -> dict:
    overlay = json.loads(OVERLAY_SOURCE.read_text(encoding="utf-8"))
    base_path = ROOT / overlay["base_source"]
    book = copy.deepcopy(json.loads(base_path.read_text(encoding="utf-8")))
    book["version"] = overlay["version"]
    book["status"] = overlay["status"]
    book["subtitle"] = overlay["subtitle"]
    for page_number, update in overlay["page_updates"].items():
        page = book["pages"][int(page_number) - 1]
        if page["page"] != int(page_number):
            raise ValueError(f"page overlay mismatch at {page_number}")
        page.update(update)
    return book


def drawing_for(name: str):
    if name in _DRAWINGS:
        return _DRAWINGS[name]
    path = OPENMOJI / f"{EMOJI[name]}.svg"
    if not path.is_file():
        raise FileNotFoundError(f"OpenMoji asset missing: {path}")
    drawing = svg2rlg(str(path))
    if drawing is None:
        raise ValueError(f"OpenMoji asset could not be read: {path}")
    _DRAWINGS[name] = drawing
    return drawing


def emoji(c: canvas.Canvas, name: str, x: float, y: float, size: float, label: str | None = None) -> None:
    drawing = drawing_for(name)
    scale = size / max(drawing.width, drawing.height)
    c.saveState()
    c.translate(x - drawing.width * scale / 2, y - drawing.height * scale / 2)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()
    if label:
        label_box(c, label, x, y - size / 2 - 6 * mm)


def label_box(c: canvas.Canvas, text: str, x: float, y: float, width: float | None = None) -> None:
    if width is None:
        width = max(27 * mm, min(58 * mm, (len(text) * 2.15 + 13) * mm))
    c.setFillColor(WHITE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.4)
    c.roundRect(x - width / 2, y - 4.5 * mm, width, 9 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(base.font("bold"), 6.8 if len(text) > 14 else 7.8)
    c.drawCentredString(x, y - 1.8 * mm, text)


def code_ticket(c: canvas.Canvas, text: str) -> None:
    c.setFillColor(YELLOW)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.8)
    c.roundRect(62 * mm, 174 * mm, 86 * mm, 11 * mm, 4 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY)
    c.setFont(base.font("bold"), 8)
    c.drawCentredString(PAGE / 2, 178 * mm, f"BOOK CODE: {text}")


def emoji_grid(c: canvas.Canvas, items: list[tuple[str, str]], labelled: bool = False, top: float = 158 * mm) -> None:
    count = len(items)
    columns = 4 if count > 6 else 3 if count > 4 else 2
    rows = (count + columns - 1) // columns
    x_positions = [PAGE * (index + 1) / (columns + 1) for index in range(columns)]
    row_gap = 50 * mm if rows == 2 else 39 * mm
    y_positions = [top - row * row_gap for row in range(rows)]
    size = 26 * mm if count <= 6 else 21 * mm
    for index, (name, text) in enumerate(items):
        x = x_positions[index % columns]
        y = y_positions[index // columns]
        emoji(c, name, x, y, size, text if labelled else None)


def word_blocks(c: canvas.Canvas, labelled: bool) -> None:
    for index, letter in enumerate("NOTHING"):
        x = 36 * mm + index * 23 * mm
        c.setFillColor((SKY, YELLOW, PALE_GREEN, colors.HexColor("#EEE9F7"), colors.HexColor("#FAD7CB"), SKY, YELLOW)[index])
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.6)
        c.roundRect(x - 9 * mm, 121 * mm, 18 * mm, 18 * mm, 3 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont(base.font("bold"), 18)
        c.drawCentredString(x, 126 * mm, letter)
    emoji(c, "mira", 40 * mm, 159 * mm, 24 * mm)
    emoji(c, "pip", 169 * mm, 159 * mm, 23 * mm)
    if labelled:
        label_box(c, "THE WORD NOTHING", PAGE / 2, 103 * mm, 74 * mm)


def curtain_scene(c: canvas.Canvas, labelled: bool) -> None:
    emoji(c, "mira", 42 * mm, 133 * mm, 30 * mm, "MIRA" if labelled else None)
    emoji(c, "pip", 168 * mm, 133 * mm, 28 * mm, "PIP" if labelled else None)
    c.setFillColor(PURPLE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2.5)
    c.roundRect(72 * mm, 104 * mm, 66 * mm, 69 * mm, 6 * mm, fill=1, stroke=1)
    c.setStrokeColor(colors.HexColor("#D4C9EB"))
    for x in (84, 98, 112, 126):
        c.line(x * mm, 108 * mm, x * mm, 168 * mm)
    emoji(c, "teddy", 94 * mm, 105 * mm, 20 * mm)
    emoji(c, "box", 119 * mm, 105 * mm, 19 * mm)
    if labelled:
        label_box(c, "CURTAIN", 105 * mm, 165 * mm, 42 * mm)
        label_box(c, "TOYS PARTLY HIDDEN", 105 * mm, 96 * mm, 72 * mm)


def empty_frame(c: canvas.Canvas, x: float, y: float, width: float, height: float, label: str | None = None) -> None:
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.setDash(5, 4)
    c.roundRect(x - width / 2, y - height / 2, width, height, 4 * mm, fill=0, stroke=1)
    c.setDash()
    if label:
        label_box(c, label, x, y - height / 2 - 6 * mm, max(51 * mm, min(70 * mm, width + 20 * mm)))


def doors_scene(c: canvas.Canvas, mode: str) -> None:
    emoji(c, "door", 64 * mm, 139 * mm, 54 * mm, "DOOR A")
    emoji(c, "door", 146 * mm, 139 * mm, 54 * mm, "DOOR B")
    if mode in ("challenge", "a"):
        emoji(c, "card", 84 * mm if mode == "a" else 64 * mm, 116 * mm, 21 * mm, "CARD SHOWN" if mode == "a" else None)
    if mode == "a":
        emoji(c, "mira", 113 * mm, 116 * mm, 28 * mm, "MIRA LOOKING")
        label_box(c, "HANDOVER", 96 * mm, 153 * mm, 43 * mm)
    elif mode in ("challenge", "b"):
        if mode == "challenge":
            empty_frame(c, 146 * mm, 122.5 * mm, 29 * mm, 27 * mm)
            return
        emoji(c, "mira", 109 * mm, 112 * mm, 28 * mm, "MIRA LOOKING")
        c.setStrokeColor(PURPLE)
        c.setDash(5, 4)
        c.roundRect(132 * mm, 109 * mm, 29 * mm, 27 * mm, 4 * mm, fill=0, stroke=1)
        c.setDash()
        label_box(c, "EMPTY FRAME", 146 * mm, 102 * mm, 49 * mm)
        label_box(c, "NO CARD SHOWN YET", 146 * mm, 164 * mm, 68 * mm)


def final_scene(c: canvas.Canvas, labelled: bool) -> None:
    emoji(c, "box", 62 * mm, 153 * mm, 27 * mm, "EMPTY BOX" if labelled else None)
    emoji(c, "bell", 147 * mm, 164 * mm, 27 * mm, "STILL BELL" if labelled else None)
    emoji(c, "card", 62 * mm, 111 * mm, 27 * mm, "BLANK CARD" if labelled else None)
    c.setFillColor(PURPLE)
    c.setStrokeColor(NAVY)
    c.setLineWidth(2)
    c.roundRect(130 * mm, 98 * mm, 34 * mm, 36 * mm, 4 * mm, fill=1, stroke=1)
    emoji(c, "teddy", 147 * mm, 99 * mm, 20 * mm)
    if labelled:
        label_box(c, "CURTAIN", 147 * mm, 127 * mm, 39 * mm)
        label_box(c, "TOY PARTLY HIDDEN", 147 * mm, 90 * mm, 68 * mm)
    else:
        emoji(c, "mira", 35 * mm, 91 * mm, 19 * mm)
        emoji(c, "pip", 177 * mm, 91 * mm, 18 * mm)


def sort_scene(c: canvas.Canvas, labelled: bool) -> None:
    positions = (("box", "BOX", 35), ("bell", "BELL", 82), ("card", "CARD", 129))
    for name, text, x in positions:
        emoji(c, name, x * mm, 143 * mm, 23 * mm, text if labelled else None)
    empty_frame(c, 176 * mm, 143 * mm, 25 * mm, 23 * mm, "NOTHING SHOWN" if labelled else None)
    c.setStrokeColor(GREEN)
    c.setLineWidth(2.4)
    if labelled:
        for x in (35, 82, 129):
            c.line(x * mm, 120 * mm, 68 * mm, 103 * mm)
        c.setStrokeColor(PURPLE)
        c.line(176 * mm, 120 * mm, 155 * mm, 103 * mm)
    label_box(c, "OBJECT TO LOOK AT", 68 * mm, 98 * mm, 72 * mm)
    label_box(c, "NOTHING SHOWN YET", 155 * mm, 98 * mm, 70 * mm)


ART_CODES = {
    "room_reveal": "ROOMSTAR",
    "star_one": "BOXCLUE",
    "bell_reveal": "QUIETWINGS",
    "blank_reveal": "BLANKEDGE",
    "curtain_reveal": "CURTAINMAP",
    "treasure_reveal": "TWODOORS",
}


def draw_scene(c: canvas.Canvas, art: str) -> None:
    cx = PAGE / 2
    if art == "game_cover":
        emoji_grid(c, [("mira", ""), ("map", ""), ("pip", ""), ("box", ""), ("bell", ""), ("door", "")], top=117 * mm)
    elif art == "review_stamp":
        emoji(c, "book", 70 * mm, 132 * mm, 43 * mm, "OPEN BOOK")
        emoji(c, "magnifier", 142 * mm, 132 * mm, 43 * mm, "REVIEW 1.2.0")
    elif art == "mystery_map":
        emoji(c, "mira", 45 * mm, 132 * mm, 33 * mm)
        emoji(c, "map", cx, 132 * mm, 54 * mm, "FIND NOTHING")
        emoji(c, "pip", 165 * mm, 132 * mm, 31 * mm)
    elif art == "game_rules":
        emoji_grid(c, [("eye", "SPOT"), ("speech", "SAY"), ("book", "TURN PAGE"), ("check", "CHECK")], labelled=True, top=148 * mm)
    elif art in ("room_spot", "room_reveal"):
        emoji_grid(c, [("mira", "MIRA"), ("pip", "PIP"), ("bed", "BED"), ("window", "WINDOW"), ("books", "BOOKS"), ("lamp", "LAMP"), ("box", "BOX"), ("bell", "BELL")], labelled=art == "room_reveal", top=160 * mm)
    elif art in ("box_challenge", "box_reveal"):
        emoji_grid(c, [("mira", "MIRA LOOKING"), ("box", "BOX"), ("pip", "PIP WATCHING"), ("teddy", "TOY OUTSIDE"), ("card", "EMPTY INSIDE")], labelled=art == "box_reveal", top=153 * mm)
    elif art == "star_one":
        emoji(c, "pip", 55 * mm, 132 * mm, 35 * mm, "PIP")
        emoji(c, "star", cx, 132 * mm, 43 * mm, "CLUE STAR 1")
        emoji(c, "box", 157 * mm, 132 * mm, 35 * mm, "EMPTY BOX")
    elif art in ("bell_challenge", "bell_reveal"):
        emoji_grid(c, [("mira", "MIRA LISTENING"), ("ear", "LISTENING"), ("bell", "BELL STAYED STILL"), ("pip", "PIP WAITING")], labelled=art == "bell_reveal", top=151 * mm)
    elif art in ("blank_challenge", "blank_reveal"):
        emoji_grid(c, [("card", "CARD"), ("feather", "PIP'S FEATHER"), ("magnifier", "MAGNIFYING GLASS"), ("pencil", "PENCIL")], labelled=art == "blank_reveal", top=151 * mm)
    elif art in ("word_hunt", "word_reveal"):
        word_blocks(c, art == "word_reveal")
    elif art in ("curtain_challenge", "curtain_reveal"):
        curtain_scene(c, art == "curtain_reveal")
    elif art == "map_opens":
        emoji_grid(c, [("mira", "MIRA"), ("map", "MAP"), ("star", "FIVE CLUE STARS"), ("door", "DOOR A"), ("door", "DOOR B"), ("pip", "PIP")], labelled=True, top=154 * mm)
    elif art == "doors_challenge":
        doors_scene(c, "challenge")
    elif art == "door_a_reveal":
        doors_scene(c, "a")
    elif art == "door_b_reveal":
        doors_scene(c, "b")
    elif art == "draw_challenge":
        emoji_grid(c, [("card", ""), ("pencil", ""), ("mira", ""), ("pip", "")], labelled=False, top=150 * mm)
    elif art == "draw_reveal":
        emoji_grid(c, [("pencil", "MARK HERE"), ("card", "BLANK CARD HERE")], labelled=True, top=142 * mm)
    elif art == "detective_rule":
        emoji(c, "card", 70 * mm, 151 * mm, 26 * mm, "CARD SHOWN")
        emoji(c, "check", 140 * mm, 151 * mm, 26 * mm, "SOMETHING TO LOOK AT")
        empty_frame(c, 70 * mm, 105 * mm, 27 * mm, 24 * mm, "NOTHING SHOWN YET")
        emoji(c, "mira", 140 * mm, 105 * mm, 26 * mm, "KEEP BOTH PATHS")
    elif art == "treasure_reveal":
        emoji_grid(c, [("mira", "MIRA"), ("gift", "TREASURE"), ("star", "FIVE CLUES"), ("pip", "PIP")], labelled=True, top=146 * mm)
        label_box(c, "THERE IS NO NOTHING", cx, 108 * mm, 82 * mm)
    elif art == "fair_play":
        emoji_grid(c, [("eye", "SHOW"), ("speech", "SAY"), ("pencil", "DRAW"), ("book", "SAVE IN A NOTE"), ("stop", "DO NOT GUESS")], labelled=True, top=151 * mm)
    elif art == "final_spot":
        final_scene(c, False)
    elif art == "final_answers":
        final_scene(c, True)
    elif art == "sort_challenge":
        sort_scene(c, False)
    elif art == "sort_answers":
        sort_scene(c, True)
    elif art == "certificate":
        emoji_grid(c, [("mira", "MIRA"), ("medal", "NOTHING-HUNT DETECTIVE"), ("star", "FIVE CLUES"), ("pip", "PIP")], labelled=True, top=146 * mm)
    elif art == "game_end":
        emoji_grid(c, [("mira", ""), ("gift", "ONE WHOLE"), ("book", "NEXT BOOK"), ("pip", "")], labelled=True, top=145 * mm)
    else:
        raise ValueError(f"unhandled art scene: {art}")
    if art in ART_CODES:
        code_ticket(c, ART_CODES[art])


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(base.GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide - Review version 1.2.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult_guide() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=19 * mm,
        bottomMargin=20 * mm,
        title="Adult Guide - E01 Something Is Here - Review 1.2.0",
        author="Maria Smith",
        subject="Adult guidance, answers and companion-game notes for E01 review 1.2.0",
    )
    story = base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    for index, flowable in enumerate(story):
        if getattr(flowable, "getPlainText", lambda: "")() == "Scientific checks preserved in the adult edition":
            story.insert(index, PageBreak())
            break
    doc.build(story, onFirstPage=adult_footer, onLaterPages=adult_footer)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-only", action="store_true")
    parser.add_argument("--adult-only", action="store_true")
    args = parser.parse_args()
    base.register_fonts()
    if not OPENMOJI.is_dir():
        raise FileNotFoundError("OpenMoji dependency missing; run npm install in edu/games/companion-adventures")
    book = load_book()
    if len(book["pages"]) != 32:
        raise ValueError("E01 version 1.2.0 must contain exactly 32 pages")
    game.RELEASE_DIR = RELEASE_DIR
    game.STUDENT_PDF = STUDENT_PDF
    game.ADULT_PDF = ADULT_PDF
    game.ACCESSIBLE_HTML = ACCESSIBLE_HTML
    game.ADULT_GUIDE = ADULT_GUIDE
    game.draw_scene = draw_scene
    if not args.adult_only:
        game.render_student(book)
        game.generate_accessible_html(book)
    if not args.student_only:
        render_adult_guide()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
