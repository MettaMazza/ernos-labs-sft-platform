#!/usr/bin/env python3
"""Render E01 1.3.0 with words above pictures and hidden scene codes."""

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

import render_e01 as base
import render_e01_v1_1 as game
import render_e01_v1_2 as v12


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
OVERLAY_SOURCE = BOOK_DIR / "source" / "book-v1.3.0.json"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.3.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.3.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.3.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.3.0.html"
ADULT_GUIDE = BOOK_DIR / "adult-guide.md"

PAGE = base.PAGE
NAVY = base.NAVY
INK = base.INK
WHITE = base.WHITE
CREAM = base.CREAM
SKY = base.SKY
GREEN = base.GREEN
PALE_GREEN = base.PALE_GREEN
YELLOW = base.YELLOW
ORANGE = base.ORANGE
GREY = base.GREY
BLUE = base.BLUE
PURPLE = game.PURPLE

ART_SHIFT = -50 * mm


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


def emoji(c: canvas.Canvas, name: str, x: float, y: float, size: float, label: str | None = None) -> None:
    drawing = v12.drawing_for(name)
    scale = size / max(drawing.width, drawing.height)
    c.saveState()
    c.translate(x - drawing.width * scale / 2, y - drawing.height * scale / 2)
    c.scale(scale, scale)
    renderPDF.draw(drawing, c, 0, 0)
    c.restoreState()
    if label:
        v12.label_box(c, label, x, y + size / 2 + 6 * mm)


def empty_frame(c: canvas.Canvas, x: float, y: float, width: float, height: float, label: str | None = None) -> None:
    c.setStrokeColor(PURPLE)
    c.setLineWidth(2)
    c.setDash(5, 4)
    c.roundRect(x - width / 2, y - height / 2, width, height, 4 * mm, fill=0, stroke=1)
    c.setDash()
    if label:
        v12.label_box(c, label, x, y + height / 2 + 6 * mm, max(51 * mm, min(72 * mm, width + 25 * mm)))


HIDDEN_CODES = {
    "ROOMSTAR": (126, 112, -8),
    "BOXCLUE": (105, 132, 5),
    "QUIETWINGS": (70, 105, -7),
    "BLANKEDGE": (70, 145, 7),
    "CURTAINMAP": (105, 137, -4),
    "TWODOORS": (140, 143, 4),
}


def hidden_code(c: canvas.Canvas, text: str) -> None:
    x_mm, y_mm, angle = HIDDEN_CODES[text]
    c.saveState()
    c.translate(x_mm * mm, y_mm * mm)
    c.rotate(angle)
    c.setFillColor(CREAM if text == "CURTAINMAP" else NAVY)
    c.setFont(base.font("bold"), 4.2)
    c.drawCentredString(0, -1.2 * mm, text)
    c.restoreState()


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
        v12.label_box(c, "THE WORD NOTHING", PAGE / 2, 149 * mm, 74 * mm)


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
        v12.label_box(c, "CURTAIN", 105 * mm, 181 * mm, 42 * mm)
        v12.label_box(c, "TOYS PARTLY HIDDEN", 105 * mm, 123 * mm, 72 * mm)


def doors_scene(c: canvas.Canvas, mode: str) -> None:
    if mode == "a":
        emoji(c, "door", 45 * mm, 130 * mm, 45 * mm, "DOOR A")
        emoji(c, "card", 105 * mm, 130 * mm, 23 * mm, "CARD SHOWN")
        emoji(c, "mira", 165 * mm, 130 * mm, 30 * mm, "MIRA LOOKED")
        return
    emoji(c, "door", 64 * mm, 139 * mm, 54 * mm, "DOOR A")
    emoji(c, "door", 146 * mm, 139 * mm, 54 * mm, "DOOR B")
    if mode == "challenge":
        emoji(c, "card", 64 * mm, 111 * mm, 21 * mm)
    if mode == "challenge":
        empty_frame(c, 146 * mm, 111 * mm, 29 * mm, 27 * mm)
    elif mode == "b":
        emoji(c, "mira", 84 * mm, 88 * mm, 28 * mm, "MIRA LOOKED")
        empty_frame(c, 151 * mm, 105 * mm, 29 * mm, 27 * mm, "NO CARD SHOWN YET")


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
        v12.label_box(c, "CURTAIN", 147 * mm, 142 * mm, 39 * mm)
        v12.label_box(c, "TOY PARTLY HIDDEN", 147 * mm, 116 * mm, 68 * mm)
    else:
        emoji(c, "mira", 35 * mm, 88 * mm, 19 * mm)
        emoji(c, "pip", 177 * mm, 88 * mm, 18 * mm)


def sort_scene(c: canvas.Canvas, labelled: bool) -> None:
    if not labelled:
        v12.label_box(c, "OBJECTS TO LOOK AT", 79 * mm, 181 * mm, 75 * mm)
        v12.label_box(c, "NO OBJECT SHOWN YET", 169 * mm, 181 * mm, 72 * mm)
    positions = (("box", "BOX", 35), ("bell", "BELL", 82), ("card", "CARD", 129))
    for name, text, x in positions:
        emoji(c, name, x * mm, 137 * mm, 23 * mm, text if labelled else None)
    empty_frame(c, 176 * mm, 137 * mm, 25 * mm, 23 * mm, "EMPTY FRAME" if labelled else None)
    if labelled:
        c.setStrokeColor(GREEN)
        c.setLineWidth(2.2)
        c.roundRect(18 * mm, 108 * mm, 132 * mm, 39 * mm, 7 * mm, fill=0, stroke=1)
        c.setStrokeColor(PURPLE)
        c.roundRect(153 * mm, 108 * mm, 46 * mm, 39 * mm, 7 * mm, fill=0, stroke=1)
        v12.label_box(c, "OBJECTS TO LOOK AT", 79 * mm, 181 * mm, 75 * mm)
        v12.label_box(c, "NO OBJECT SHOWN YET", 169 * mm, 181 * mm, 72 * mm)


def detective_rule(c: canvas.Canvas) -> None:
    emoji(c, "card", 70 * mm, 151 * mm, 26 * mm, "CARD SHOWN")
    emoji(c, "check", 140 * mm, 151 * mm, 26 * mm, "SOMETHING TO LOOK AT")
    empty_frame(c, 70 * mm, 105 * mm, 27 * mm, 24 * mm, "NO OBJECT SHOWN YET")
    emoji(c, "mira", 140 * mm, 105 * mm, 26 * mm, "KEEP BOTH PATHS")


def opening_mystery(c: canvas.Canvas) -> None:
    emoji(c, "mira", 34 * mm, 143 * mm, 27 * mm, "MIRA")
    emoji(c, "pip", 177 * mm, 143 * mm, 24 * mm, "PIP")
    emoji(c, "box", 70 * mm, 128 * mm, 35 * mm, "PARCEL")
    emoji(c, "map", 111 * mm, 143 * mm, 39 * mm, "FIVE-STAR MAP")
    for index in range(5):
        c.setFillColor(WHITE)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.2)
        c.circle((84 + index * 14) * mm, 105 * mm, 5 * mm, fill=1, stroke=1)
    emoji(c, "door", 156 * mm, 112 * mm, 29 * mm, "MYSTERY DOORS")


def map_rules(c: canvas.Canvas) -> None:
    emoji(c, "map", PAGE / 2, 153 * mm, 46 * mm, "THE CLUE MAP")
    for index in range(5):
        x = 77 * mm + index * 14 * mm
        c.setFillColor(WHITE)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.2)
        c.circle(x, 121 * mm, 5 * mm, fill=1, stroke=1)
    actions = (("eye", "LOOK"), ("speech", "SAY"), ("book", "TURN"), ("check", "CHECK"))
    for index, (name, label) in enumerate(actions):
        emoji(c, name, (39 + index * 44) * mm, 83 * mm, 19 * mm, label)


def star_door_opens(c: canvas.Canvas) -> None:
    emoji(c, "mira", 34 * mm, 130 * mm, 25 * mm, "MIRA")
    emoji(c, "pip", 177 * mm, 130 * mm, 23 * mm, "PIP")
    c.setFillColor(colors.HexColor("#FFF4C7"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.roundRect(65 * mm, 96 * mm, 80 * mm, 72 * mm, 7 * mm, fill=1, stroke=1)
    emoji(c, "star", 105 * mm, 161 * mm, 18 * mm, "FIVE STARS LIT")
    emoji(c, "door", 86 * mm, 124 * mm, 38 * mm, "DOOR A")
    emoji(c, "door", 124 * mm, 124 * mm, 38 * mm, "DOOR B")


def draw_scene(c: canvas.Canvas, art: str, shift: float = ART_SHIFT) -> None:
    c.saveState()
    c.translate(0, shift)
    if art == "review_stamp":
        emoji(c, "book", 70 * mm, 132 * mm, 43 * mm, "OPEN BOOK")
        emoji(c, "magnifier", 142 * mm, 132 * mm, 43 * mm, "REVIEW 1.3.0")
    elif art == "opening_mystery":
        opening_mystery(c)
    elif art == "map_rules":
        map_rules(c)
    elif art == "star_door_opens":
        star_door_opens(c)
    elif art == "detective_rule":
        detective_rule(c)
    elif art == "box_reveal":
        v12.emoji_grid(c, [("mira", "MIRA LOOKED"), ("box", "BOX"), ("pip", "PIP WATCHED"), ("teddy", "TOY OUTSIDE"), ("card", "EMPTY INSIDE")], labelled=True, top=153 * mm)
    elif art == "bell_reveal":
        v12.emoji_grid(c, [("mira", "MIRA LISTENED"), ("ear", "LISTENING"), ("bell", "BELL STAYED STILL"), ("pip", "PIP WAITED")], labelled=True, top=151 * mm)
        hidden_code(c, "QUIETWINGS")
    elif art == "treasure_reveal":
        v12.emoji_grid(c, [("mira", "MIRA"), ("gift", "TREASURE"), ("star", "FIVE CLUES"), ("pip", "PIP")], labelled=True, top=146 * mm)
        hidden_code(c, "TWODOORS")
    else:
        v12.draw_scene(c, art)
    c.restoreState()


def page_background(c: canvas.Canvas, kind: str) -> None:
    game.page_background(c, kind)


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(book["title"])
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years picture-led game story with hidden reading codes")
    c.setKeywords("Smithian Fold Theory, early years, emoji, hidden codes, checking")
    for page in book["pages"]:
        kind = page["kind"]
        page_background(c, kind)
        badge_fill = ORANGE if kind in ("cover", "end") else (GREEN if kind in ("reveal", "result") else BLUE)
        base.rounded_label(c, page["badge"], 20 * mm, PAGE - 22 * mm, PAGE - 40 * mm, badge_fill)
        main_color = WHITE if kind in ("cover", "end") else INK
        sub_color = WHITE if kind in ("cover", "end") else GREY
        if kind == "cover":
            base.paragraph_in_box(c, page["text"], 18 * mm, 153 * mm, PAGE - 36 * mm, 29 * mm, 38, 27, main_color)
            base.paragraph_in_box(c, page["subtext"], 24 * mm, 139 * mm, PAGE - 48 * mm, 12 * mm, 16, 12, sub_color, bold=False)
            draw_scene(c, page["art"], -9 * mm)
        elif kind == "legal":
            base.paragraph_in_box(c, page["text"], 25 * mm, 137 * mm, PAGE - 50 * mm, 44 * mm, 11, 8, INK, bold=False)
            base.paragraph_in_box(c, page["subtext"], 25 * mm, 125 * mm, PAGE - 50 * mm, 10 * mm, 10, 8, GREY, bold=False)
            draw_scene(c, page["art"], -60 * mm)
        else:
            base.paragraph_in_box(c, page["text"], 18 * mm, 149 * mm, PAGE - 36 * mm, 34 * mm, 21, 14, main_color)
            base.paragraph_in_box(c, page["subtext"], 23 * mm, 134 * mm, PAGE - 46 * mm, 13 * mm, 10, 7, sub_color, bold=False)
            draw_scene(c, page["art"])
        if page["page"] > 2:
            c.setFillColor(WHITE if kind in ("cover", "end") else GREY)
            c.setFont(base.font("regular"), 8)
            c.drawRightString(PAGE - 9 * mm, 7 * mm, str(page["page"]))
        c.bookmarkPage(f"page-{page['page']}")
        if page["page"] in (1, 3, 7, 10, 12, 14, 16, 18, 24, 27, 31):
            c.addOutlineEntry(page["badge"].title(), f"page-{page['page']}", level=0)
        c.showPage()
    c.save()


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide - Review version 1.3.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult_guide() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(ADULT_PDF), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=19 * mm, bottomMargin=20 * mm,
        title="Adult Guide - E01 Something Is Here - Review 1.3.0",
        author="Maria Smith",
        subject="Adult guidance, answers and hidden-code companion notes for E01 review 1.3.0",
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
    if not v12.OPENMOJI.is_dir():
        raise FileNotFoundError("OpenMoji dependency missing; run npm install in edu/games/companion-adventures")
    book = load_book()
    if len(book["pages"]) != 32:
        raise ValueError("E01 version 1.3.0 must contain exactly 32 pages")

    v12.emoji = emoji
    v12.empty_frame = empty_frame
    v12.word_blocks = word_blocks
    v12.curtain_scene = curtain_scene
    v12.doors_scene = doors_scene
    v12.final_scene = final_scene
    v12.sort_scene = sort_scene
    v12.code_ticket = hidden_code

    if not args.adult_only:
        render_student(book)
        game.ACCESSIBLE_HTML = ACCESSIBLE_HTML
        game.generate_accessible_html(book)
    if not args.student_only:
        render_adult_guide()
    print(STUDENT_PDF)
    print(ADULT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
