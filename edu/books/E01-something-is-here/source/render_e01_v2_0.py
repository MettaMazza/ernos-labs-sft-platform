#!/usr/bin/env python3
"""Render E01 2.0.0 as a paper-native illustrated picture book."""

from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[4]
BOOK_DIR = Path(__file__).resolve().parents[1]
SOURCE = BOOK_DIR / "source" / "book-v2.0.0.json"
ART_DIR = BOOK_DIR / "art" / "v2.0.0" / "story"
EMOJI_DIR = ROOT / "edu" / "assets" / "openmoji" / "16.0.0" / "color" / "png-512"
RELEASE_DIR = ROOT / "output" / "pdf" / "edu" / "SFT-EDU-E01-SOMETHING-IS-HERE" / "2.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E01-Something-Is-Here-v2.0.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible" / "student-book-v2.0.0.html"

PAGE = 210 * mm
NAVY = colors.HexColor("#101A33")
INK = colors.HexColor("#1E2B42")
CREAM = colors.HexColor("#FFF7E7")
GOLD = colors.HexColor("#FFD45A")
TEAL = colors.HexColor("#54C9C5")
PURPLE = colors.HexColor("#76519B")
WHITE = colors.white

SCENES = {
    "cover": ART_DIR / "e01-cover-v2.0.0.png",
    "meet": ART_DIR / "e01-opening-meet-v2.0.0.png",
    "note": ART_DIR / "e01-note-arrives-v2.0.0.png",
    "box": ART_DIR / "e01-box-rug-v2.0.0.png",
    "nori": ART_DIR / "e01-meet-nori-v2.0.0.png",
    "paper-room": ART_DIR / "e01-paper-room-v2.0.0.png",
    "curtain": ART_DIR / "e01-curtain-nook-v2.0.0.png",
    "curtain-reveal": ART_DIR / "e01-curtain-reveal-v2.0.0.png",
    "shelves": ART_DIR / "e01-two-shelves-v2.0.0.png",
    "library": ART_DIR / "e01-library-ending-v2.0.0.png",
}

EMOJI = {
    "note": EMOJI_DIR / "1F4DD.png",
    "map": EMOJI_DIR / "1F5FA.png",
    "book": EMOJI_DIR / "1F4D5.png",
    "box": EMOJI_DIR / "1F4E6.png",
    "teddy": EMOJI_DIR / "1F9F8.png",
    "bell": EMOJI_DIR / "1F514.png",
    "blank": EMOJI_DIR / "2B1C.png",
    "door": EMOJI_DIR / "1F6AA.png",
    "star": EMOJI_DIR / "2B50.png",
    "pencil": EMOJI_DIR / "270F.png",
}

IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def register_fonts() -> tuple[str, str]:
    regular = ROOT / "edu" / "games" / "companion-adventures" / "node_modules" / "@vercel" / "og" / "dist" / "noto-sans-v27-latin-regular.ttf"
    if regular.exists():
        pdfmetrics.registerFont(TTFont("SFTNoto", str(regular)))
        return "SFTNoto", "Helvetica-Bold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = register_fonts()


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if len(pages) != 32 or [page["page"] for page in pages] != list(range(1, 33)):
        raise ValueError("E01 v2.0.0 must contain exactly 32 contiguous pages")
    return book


def draw_crop(c: canvas.Canvas, path: Path) -> None:
    reader = image(path)
    iw, ih = reader.getSize()
    scale = max(PAGE / iw, PAGE / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(reader, (PAGE - dw) / 2, (PAGE - dh) / 2, width=dw, height=dh, mask="auto")


def draw_paper(c: canvas.Canvas, seed: int) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE, PAGE, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#F4E8CB"))
    for index in range(28):
        x = ((index * 71 + seed * 29) % 199 + 5) * mm
        y = ((index * 43 + seed * 17) % 199 + 5) * mm
        r = (0.4 + (index % 3) * 0.25) * mm
        c.circle(x, y, r, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor("#E3C887"))
    c.setLineWidth(1)
    c.roundRect(8 * mm, 8 * mm, PAGE - 16 * mm, PAGE - 16 * mm, 7 * mm, fill=0, stroke=1)


def wrap_lines(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    output: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            output.append("")
            continue
        words = paragraph.split()
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
                current = candidate
            else:
                output.append(current)
                current = word
        output.append(current)
    return output


def draw_text(c: canvas.Canvas, text: str, *, x: float, top: float, width: float, size: float = 18, colour=WHITE,
              font: str = REGULAR, leading: float | None = None, max_lines: int | None = None) -> float:
    leading = leading or size * 1.23
    lines = wrap_lines(text, font, size, width)
    if max_lines and len(lines) > max_lines:
        raise ValueError(f"Text does not fit allotted lines: {text}")
    c.setFillColor(colour)
    c.setFont(font, size)
    y = top
    for line in lines:
        if line:
            c.drawString(x, y, line)
        y -= leading
    return y


def draw_story_text(c: canvas.Canvas, page: dict) -> None:
    # The generated scenes reserve calm dark space for type, so the words can sit
    # directly in the illustration like a picture book instead of inside UI.
    heading = page.get("heading")
    top = PAGE - 14 * mm
    if heading:
        draw_text(c, heading, x=13 * mm, top=top, width=168 * mm, size=24, colour=GOLD, font=BOLD, max_lines=2)
        top -= 18 * mm if len(heading) < 26 else 26 * mm
    # A one-point navy shadow keeps the letters readable while leaving the art open.
    draw_text(c, page["text"], x=13.5 * mm, top=top - .5 * mm, width=168 * mm, size=18.5, colour=NAVY, leading=23, max_lines=7)
    draw_text(c, page["text"], x=13 * mm, top=top, width=168 * mm, size=18.5, colour=WHITE, leading=23, max_lines=7)


def draw_page_number(c: canvas.Canvas, number: int, dark: bool) -> None:
    c.setFillColor(WHITE if dark else INK)
    c.setFont(BOLD, 8)
    c.drawCentredString(PAGE / 2, 5.5 * mm, str(number))


def emoji_position(spec: dict) -> tuple[float, float, float]:
    size = spec["size"] * PAGE
    x = spec["x"] * PAGE - size / 2
    y = PAGE - spec["y"] * PAGE - size / 2
    return x, y, size


def draw_emoji(c: canvas.Canvas, spec: dict) -> None:
    x, y, size = emoji_position(spec)
    c.drawImage(image(EMOJI[spec["id"]]), x, y, width=size, height=size, mask="auto")
    if label := spec.get("label"):
        c.setFont(BOLD, 9.5)
        ly = y + size + 3 * mm
        c.setFillColor(NAVY)
        c.drawCentredString(x + size / 2 + .45 * mm, ly - .45 * mm, label)
        c.setFillColor(CREAM)
        c.drawCentredString(x + size / 2, ly, label)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.4)
        half = min(size * .34, pdfmetrics.stringWidth(label, BOLD, 9.5) * .6)
        c.line(x + size / 2 - half, ly - 2.2 * mm, x + size / 2 + half, ly - 2.2 * mm)


def draw_magic_stars(c: canvas.Canvas, count: int) -> None:
    if not count:
        return
    positions = [(154, 84), (169, 93), (180, 78), (163, 67), (184, 58)]
    for index in range(count):
        x, y = positions[index]
        size = 11 * mm
        c.drawImage(image(EMOJI["star"]), x * mm - size / 2, y * mm - size / 2, width=size, height=size, mask="auto")


def draw_cover(c: canvas.Canvas, book: dict) -> None:
    draw_crop(c, SCENES["cover"])
    c.setFillColor(GOLD)
    c.setFont(BOLD, 10)
    c.drawCentredString(PAGE / 2, PAGE - 15 * mm, "A STAR ROOMS ADVENTURE · BOOK 1")
    c.setFillColor(WHITE)
    c.setFont(BOLD, 31)
    c.drawCentredString(PAGE / 2, PAGE - 37 * mm, book["title"])
    c.setFillColor(GOLD)
    c.setFont(BOLD, 20)
    c.drawCentredString(PAGE / 2, PAGE - 53 * mm, book["subtitle"])
    c.setFillColor(WHITE)
    c.setFont(BOLD, 12)
    c.drawCentredString(PAGE / 2, 12 * mm, "Maria Smith")


def draw_title(c: canvas.Canvas, book: dict, page: dict) -> None:
    draw_paper(c, 2)
    c.setFillColor(NAVY)
    c.setFont(BOLD, 30)
    c.drawCentredString(PAGE / 2, PAGE - 43 * mm, book["title"])
    c.setFillColor(PURPLE)
    c.setFont(BOLD, 18)
    c.drawCentredString(PAGE / 2, PAGE - 58 * mm, book["subtitle"])
    size = 35 * mm
    for idx, emoji_id in enumerate(("note", "star", "door")):
        c.drawImage(image(EMOJI[emoji_id]), (43 + idx * 47) * mm, PAGE - 111 * mm, width=size, height=size, mask="auto")
    draw_text(c, page["subtext"], x=28 * mm, top=PAGE - 133 * mm, width=154 * mm, size=13.5, colour=INK, leading=19, max_lines=7)
    c.setFillColor(colors.HexColor("#5A6473"))
    c.setFont(REGULAR, 8.5)
    c.drawCentredString(PAGE / 2, 16 * mm, "CC BY 4.0 text · OpenMoji items CC BY-SA 4.0 · review copy")


def draw_spot_note(c: canvas.Canvas) -> None:
    draw_paper(c, 7)
    draw_text(c, "Can you find the note?", x=16 * mm, top=PAGE - 21 * mm, width=178 * mm, size=25, colour=INK, font=BOLD)
    draw_text(c, "Point to the note Mia found.", x=16 * mm, top=PAGE - 37 * mm, width=178 * mm, size=18, colour=PURPLE)
    choices = [("map", "MAP", 38), ("book", "BOOK", 87), ("note", "NOTE", 136)]
    for emoji_id, label, x_mm in choices:
        c.setFillColor(colors.HexColor("#F1E3BF"))
        c.circle((x_mm + 18) * mm, 92 * mm, 25 * mm, fill=1, stroke=0)
        c.drawImage(image(EMOJI[emoji_id]), x_mm * mm, 74 * mm, width=36 * mm, height=36 * mm, mask="auto")
        c.setFillColor(INK)
        c.setFont(BOLD, 13)
        c.drawCentredString((x_mm + 18) * mm, 123 * mm, label)
    c.setFillColor(PURPLE)
    c.setFont(BOLD, 12)
    c.drawCentredString(PAGE / 2, 28 * mm, "Say its name before you turn the page.")


def draw_teddy_trail(c: canvas.Canvas) -> None:
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(6)
    c.setLineCap(1)
    path = c.beginPath()
    path.moveTo(82 * mm, 61 * mm)
    path.curveTo(104 * mm, 55 * mm, 101 * mm, 92 * mm, 129 * mm, 91 * mm)
    path.curveTo(153 * mm, 90 * mm, 149 * mm, 62 * mm, 171 * mm, 56 * mm)
    c.drawPath(path, fill=0, stroke=1)
    c.setFillColor(CREAM)
    for x, y in ((103, 71), (127, 92), (151, 75)):
        c.circle(x * mm, y * mm, 4 * mm, fill=1, stroke=0)
    c.restoreState()
    c.setFillColor(CREAM)
    c.setFont(BOLD, 11)
    c.drawCentredString(170 * mm, 44 * mm, "RUG")


def draw_word_activity(c: canvas.Canvas) -> None:
    draw_paper(c, 20)
    draw_text(c, "A word appears", x=16 * mm, top=PAGE - 20 * mm, width=178 * mm, size=25, colour=INK, font=BOLD)
    draw_text(c, "Point from left to right. Say each letter, then say the whole word.", x=16 * mm, top=PAGE - 37 * mm, width=178 * mm, size=17.5, colour=PURPLE)
    letters = "NOTHING"
    for index, letter in enumerate(letters):
        cx = (27 + index * 26) * mm
        cy = 105 * mm + math.sin(index * 1.1) * 7 * mm
        c.setFillColor((TEAL, GOLD, colors.HexColor("#F39A58"), PURPLE)[index % 4])
        c.circle(cx, cy, 11 * mm, fill=1, stroke=0)
        c.setFillColor(NAVY if index != 3 else WHITE)
        c.setFont(BOLD, 24)
        c.drawCentredString(cx, cy - 3.3 * mm, letter)
        if index < len(letters) - 1:
            c.setStrokeColor(colors.HexColor("#D4B765"))
            c.setLineWidth(2)
            c.line(cx + 11 * mm, cy, cx + 15 * mm, 105 * mm + math.sin((index + 1) * 1.1) * 7 * mm)
    c.setFillColor(INK)
    c.setFont(BOLD, 22)
    c.drawCentredString(PAGE / 2, 59 * mm, "NOTHING")
    c.setFont(REGULAR, 14)
    c.drawCentredString(PAGE / 2, 45 * mm, "You can see the word. It is not a secret object.")


def draw_final_match(c: canvas.Canvas) -> None:
    draw_paper(c, 29)
    draw_text(c, "Match the clues", x=16 * mm, top=PAGE - 20 * mm, width=178 * mm, size=25, colour=INK, font=BOLD)
    draw_text(c, "Trace each gold trail. Say the word at the end.", x=16 * mm, top=PAGE - 37 * mm, width=178 * mm, size=17.5, colour=PURPLE)
    rows = [("box", "EMPTY"), ("bell", "QUIET"), ("blank", "BLANK"), ("teddy", "HIDDEN")]
    for index, (emoji_id, word) in enumerate(rows):
        y = (139 - index * 31) * mm
        c.drawImage(image(EMOJI[emoji_id]), 29 * mm, y - 11 * mm, width=22 * mm, height=22 * mm, mask="auto")
        c.setStrokeColor(GOLD)
        c.setLineWidth(3)
        path = c.beginPath()
        path.moveTo(56 * mm, y)
        path.curveTo(87 * mm, y + (7 if index % 2 == 0 else -7) * mm, 112 * mm, y - (7 if index % 2 == 0 else -7) * mm, 143 * mm, y)
        c.drawPath(path, fill=0, stroke=1)
        c.setFillColor(INK)
        c.setFont(BOLD, 17)
        c.drawString(149 * mm, y - 2.5 * mm, word)


def draw_activity(c: canvas.Canvas, page: dict) -> bool:
    activity = page.get("activity")
    if activity == "spot-note":
        draw_spot_note(c)
        return True
    if activity == "nothing-word":
        draw_word_activity(c)
        return True
    if activity == "final-match":
        draw_final_match(c)
        return True
    return False


def render_page(c: canvas.Canvas, book: dict, page: dict) -> None:
    number = page["page"]
    if page["kind"] == "cover":
        draw_cover(c, book)
        return
    if page["kind"] == "title":
        draw_title(c, book, page)
        draw_page_number(c, number, False)
        return
    if draw_activity(c, page):
        draw_page_number(c, number, False)
        return

    scene = page["scene"]
    if scene == "paper":
        draw_paper(c, number)
        dark = False
    else:
        draw_crop(c, SCENES[scene])
        dark = True
    draw_story_text(c, page)

    for spec in page.get("emoji", []):
        draw_emoji(c, spec)
    if page.get("activity") == "teddy-trail":
        draw_teddy_trail(c)
    draw_page_number(c, number, dark)


def render_pdf(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']}: {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Open Education Early Years picture book")
    for page in book["pages"]:
        render_page(c, book, page)
        c.showPage()
    c.save()


def render_html(book: dict) -> None:
    sections = []
    for page in book["pages"]:
        heading = html.escape(page.get("heading") or f"Page {page['page']}")
        text = html.escape(page.get("text", "")).replace("\n", "<br>")
        subtext = html.escape(page.get("subtext", "")).replace("\n", "<br>")
        alt = html.escape(page["alt"])
        activity_class = " activity-page" if page.get("activity") else ""
        activity_label = '<p class="activity"><strong>This page is a paper activity.</strong></p>' if page.get("activity") else ""
        sections.append(
            f'<section class="page{activity_class}" aria-labelledby="p{page["page"]}">'
            f'<h2 id="p{page["page"]}">Page {page["page"]}: {heading}</h2>'
            f'<figure role="img" aria-label="{alt}"></figure>'
            f'{activity_label}<p>{text}</p><p>{subtext}</p>'
            f'<p class="description"><strong>Picture description:</strong> {alt}</p></section>'
        )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(book['title'])} — accessible review edition {book['version']}</title>
<style>body{{font-family:Arial,sans-serif;line-height:1.6;max-width:48rem;margin:auto;padding:2rem;color:#1e2b42}}section{{border-bottom:1px solid #ddd;padding:1rem 0 2rem}}h1,h2{{line-height:1.2}}figure{{margin:0}}.activity{{background:#fff3c9;padding:1rem;border-left:6px solid #76519b}}.description{{color:#45566f}}</style></head>
<body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])}</p><p>By {html.escape(book['author'])} · Book 1 of 4 · Review edition {book['version']} · ages 3–5</p></header><main>{''.join(sections)}</main></body></html>"""
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    ACCESSIBLE_HTML.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-only", action="store_true", help="Reserved for compatibility")
    args = parser.parse_args()
    _ = args
    book = load_book()
    missing = [path for path in list(SCENES.values()) + list(EMOJI.values()) if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing art: " + ", ".join(map(str, missing)))
    render_pdf(book)
    render_html(book)
    print(STUDENT_PDF)
    print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
