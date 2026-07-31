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


def draw_sequence(c: canvas.Canvas, roles: list[str], x: float, y: float, gap: float = 28 * mm, mark: int | None = None) -> None:
    for index, role in enumerate(roles):
        cx = x + index * gap
        draw_role(c, cx, y, role, 9 * mm)
        if index + 1 < len(roles):
            c.setStrokeColor(WHITE); c.setLineWidth(2)
            c.line(cx + 10 * mm, y, cx + gap - 10 * mm, y)
        if mark == index:
            c.setStrokeColor(colors.HexColor("#EF6F61")); c.setLineWidth(4)
            c.circle(cx, y, 12 * mm, fill=0, stroke=1)


def draw_unknown(c: canvas.Canvas, cx: float, cy: float) -> None:
    c.setFillColor(CREAM); c.setStrokeColor(WHITE); c.setLineWidth(2)
    c.circle(cx, cy, 9 * mm, fill=1, stroke=1)
    c.setFillColor(NAVY); c.setFont(base.font("bold"), 20)
    c.drawCentredString(cx, cy - 2.5 * mm, "?")


def draw_page_diagram(c: canvas.Canvas, page: dict, x: float, y: float, w: float, h: float) -> None:
    number = page["page"]
    cy = y + 62 * mm
    if number in (3, 4, 15, 16, 17):
        roles = ["moon", "sun", "moon", "sun"]
        draw_sequence(c, roles, x + 40 * mm, cy)
        if number == 16:
            draw_unknown(c, x + 152 * mm, cy)
        elif number == 17:
            draw_role(c, x + 152 * mm, cy, "moon", 9 * mm)
    elif number in (6, 7, 8):
        draw_role(c, x + 70 * mm, cy, "moon", 16 * mm)
        draw_role(c, x + 114 * mm, cy, "sun", 16 * mm, dim=number in (6, 7))
    elif number in (9, 10):
        draw_role(c, x + 92 * mm, cy, "moon", 18 * mm)
    elif number == 11:
        draw_role(c, x + 92 * mm, cy, "sun", 18 * mm)
    elif number == 12:
        draw_role(c, x + 92 * mm, cy, "sun", 18 * mm)
        draw_unknown(c, x + 132 * mm, cy)
    elif number in (13, 14):
        draw_sequence(c, ["moon", "sun", "moon"], x + 64 * mm, cy)
    elif number in (18, 19, 20):
        draw_sequence(c, ["moon", "sun", "moon", "moon"], x + 40 * mm, cy, mark=3 if number == 20 else None)
    elif number == 21:
        draw_sequence(c, ["moon", "sun", "moon", "sun"], x + 40 * mm, cy)
    elif number in (22, 23, 24):
        c.setFillColor(CREAM); c.setStrokeColor(WHITE); c.setLineWidth(2)
        c.roundRect(x + 44 * mm, cy - 8 * mm, 28 * mm, 16 * mm, 5 * mm, fill=1, stroke=1)
        c.roundRect(x + 80 * mm, cy - 8 * mm, 28 * mm, 16 * mm, 5 * mm, fill=1, stroke=1)
        c.roundRect(x + 116 * mm, cy - 8 * mm, 28 * mm, 16 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY); c.setFont(base.font("bold"), 10)
        for label, cx in (("OVER", 58), ("UNDER", 94), ("OVER", 130)):
            c.drawCentredString(x + cx * mm, cy - 1.8 * mm, label)
        if number == 24:
            rounded_label(c, "UNDER", x + 148 * mm, cy - 5 * mm, 28 * mm, GOLD)
        elif number == 23:
            draw_unknown(c, x + 162 * mm, cy)
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
            if chosen:
                c.setStrokeColor(GOLD); c.setLineWidth(3)
                c.roundRect(x + 84 * mm, ry - 8 * mm, 80 * mm, 16 * mm, 8 * mm, fill=0, stroke=1)
    elif number in (28, 29):
        draw_role(c, x + 70 * mm, cy, "moon", 14 * mm)
        c.setStrokeColor(WHITE); c.setLineWidth(3); c.line(x + 88 * mm, cy, x + 112 * mm, cy)
        draw_unknown(c, x + 132 * mm, cy) if number == 28 else draw_role(c, x + 132 * mm, cy, "sun", 14 * mm)
    elif number in (30, 31):
        draw_sequence(c, ["star", "leaf", "star"], x + 58 * mm, cy)
        draw_unknown(c, x + 142 * mm, cy) if number == 30 else draw_role(c, x + 142 * mm, cy, "leaf", 9 * mm)


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
