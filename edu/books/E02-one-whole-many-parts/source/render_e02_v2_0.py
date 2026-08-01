#!/usr/bin/env python3
"""Render E02 2.0.0 as a paper-native illustrated picture book."""

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
SOURCE = BOOK_DIR / "source/book-v2.0.0.json"
ART_DIR = BOOK_DIR / "art/v2.0.0/story"
EMOJI_DIR = ROOT / "edu/assets/openmoji/16.0.0/color/png-512"
PART_DIR = ROOT / "edu/assets/openmoji/16.0.0/derived/lantern-parts"
RELEASE_DIR = ROOT / "output/pdf/edu/SFT-EDU-E02-ONE-WHOLE-MANY-PARTS/2.0.0"
STUDENT_PDF = RELEASE_DIR / "SFT-E02-One-Whole-Many-Parts-v2.0.0.pdf"
ACCESSIBLE_HTML = BOOK_DIR / "accessible/student-book-v2.0.0.html"

PAGE = 210 * mm
NAVY = colors.HexColor("#101A33")
INK = colors.HexColor("#1E2B42")
CREAM = colors.HexColor("#FFF7E7")
GOLD = colors.HexColor("#FFD45A")
TEAL = colors.HexColor("#54C9C5")
PURPLE = colors.HexColor("#76519B")
CORAL = colors.HexColor("#F06450")
WHITE = colors.white

SCENES = {
    "cover": ART_DIR / "e02-cover-v2.0.0.png",
    "library": ART_DIR / "e02-library-parcel-v2.0.0.png",
    "small-door": ART_DIR / "e02-small-door-v2.0.0.png",
    "worktable": ART_DIR / "e02-worktable-v2.0.0.png",
    "doorway": ART_DIR / "e02-doorway-parade-v2.0.0.png",
    "two-groups": ART_DIR / "e02-two-groups-v2.0.0.png",
    "balcony": ART_DIR / "e02-balcony-ending-v2.0.0.png",
}

EMOJI = {
    "box": EMOJI_DIR / "1F4E6.png",
    "lantern": EMOJI_DIR / "1F3EE.png",
    "moon": EMOJI_DIR / "1F319.png",
    "sun": EMOJI_DIR / "2600.png",
    "door": EMOJI_DIR / "1F6AA.png",
    "star": EMOJI_DIR / "2B50.png",
    "blank": EMOJI_DIR / "2B1C.png",
    "part-tl": PART_DIR / "lantern-top-left-tile.png",
    "part-tr": PART_DIR / "lantern-top-right-tile.png",
    "part-bl": PART_DIR / "lantern-bottom-left-tile.png",
    "part-br": PART_DIR / "lantern-bottom-right-tile.png",
    "part-tl-tile": PART_DIR / "lantern-top-left-tile.png",
    "part-tr-tile": PART_DIR / "lantern-top-right-tile.png",
    "part-bl-tile": PART_DIR / "lantern-bottom-left-tile.png",
    "part-br-tile": PART_DIR / "lantern-bottom-right-tile.png",
}

FRAME_PARTS = {
    "tl": PART_DIR / "lantern-top-left.png",
    "tr": PART_DIR / "lantern-top-right.png",
    "bl": PART_DIR / "lantern-bottom-left.png",
    "br": PART_DIR / "lantern-bottom-right.png",
}

IMAGE_CACHE: dict[Path, ImageReader] = {}


def image(path: Path) -> ImageReader:
    if path not in IMAGE_CACHE:
        IMAGE_CACHE[path] = ImageReader(str(path))
    return IMAGE_CACHE[path]


def register_fonts() -> tuple[str, str]:
    regular = ROOT / "edu/games/companion-adventures/node_modules/@vercel/og/dist/noto-sans-v27-latin-regular.ttf"
    if regular.exists():
        pdfmetrics.registerFont(TTFont("SFTNoto", str(regular)))
        return "SFTNoto", "Helvetica-Bold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = register_fonts()


def load_book() -> dict:
    book = json.loads(SOURCE.read_text(encoding="utf-8"))
    pages = book["pages"]
    if len(pages) != 32 or [page["page"] for page in pages] != list(range(1, 33)):
        raise ValueError("E02 v2.0.0 must contain exactly 32 contiguous pages")
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
        c.circle(x, y, (0.4 + (index % 3) * 0.25) * mm, fill=1, stroke=0)
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


def draw_text(c: canvas.Canvas, text: str, *, x: float, top: float, width: float, size: float = 18,
              colour=WHITE, font: str = REGULAR, leading: float | None = None,
              max_lines: int | None = None, centred: bool = False) -> float:
    leading = leading or size * 1.23
    lines = wrap_lines(text, font, size, width)
    if max_lines and len(lines) > max_lines:
        raise ValueError(f"Text does not fit allotted lines: {text}")
    c.setFillColor(colour)
    c.setFont(font, size)
    y = top
    for line in lines:
        if line:
            if centred:
                c.drawCentredString(x + width / 2, y, line)
            else:
                c.drawString(x, y, line)
        y -= leading
    return y


def draw_story_text(c: canvas.Canvas, page: dict) -> None:
    heading = page.get("heading")
    top = PAGE - 14 * mm
    if heading:
        draw_text(c, heading, x=13 * mm, top=top, width=168 * mm, size=24, colour=GOLD, font=BOLD, max_lines=2)
        top -= 18 * mm if len(heading) < 27 else 26 * mm
    draw_text(c, page["text"], x=13.5 * mm, top=top - .5 * mm, width=168 * mm, size=18.2, colour=NAVY, leading=22.5, max_lines=8)
    draw_text(c, page["text"], x=13 * mm, top=top, width=168 * mm, size=18.2, colour=WHITE, leading=22.5, max_lines=8)


def draw_page_number(c: canvas.Canvas, number: int, dark: bool) -> None:
    c.setFillColor(WHITE if dark else INK)
    c.setFont(BOLD, 8)
    c.drawCentredString(PAGE / 2, 5.5 * mm, str(number))


def emoji_position(spec: dict) -> tuple[float, float, float]:
    size = spec["size"] * PAGE
    return spec["x"] * PAGE - size / 2, PAGE - spec["y"] * PAGE - size / 2, size


def draw_lantern_seams(c: canvas.Canvas, x: float, y: float, size: float) -> None:
    c.drawImage(image(EMOJI["lantern"]), x, y, width=size, height=size, mask="auto")
    c.saveState()
    c.setStrokeColor(GOLD)
    c.setLineWidth(3)
    c.setDash(5, 4)
    c.line(x + size / 2, y + size * .08, x + size / 2, y + size * .92)
    c.line(x + size * .12, y + size / 2, x + size * .88, y + size / 2)
    c.restoreState()


def draw_part_card(c: canvas.Canvas, asset: Path, x: float, y: float, size: float,
                   *, border=GOLD, fill=colors.HexColor("#FFF0C9")) -> None:
    """Show one stable emoji quarter as a separate, countable picture card."""
    c.setFillColor(fill)
    c.setStrokeColor(border)
    c.setLineWidth(1.8)
    c.roundRect(x, y, size, size, max(2 * mm, size * .10), fill=1, stroke=1)
    inset = size * .13
    c.drawImage(image(asset), x + inset, y + inset, width=size - 2 * inset,
                height=size - 2 * inset, mask="auto")


def draw_emoji(c: canvas.Canvas, spec: dict) -> None:
    x, y, size = emoji_position(spec)
    if spec["id"] == "lantern-seams":
        draw_lantern_seams(c, x, y, size)
    elif spec["id"].startswith("part-"):
        draw_part_card(c, EMOJI[spec["id"]], x, y, size)
    else:
        c.drawImage(image(EMOJI[spec["id"]]), x, y, width=size, height=size, mask="auto")
    if label := spec.get("label"):
        ly = y + size + 3 * mm
        c.setFont(BOLD, 9.5)
        c.setFillColor(NAVY)
        c.drawCentredString(x + size / 2 + .45 * mm, ly - .45 * mm, label)
        c.setFillColor(CREAM)
        c.drawCentredString(x + size / 2, ly, label)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.4)
        half = min(size * .34, pdfmetrics.stringWidth(label, BOLD, 9.5) * .6)
        c.line(x + size / 2 - half, ly - 2.2 * mm, x + size / 2 + half, ly - 2.2 * mm)


def draw_frame(c: canvas.Canvas, x: float, y: float, size: float, missing: str | None = None,
               highlight: bool = False) -> None:
    c.setFillColor(colors.HexColor("#21375D"))
    c.setStrokeColor(GOLD if highlight else colors.HexColor("#71809B"))
    c.setLineWidth(3 if highlight else 2)
    c.roundRect(x, y, size, size, 3 * mm, fill=1, stroke=1)
    for key, path in FRAME_PARTS.items():
        if key != missing:
            c.drawImage(image(path), x, y, width=size, height=size, mask="auto")
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.2)
    c.line(x + size / 2, y, x + size / 2, y + size)
    c.line(x, y + size / 2, x + size, y + size / 2)


def draw_title(c: canvas.Canvas, book: dict, page: dict) -> None:
    draw_paper(c, 2)
    c.setFillColor(NAVY)
    c.setFont(BOLD, 28)
    c.drawCentredString(PAGE / 2, PAGE - 41 * mm, book["title"])
    c.setFillColor(PURPLE)
    c.setFont(BOLD, 18)
    c.drawCentredString(PAGE / 2, PAGE - 56 * mm, book["subtitle"])
    for idx, emoji_id in enumerate(("lantern", "moon", "door")):
        size = 35 * mm
        c.drawImage(image(EMOJI[emoji_id]), (43 + idx * 47) * mm, PAGE - 111 * mm, width=size, height=size, mask="auto")
    draw_text(c, page["subtext"], x=28 * mm, top=PAGE - 133 * mm, width=154 * mm, size=13.5, colour=INK, leading=19, max_lines=7)
    c.setFillColor(colors.HexColor("#5A6473"))
    c.setFont(REGULAR, 8.5)
    c.drawCentredString(PAGE / 2, 16 * mm, "CC BY 4.0 text · OpenMoji items CC BY-SA 4.0 · review copy")


def draw_cover(c: canvas.Canvas, book: dict) -> None:
    draw_crop(c, SCENES["cover"])
    c.setFillColor(GOLD)
    c.setFont(BOLD, 10)
    c.drawCentredString(PAGE / 2, PAGE - 15 * mm, "A STAR ROOMS ADVENTURE · BOOK 2")
    c.setFillColor(WHITE)
    c.setFont(BOLD, 29)
    c.drawCentredString(PAGE / 2, PAGE - 36 * mm, book["title"])
    c.setFillColor(GOLD)
    c.setFont(BOLD, 18)
    c.drawCentredString(PAGE / 2, PAGE - 51 * mm, book["subtitle"])
    size = 42 * mm
    c.drawImage(image(EMOJI["lantern"]), PAGE / 2 - size / 2, 37 * mm, width=size, height=size, mask="auto")
    c.setFillColor(WHITE)
    c.setFont(BOLD, 12)
    c.drawCentredString(PAGE / 2, 10 * mm, "Maria Smith")


def paper_heading(c: canvas.Canvas, heading: str, instruction: str) -> None:
    draw_text(c, heading, x=16 * mm, top=PAGE - 20 * mm, width=178 * mm, size=25, colour=INK, font=BOLD)
    draw_text(c, instruction, x=16 * mm, top=PAGE - 37 * mm, width=178 * mm, size=17.5, colour=PURPLE, leading=22, max_lines=4)


def draw_detective(c: canvas.Canvas) -> None:
    draw_paper(c, 8)
    paper_heading(c, "Lantern Detective", "Which picture is the same lantern Mia took from the parcel?")
    centres = [47 * mm, 105 * mm, 163 * mm]
    for cx in centres:
        c.setFillColor(colors.HexColor("#F1E3BF")); c.circle(cx, 91 * mm, 25 * mm, fill=1, stroke=0)
    size = 38 * mm
    draw_frame(c, centres[0] - size / 2, 72 * mm, size, missing="br")
    c.drawImage(image(EMOJI["lantern"]), centres[1] - size / 2, 72 * mm, width=size, height=size, mask="auto")
    c.drawImage(image(EMOJI["lantern"]), centres[2] - size / 2, 72 * mm, width=size, height=size, mask="auto")
    c.drawImage(image(EMOJI["star"]), centres[2] + 9 * mm, 99 * mm, width=13 * mm, height=13 * mm, mask="auto")
    labels = ("MISSING PLACE", "SAME WHOLE", "EXTRA PIECE")
    c.setFillColor(INK); c.setFont(BOLD, 10)
    for cx, label in zip(centres, labels): c.drawCentredString(cx, 123 * mm, label)
    c.setFillColor(PURPLE); c.setFont(BOLD, 12); c.drawCentredString(PAGE / 2, 25 * mm, "Point first. Then turn the page to check.")


def draw_seam_hunt(c: canvas.Canvas) -> None:
    draw_paper(c, 11)
    paper_heading(c, "Seam Hunt", "Trace down the lantern. Then trace across it. How many parts might open?")
    size = 90 * mm; x = PAGE / 2 - size / 2; y = 52 * mm
    draw_lantern_seams(c, x, y, size)
    c.setFillColor(INK); c.setFont(BOLD, 13); c.drawCentredString(PAGE / 2, 39 * mm, "Make your guess before the page turns.")


def draw_count_keeper(c: canvas.Canvas) -> None:
    draw_paper(c, 14)
    paper_heading(c, "Count Keeper", "Follow the gold trail. Touch each lantern part once. Say one, two, three, four.")
    points = [(44, 104), (86, 82), (128, 108), (166, 74)]
    c.setStrokeColor(GOLD); c.setLineWidth(4); c.setLineCap(1)
    path = c.beginPath(); path.moveTo(points[0][0] * mm, points[0][1] * mm)
    for x, y in points[1:]: path.lineTo(x * mm, y * mm)
    c.drawPath(path, fill=0, stroke=1)
    for (x, y), key in zip(points, ("part-tl", "part-tr", "part-bl", "part-br")):
        size = 27 * mm
        draw_part_card(c, EMOJI[key], x * mm - size / 2, y * mm - size / 2, size)
    c.setFillColor(PURPLE); c.setFont(BOLD, 13); c.drawCentredString(PAGE / 2, 38 * mm, "One number for each part.")


def draw_same_size(c: canvas.Canvas, answer: bool) -> None:
    draw_paper(c, 21 if answer else 20)
    paper_heading(c, "Pair A is the same size" if answer else "Same-Size Pairs",
                  "Both pieces in Pair A match." if answer else "Which pair has two pieces the same size? Point to Pair A or Pair B.")
    for idx, (label, x) in enumerate((("PAIR A", 27), ("PAIR B", 112))):
        c.setFillColor(colors.HexColor("#F1E3BF")); c.setStrokeColor(GOLD if answer and idx == 0 else colors.HexColor("#8290A7")); c.setLineWidth(4 if answer and idx == 0 else 2)
        c.roundRect(x * mm, 54 * mm, 72 * mm, 82 * mm, 5 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont(BOLD, 14); c.drawCentredString((x + 36) * mm, 125 * mm, label)
    for x, size, key in ((38, 25, "part-tl"), (66, 25, "part-tr"), (120, 31, "part-bl"), (158, 18, "part-br")):
        draw_part_card(c, EMOJI[key], x * mm, 76 * mm, size * mm)
    if answer:
        c.setFillColor(PURPLE); c.setFont(BOLD, 13); c.drawCentredString(PAGE / 2, 40 * mm, "Same-size parts can return to same-size places.")


def draw_missing_place(c: canvas.Canvas, answer: bool) -> None:
    draw_paper(c, 23 if answer else 22)
    paper_heading(c, "The last part fits" if answer else "The Missing Place",
                  "All four places are full. No gap. No part covers another." if answer else "Three parts are in the frame. Which part fits the empty place?")
    size = 76 * mm; x = 25 * mm; y = 53 * mm
    draw_frame(c, x, y, size, missing=None if answer else "br", highlight=answer)
    if not answer:
        c.setFillColor(INK); c.setFont(BOLD, 13); c.drawCentredString(152 * mm, 126 * mm, "CHOOSE")
        for py, key in zip((103, 78, 53), ("part-br", "part-tl", "star")):
            c.setFillColor(colors.HexColor("#F1E3BF")); c.roundRect(128 * mm, (py - 10) * mm, 48 * mm, 21 * mm, 4 * mm, fill=1, stroke=0)
            asset = EMOJI[key]
            if key.startswith("part-"):
                draw_part_card(c, asset, 142 * mm, (py - 8) * mm, 17 * mm)
            else:
                c.drawImage(image(asset), 142 * mm, (py - 8) * mm, width=17 * mm, height=17 * mm, mask="auto")
    else:
        c.setFillColor(PURPLE); c.setFont(BOLD, 13); c.drawString(117 * mm, 91 * mm, "The bottom-right")
        c.drawString(117 * mm, 83 * mm, "part completed")
        c.drawString(117 * mm, 75 * mm, "the same lantern.")


def draw_lantern_builder(c: canvas.Canvas) -> None:
    draw_paper(c, 28)
    paper_heading(c, "Lantern Builder", "Trace each lantern part to its matching place. Use every part once.")
    frame_size = 68 * mm; fx = PAGE / 2 - frame_size / 2; fy = 62 * mm
    c.setFillColor(colors.HexColor("#21375D")); c.setStrokeColor(WHITE); c.setLineWidth(2)
    c.roundRect(fx, fy, frame_size, frame_size, 4 * mm, fill=1, stroke=1)
    c.line(fx + frame_size / 2, fy, fx + frame_size / 2, fy + frame_size)
    c.line(fx, fy + frame_size / 2, fx + frame_size, fy + frame_size / 2)
    sources = [(29, 137, "part-tl"), (158, 137, "part-tr"), (29, 48, "part-bl"), (158, 48, "part-br")]
    targets = [(fx + frame_size * .25, fy + frame_size * .75), (fx + frame_size * .75, fy + frame_size * .75), (fx + frame_size * .25, fy + frame_size * .25), (fx + frame_size * .75, fy + frame_size * .25)]
    for (sx, sy, key), (tx, ty) in zip(sources, targets):
        c.setStrokeColor(GOLD); c.setLineWidth(3); c.line(sx * mm, sy * mm, tx, ty)
        c.setFillColor(CREAM); c.circle((sx * mm + tx) / 2, (sy * mm + ty) / 2, 3 * mm, fill=1, stroke=0)
        size = 25 * mm
        draw_part_card(c, EMOJI[key], sx * mm - size / 2, sy * mm - size / 2, size)


def draw_paper_activity(c: canvas.Canvas, page: dict) -> bool:
    activity = page.get("activity")
    layout = page.get("layout")
    if activity == "lantern-detective": draw_detective(c); return True
    if activity == "seam-hunt": draw_seam_hunt(c); return True
    if activity == "count-keeper": draw_count_keeper(c); return True
    if activity == "same-size-pairs": draw_same_size(c, False); return True
    if layout == "same-size-answer": draw_same_size(c, True); return True
    if activity == "missing-place": draw_missing_place(c, False); return True
    if layout == "missing-place-answer": draw_missing_place(c, True); return True
    if activity == "lantern-builder": draw_lantern_builder(c); return True
    return False


def draw_doorway_overlay(c: canvas.Canvas) -> None:
    starts = [(42, 87), (53, 74), (35, 62), (49, 49)]
    ends = [(152, 76), (161, 76), (152, 67), (161, 67)]
    colours = (GOLD, TEAL, CORAL, PURPLE)
    keys = ("part-tl", "part-tr", "part-bl", "part-br")
    for (sx, sy), (ex, ey), colour, key in zip(starts, ends, colours, keys):
        c.setStrokeColor(colour); c.setLineWidth(3); c.setLineCap(1)
        path = c.beginPath(); path.moveTo(sx * mm, sy * mm); path.curveTo(80 * mm, sy * mm, 92 * mm, ey * mm, ex * mm, ey * mm); c.drawPath(path, fill=0, stroke=1)
        size = 18 * mm
        draw_part_card(c, EMOJI[key], sx * mm - size / 2, sy * mm - size / 2, size,
                       border=colour)


def draw_add_choices(c: canvas.Canvas) -> None:
    for value, x in zip((3, 4, 5), (79, 105, 131)):
        c.setFillColor(colors.HexColor("#F1E3BF")); c.setStrokeColor(GOLD); c.setLineWidth(2); c.circle(x * mm, 123 * mm, 10 * mm, fill=1, stroke=1)
        c.setFillColor(NAVY); c.setFont(BOLD, 20); c.drawCentredString(x * mm, 120 * mm, str(value))


def draw_builder_setup(c: canvas.Canvas) -> None:
    fx, fy, size = 82 * mm, 47 * mm, 48 * mm
    c.setFillColor(colors.HexColor("#21375D")); c.setStrokeColor(WHITE); c.setLineWidth(1.6); c.roundRect(fx, fy, size, size, 3 * mm, fill=1, stroke=1)
    c.line(fx + size / 2, fy, fx + size / 2, fy + size); c.line(fx, fy + size / 2, fx + size, fy + size / 2)
    for x, y, key in ((55, 87, "part-tl"), (151, 87, "part-tr"), (55, 51, "part-bl"), (151, 51, "part-br")):
        part_size = 24 * mm
        draw_part_card(c, EMOJI[key], x * mm - part_size / 2, y * mm - part_size / 2, part_size)


def render_page(c: canvas.Canvas, book: dict, page: dict) -> None:
    number = page["page"]
    if page["kind"] == "cover": draw_cover(c, book); return
    if page["kind"] == "title": draw_title(c, book, page); draw_page_number(c, number, False); return
    if draw_paper_activity(c, page): draw_page_number(c, number, False); return

    scene = page["scene"]
    if scene == "paper": draw_paper(c, number); dark = False
    else: draw_crop(c, SCENES[scene]); dark = True
    draw_story_text(c, page)
    for spec in page.get("emoji", []): draw_emoji(c, spec)
    if page.get("activity") == "doorway-parade": draw_doorway_overlay(c)
    if page.get("activity") == "add-together": draw_add_choices(c)
    if page.get("layout") == "builder-setup": draw_builder_setup(c)
    draw_page_number(c, number, dark)


def render_pdf(book: dict) -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(STUDENT_PDF), pagesize=(PAGE, PAGE), pageCompression=1)
    c.setTitle(f"{book['title']}: {book['subtitle']}")
    c.setAuthor(book["author"])
    c.setSubject("SFT Open Education Early Years picture book")
    for page in book["pages"]:
        render_page(c, book, page); c.showPage()
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
        sections.append(f'<section class="page{activity_class}" aria-labelledby="p{page["page"]}"><h2 id="p{page["page"]}">Page {page["page"]}: {heading}</h2><figure role="img" aria-label="{alt}"></figure>{activity_label}<p>{text}</p><p>{subtext}</p><p class="description"><strong>Picture description:</strong> {alt}</p></section>')
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(book['title'])} — accessible review edition {book['version']}</title>
<style>body{{font-family:Arial,sans-serif;line-height:1.6;max-width:48rem;margin:auto;padding:2rem;color:#1e2b42}}section{{border-bottom:1px solid #ddd;padding:1rem 0 2rem}}h1,h2{{line-height:1.2}}figure{{margin:0}}.activity{{background:#fff3c9;padding:1rem;border-left:6px solid #76519b}}.description{{color:#45566f}}</style></head>
<body><header><h1>{html.escape(book['title'])}</h1><p>{html.escape(book['subtitle'])}</p><p>By {html.escape(book['author'])} · Book 2 of 4 · Review edition {book['version']} · ages 3–5</p></header><main>{''.join(sections)}</main></body></html>"""
    ACCESSIBLE_HTML.parent.mkdir(parents=True, exist_ok=True)
    ACCESSIBLE_HTML.write_text(document, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--student-only", action="store_true"); parser.parse_args()
    book = load_book()
    missing = [path for path in list(SCENES.values()) + list(EMOJI.values()) + list(FRAME_PARTS.values()) if not path.exists()]
    if missing: raise FileNotFoundError("Missing art: " + ", ".join(map(str, missing)))
    render_pdf(book); render_html(book)
    print(STUDENT_PDF); print(ACCESSIBLE_HTML)


if __name__ == "__main__":
    main()
