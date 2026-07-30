#!/usr/bin/env python3
"""Render the plain-language 3D-stage E01 review edition 1.5.0."""

from __future__ import annotations

import argparse
import html
import json
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
SOURCE = BOOK_DIR / "source" / "book-v1.5.0.json"
GAME = ROOT / "edu" / "games" / "companion-adventures"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "1.5.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v1.5.0.pdf"
ADULT_PDF = RELEASE_DIR / "SFT-E01-Adult-Guide-v1.5.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v1.5.0.html"
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
PROPS = {name: GAME / "public" / "art" / "props" / f"{name}.png" for name in ("box", "teddy", "bell", "card", "map")}
IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    if len(book["pages"]) != 32:
        raise ValueError("E01 1.5.0 must contain exactly 32 pages")
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
    """Draw one unmistakable note beside Mira without adding decorative jargon."""
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

    cast = page.get("cast", [])
    positions = {1: [0.12], 2: [0.08, 0.69], 3: [0.03, 0.38, 0.73], 4: [0.01, 0.25, 0.50, 0.74]}.get(len(cast), [])
    if page["page"] in (27, 28):
        positions = [0.03, 0.20, 0.75]
    for position, name in zip(positions, cast):
        sprite_w = (43 if name == "mira" else 31) * mm
        c.drawImage(image(SPRITES[name]), x + position * w, y + 4 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")

    if page["page"] in (4, 5, 26):
        raised = page["page"] in (5, 26)
        draw_note(c, x + (30 if raised else 27) * mm, y + (25 if raised else 6) * mm, raised)

    props = page.get("props", [])
    for index, name in enumerate(props):
        prop_name = "teddy" if name == "teddy-outside" else name
        if prop_name not in PROPS:
            continue
        prop_w = 27 * mm if prop_name != "card" else 22 * mm
        px = x + w * (0.44 + index * .18)
        if page["page"] in (27, 28):
            px = x + w * (0.45 + index * .17)
        py = y + (23 if name == "teddy" and "box" in props else 9) * mm
        c.drawImage(image(PROPS[prop_name]), px, py, width=prop_w, height=prop_w, preserveAspectRatio=True, anchor="c", mask="auto")

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
    c.drawImage(image(ART["observatory"]), 0, 0, width=PAGE, height=PAGE, preserveAspectRatio=False, mask="auto")
    c.setFillColor(colors.Color(0.02, .04, .10, alpha=.68))
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    for position, name in zip((0.06, 0.29, 0.52, 0.75), ("mira", "tavi", "sol", "nori")):
        sprite_w = (52 if name == "mira" else 42) * mm
        c.drawImage(image(SPRITES[name]), position * PAGE, 28 * mm, width=sprite_w, height=sprite_w, preserveAspectRatio=True, anchor="c", mask="auto")
    rounded_label(c, page["badge"], 18 * mm, PAGE - 25 * mm, 174 * mm, GOLD)
    base.paragraph_in_box(c, page["text"], 17 * mm, 139 * mm, 176 * mm, 40 * mm, 38, 27, WHITE)
    base.paragraph_in_box(c, page["subtext"], 19 * mm, 122 * mm, 172 * mm, 15 * mm, 18, 12, colors.HexColor("#FFE8A1"), bold=False)
    c.setFillColor(WHITE)
    c.setFont(base.font("bold"), 9)
    c.drawString(18 * mm, 14 * mm, "Maria Smith · Review edition 1.5.0")


def render_student(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']} · {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Early Years plain-language 3D story adventure, review 1.5.0")
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
    ACCESSIBLE_HTML.write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(book['title'])} · accessible 1.5.0</title><style>body{{font:1.15rem/1.65 system-ui,sans-serif;max-width:52rem;margin:auto;padding:2rem;color:#20314a;background:#fff9ea}}section{{padding:2rem 0;border-bottom:2px solid #c9b98d}}figure{{margin:1rem 0;padding:1rem;border-left:.35rem solid #2f8f76;background:#fff}}h1,h2{{line-height:1.15}}nav a{{margin-right:.7rem}}</style></head><body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])} · Review 1.5.0</p></header><nav aria-label="Page links">{''.join(f'<a href="#page-{n}">{n}</a>' for n in range(1,33))}</nav><main>{''.join(sections)}</main></body></html>''', encoding="utf-8")


def adult_footer(c: canvas.Canvas, doc: SimpleDocTemplate) -> None:
    c.saveState()
    c.setStrokeColor(colors.HexColor("#C5D3D8"))
    c.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    c.setFillColor(GREY)
    c.setFont(base.font("regular"), 8)
    c.drawString(20 * mm, 9 * mm, "SFT E01 Adult Guide · Review version 1.5.0")
    c.drawRightString(A4[0] - 20 * mm, 9 * mm, f"Page {doc.page}")
    c.restoreState()


def render_adult() -> None:
    doc = SimpleDocTemplate(str(ADULT_PDF), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=19*mm, bottomMargin=20*mm, title="Adult Guide · E01 · Review 1.5.0", author="Maria Smith")
    story = base.parse_markdown_to_story(ADULT_GUIDE.read_text(encoding="utf-8"))
    for index, flowable in enumerate(story):
        if getattr(flowable, "getPlainText", lambda: "")() == "Vocabulary rule":
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
