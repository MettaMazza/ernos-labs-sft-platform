#!/usr/bin/env python3
"""Render the plain-language 3D-stage E02 review edition 1.0.0."""

from __future__ import annotations

import argparse
import html
import json
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
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E02-ONE-WHOLE-MANY-PARTS" / "1.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E02-One-Whole-Many-Parts-v1.0.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E02-Adult-Guide-v1.0.0.pdf"
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
    "library": GAME / "public" / "art" / "stages" / "e01-stage-06-library-v1.png",
    "e02-keyart": GAME / "public" / "art" / "stages" / "e02-stage-02-whole-room-v1.png",
    "whole-room": GAME / "public" / "art" / "stages" / "e02-stage-02-whole-room-v1.png",
    "count-bridge": GAME / "public" / "art" / "stages" / "e02-stage-03-count-bridge-v1.png",
    "part-gate": GAME / "public" / "art" / "stages" / "e02-stage-04-part-gate-v1.png",
    "carry-room": GAME / "public" / "art" / "stages" / "e02-stage-05-rebuild-room-v1.png",
    "match-table": GAME / "public" / "art" / "stages" / "e02-stage-06-match-table-v1.png",
    "gap-gate": GAME / "public" / "art" / "stages" / "e02-stage-07-checking-room-v1.png",
    "extra-gate": GAME / "public" / "art" / "stages" / "e02-stage-07-checking-room-v1.png",
    "holding-dial": GAME / "public" / "art" / "stages" / "e02-stage-07-checking-room-v1.png",
    "final-workshop": GAME / "public" / "art" / "stages" / "e02-stage-03-count-bridge-v1.png",
    "balcony": GAME / "public" / "art" / "stages" / "e02-stage-08-balcony-v1.png",
}

SPRITES = {name: GAME / "public" / "art" / "characters" / "individual" / (f"{name}-v1.png" if name in ("mira", "pax") else f"{name}.png") for name in ("mira", "tavi", "sol", "pax")}
IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32:
        raise ValueError("E02 1.0.0 must contain exactly 32 pages")
    if [page["page"] for page in book["pages"]] != list(range(1, 33)):
        raise ValueError("E02 page sequence is not contiguous")
    return book


def rounded_label(c: canvas.Canvas, text: str, x: float, y: float, width: float, fill: colors.Color) -> None:
    c.setFillColor(fill)
    c.roundRect(x, y, width, 10 * mm, 5 * mm, fill=1, stroke=0)
    c.setFillColor(NAVY if fill != NAVY else WHITE)
    c.setFont(base.font("bold"), 8.2)
    c.drawCentredString(x + width / 2, y + 3.2 * mm, text)


PART_COLORS = (colors.HexColor("#6FD4D0"), colors.HexColor("#FFD35C"), colors.HexColor("#8E6BC4"), colors.HexColor("#EF816D"))


def draw_quartered_lantern(c: canvas.Canvas, cx: float, cy: float, radius: float, filled: int = 4, alternate: bool = False) -> None:
    """Draw one exact four-part lantern; `filled` controls how many parts remain."""
    c.saveState()
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.5)
    for index, angle in enumerate((0, 90, 180, 270)):
        if index < filled:
            fill = (BLUE, GOLD)[index % 2] if alternate else PART_COLORS[index]
        else:
            fill = colors.HexColor("#FFF9EA")
        c.setFillColor(fill)
        c.wedge(cx - radius, cy - radius, cx + radius, cy + radius, angle, 90, fill=1, stroke=1)
    c.setFillColor(colors.Color(1, 1, 1, alpha=.14))
    c.circle(cx, cy, radius * .58, fill=1, stroke=0)
    c.setStrokeColor(GOLD)
    c.setLineWidth(2.4)
    c.circle(cx, cy, radius, fill=0, stroke=1)
    c.restoreState()


def draw_gap_lantern(c: canvas.Canvas, cx: float, cy: float, radius: float) -> None:
    draw_quartered_lantern(c, cx, cy, radius, filled=3)


def draw_extra_triangle(c: canvas.Canvas, cx: float, cy: float, size: float) -> None:
    c.saveState()
    c.setFillColor(colors.HexColor("#EF816D"))
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.5)
    path = c.beginPath()
    path.moveTo(cx, cy + size)
    path.lineTo(cx - size, cy - size)
    path.lineTo(cx + size, cy - size)
    path.close()
    c.drawPath(path, fill=1, stroke=1)
    c.restoreState()


def draw_footprint(c: canvas.Canvas, cx: float, cy: float, fill: colors.Color) -> None:
    c.saveState()
    c.setFillColor(fill)
    c.ellipse(cx - 3.2 * mm, cy - 5 * mm, cx + 3.2 * mm, cy + 3 * mm, fill=1, stroke=0)
    for dx, dy, radius in ((-3, 4, 1.4), (0, 5, 1.6), (3, 4, 1.35)):
        c.circle(cx + dx * mm, cy + dy * mm, radius * mm, fill=1, stroke=0)
    c.restoreState()


def draw_partition_choices(c: canvas.Canvas, x: float, y: float, reveal: bool) -> None:
    centers = (x + 47 * mm, x + 91 * mm, x + 135 * mm)
    radius = 13 * mm
    draw_gap_lantern(c, centers[0], y, radius)
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.setFillColor(colors.HexColor("#6FD4D0"))
    c.circle(centers[1] - 4 * mm, y, radius * .78, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#8E6BC4"))
    c.circle(centers[1] + 4 * mm, y, radius * .78, fill=1, stroke=1)
    c.restoreState()
    draw_quartered_lantern(c, centers[2], y, radius)
    if reveal:
        c.saveState()
        c.setStrokeColor(GOLD)
        c.setLineWidth(4)
        c.circle(centers[2], y, radius + 3 * mm, fill=0, stroke=1)
        c.restoreState()


def draw_pair(c: canvas.Canvas, cx: float, cy: float, equal: bool) -> None:
    sizes = (7 * mm, 7 * mm) if equal else (9 * mm, 5 * mm)
    for offset, size, fill in ((-10 * mm, sizes[0], BLUE), (10 * mm, sizes[1], GOLD)):
        c.setFillColor(fill)
        c.setStrokeColor(NAVY)
        c.setLineWidth(1.4)
        c.circle(cx + offset, cy, size, fill=1, stroke=1)


def draw_lantern_part_card(c: canvas.Canvas, cx: float, cy: float, part: int, size: float = 18 * mm) -> None:
    c.saveState()
    c.setFillColor(CREAM)
    c.setStrokeColor(NAVY)
    c.setLineWidth(1.2)
    c.roundRect(cx - size / 2, cy - size / 2, size, size, 2.5 * mm, fill=1, stroke=1)
    radius = size * .36
    starts = {1: 90, 2: 0, 3: 180, 4: 270}
    c.setFillColor(PART_COLORS[part - 1])
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.4)
    c.wedge(cx - radius, cy - radius, cx + radius, cy + radius, starts[part], 90, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(base.font("bold"), 7)
    c.drawCentredString(cx, cy - size * .41, "1")
    c.restoreState()


def draw_addition_equation(c: canvas.Canvas, x: float, y: float, answer: str) -> None:
    positions = (x + 18 * mm, x + 53 * mm, x + 88 * mm, x + 123 * mm)
    for index, cx in enumerate(positions, 1):
        draw_lantern_part_card(c, cx, y, index)
        if index < 4:
            c.setFillColor(WHITE)
            c.setFont(base.font("bold"), 18)
            c.drawCentredString(cx + 17.5 * mm, y - 2 * mm, "+")
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 18)
    c.drawCentredString(x + 142 * mm, y - 2 * mm, "=")
    c.setFillColor(GOLD)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.6)
    c.roundRect(x + 151 * mm, y - 10 * mm, 24 * mm, 20 * mm, 3 * mm, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont(base.font("bold"), 17)
    c.drawCentredString(x + 163 * mm, y - 3 * mm, answer)


def draw_page_diagram(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    number = page["page"]
    if number == 4:
        draw_quartered_lantern(c, x + 92 * mm, y + 57 * mm, 20 * mm)
    elif number == 5:
        draw_quartered_lantern(c, x + 132 * mm, y + 62 * mm, 27 * mm)
    elif number == 6:
        draw_quartered_lantern(c, x + 42 * mm, y + 60 * mm, 13 * mm)
        for index, cx in enumerate((x + 73 * mm, x + 84 * mm, x + 95 * mm, x + 106 * mm)):
            c.setFillColor(PART_COLORS[index]); c.setStrokeColor(NAVY); c.setLineWidth(1.1)
            c.roundRect(cx - 4 * mm, y + 56 * mm, 8 * mm, 8 * mm, 2 * mm, fill=1, stroke=1)
        c.setFillColor(CREAM); c.setStrokeColor(GOLD); c.setLineWidth(2.2)
        c.roundRect(x + 118 * mm, y + 43 * mm, 17 * mm, 34 * mm, 6 * mm, fill=1, stroke=1)
        draw_quartered_lantern(c, x + 155 * mm, y + 60 * mm, 13 * mm)
    elif number in (7, 8):
        draw_gap_lantern(c, x + 47 * mm, y + 66 * mm, 12 * mm)
        draw_quartered_lantern(c, x + 91 * mm, y + 66 * mm, 12 * mm)
        draw_quartered_lantern(c, x + 135 * mm, y + 66 * mm, 12 * mm)
        draw_extra_triangle(c, x + 150 * mm, y + 73 * mm, 5 * mm)
        if number == 8:
            c.setStrokeColor(GOLD); c.setLineWidth(4)
            c.circle(x + 91 * mm, y + 66 * mm, 15 * mm, fill=0, stroke=1)
    elif number in (11, 12, 13):
        tile_x = (x + 51 * mm, x + 79 * mm, x + 107 * mm, x + 135 * mm)
        for index, cx in enumerate(tile_x):
            draw_footprint(c, cx, y + 50 * mm, GREEN if number in (11, 13, 29) else colors.HexColor("#EF816D"))
            if index == 2 and number in (12, 13):
                draw_footprint(c, cx + 5 * mm, y + 58 * mm, colors.HexColor("#EF816D"))
    elif number in (14, 15, 16, 17):
        draw_partition_choices(c, x, y + 68 * mm, reveal=number == 17)
    elif number in (18, 19):
        for index, cx in enumerate((x + 94 * mm, x + 113 * mm, x + 132 * mm, x + 151 * mm)):
            c.setFillColor(PART_COLORS[index]); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
            c.roundRect(cx - 7 * mm, y + 49 * mm, 14 * mm, 14 * mm, 3 * mm, fill=1, stroke=1)
    elif number == 20:
        for index, cx in enumerate((x + 65 * mm, x + 84 * mm, x + 103 * mm, x + 122 * mm)):
            c.setFillColor(PART_COLORS[index]); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
            c.roundRect(cx - 7 * mm, y + 49 * mm, 14 * mm, 14 * mm, 3 * mm, fill=1, stroke=1)
    elif number in (21, 22):
        draw_pair(c, x + 55 * mm, y + 58 * mm, True)
        draw_pair(c, x + 128 * mm, y + 58 * mm, False)
    elif number == 23:
        draw_quartered_lantern(c, x + 92 * mm, y + 61 * mm, 26 * mm, filled=3)
    elif number == 24:
        draw_quartered_lantern(c, x + 92 * mm, y + 61 * mm, 26 * mm)
    elif number == 25:
        draw_quartered_lantern(c, x + 82 * mm, y + 61 * mm, 24 * mm)
        draw_extra_triangle(c, x + 132 * mm, y + 58 * mm, 8 * mm)
    elif number in (26, 27):
        draw_quartered_lantern(c, x + 76 * mm, y + 61 * mm, 24 * mm, filled=2)
        for index, (cx, cy) in enumerate(((x + 130 * mm, y + 67 * mm), (x + 145 * mm, y + 55 * mm))):
            c.setFillColor(PART_COLORS[index + 2]); c.setStrokeColor(NAVY); c.setLineWidth(1.4)
            c.roundRect(cx - 6 * mm, cy - 6 * mm, 12 * mm, 12 * mm, 3 * mm, fill=1, stroke=1)
    elif number == 28:
        draw_addition_equation(c, x, y + 58 * mm, "?")
    elif number == 29:
        draw_addition_equation(c, x, y + 58 * mm, "4")
    elif number == 30:
        for index, cx in enumerate((x + 28 * mm, x + 50 * mm, x + 72 * mm, x + 94 * mm), 1):
            draw_lantern_part_card(c, cx, y + 58 * mm, index, 16 * mm)
        c.setFillColor(WHITE)
        c.setFont(base.font("bold"), 16)
        c.drawCentredString(x + 116 * mm, y + 56 * mm, "->")
        draw_quartered_lantern(c, x + 150 * mm, y + 58 * mm, 22 * mm)
    elif number == 31:
        draw_addition_equation(c, x, y + 72 * mm, "4")
        c.setFillColor(WHITE)
        c.setFont(base.font("bold"), 12)
        c.drawCentredString(x + 92 * mm, y + 42 * mm, "4 PARTS  ->  1 WHOLE LANTERN")
        draw_quartered_lantern(c, x + 92 * mm, y + 24 * mm, 13 * mm)
    elif number == 32:
        draw_quartered_lantern(c, x + 92 * mm, y + 58 * mm, 26 * mm, alternate=True)


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
    c.drawImage(image(ART["e02-keyart"]), 0, 0, width=PAGE, height=PAGE, preserveAspectRatio=False, mask="auto")
    c.setFillColor(colors.Color(0.02, .04, .10, alpha=.68))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    for position, name in zip((0.04, 0.27, 0.50, 0.73), ("mira", "tavi", "sol", "pax")):
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
    c.setKeywords("Smithian Fold Theory, early years, whole, parts, counting")
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
    c.drawString(20 * mm, 9 * mm, "SFT E02 Adult Guide · Review version 1.0.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult() -> None:
    doc = SimpleDocTemplate(str(ADULT_PDF), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=19*mm, bottomMargin=20*mm, title="Adult Guide · E02 · Review 1.0.0", author="Maria Smith")
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
