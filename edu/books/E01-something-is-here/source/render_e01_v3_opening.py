#!/usr/bin/env python3
"""Render the opening and append the already-reviewed box sequence.

This remains a twelve-page development excerpt, not the complete 32-page book.
"""
import html
import json
import math
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from render_e01_v3_box_proof import BOOK, ROOT, SIZE, INK, CREAM, TEAL, emoji, open_box, polygon, wrapped

ART = BOOK / "art/v3.0.0/story"
OLD = BOOK / "art/v2.0.0/story"
OUT = ROOT / "output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/3.0.0-development"
SCRATCH = ROOT / "tmp/pdfs/e01-v3-opening"


def words(c, text, x, y, width, size=20, leading=25, colour=INK):
    c.setFont("BookText", size)
    c.setFillColor(colour)
    for line in wrapped(text, width, size):
        c.drawString(x, y, line)
        y -= leading
    return y


def picture(c, path, x=12, y=18, width=186, height=136, square_bottom=True):
    im = ImageReader(str(path))
    iw, ih = im.getSize()
    x, y, w, h = [v * mm for v in (x, y, width, height)]
    c.saveState()
    p = c.beginPath()
    p.roundRect(x, y, w, h, 5 * mm)
    c.clipPath(p, stroke=0)
    scale = w / iw
    dh = ih * scale
    bottom = y if square_bottom and ih > iw * .8 else y + (h - dh) / 2
    c.drawImage(im, x, bottom, w, dh, mask="auto")
    c.restoreState()


def page_base(c, page):
    c.setFillColor(CREAM)
    c.rect(0, 0, SIZE, SIZE, fill=1, stroke=0)
    words(c, "A Star Rooms adventure", 16 * mm, 197 * mm, 180 * mm, 10, 13, TEAL)
    end = words(c, page["text"], 16 * mm, 184 * mm, 178 * mm)
    if end < 145 * mm:
        raise ValueError(f"Page {page['page']}: reading text reaches picture")


def footer(c, n):
    words(c, "Development excerpt · Not a complete edition", 16 * mm, 5 * mm, 170 * mm, 7, 9)
    c.setFont("BookText", 9)
    c.drawRightString(197 * mm, 8 * mm, str(n))


def hollow_star(c, x, y, radius=3):
    pts = []
    for j in range(10):
        angle = math.pi / 2 + j * math.pi / 5
        r = radius * mm * (1 if j % 2 == 0 else .45)
        pts.append((x + r * math.cos(angle), y + r * math.sin(angle)))
    polygon(c, pts, "#FFF9EB", "#7A654A", 1)


def curtain(c, x, y, size):
    c.setFillColor(HexColor("#77518E"))
    c.setStrokeColor(INK)
    c.setLineWidth(1.4)
    c.roundRect(x, y, size, size, size * .08, fill=1, stroke=1)
    for f in (.22, .42, .6, .81):
        c.line(x + size * f, y + size * .04, x + size * f, y + size * .94)
    c.setStrokeColor(HexColor("#C48B34"))
    c.setLineWidth(3)
    c.line(x - 2, y + size + 2, x + size + 2, y + size + 2)


def shelves(c, x, y, size):
    c.setFillColor(HexColor("#DFB875"))
    c.setStrokeColor(INK)
    c.setLineWidth(1)
    for dx in (0, size * .56):
        c.rect(x + dx, y, size * .44, size * .87, fill=1, stroke=1)
        c.setFillColor(CREAM)
        c.rect(x + dx + size * .055, y + size * .09, size * .33, size * .66, fill=1, stroke=1)
        c.setFillColor(HexColor("#DFB875"))
    emoji(c, "2B1C", x + size * .10, y + size * .22, size * .23)


def arrow(c, x1, y1, x2, y2):
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    c.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    a = math.atan2(y2 - y1, x2 - x1)
    points = [(x2 * mm, y2 * mm)]
    for sign in (-1, 1):
        points.append(((x2 - 2.5 * math.cos(a) + sign * 1.5 * math.sin(a)) * mm,
                       (y2 - 2.5 * math.sin(a) - sign * 1.5 * math.cos(a)) * mm))
    polygon(c, points, "#23796F", "#23796F", .5)


def route_map(c):
    c.setFillColor(HexColor("#F4E5BF"))
    c.setStrokeColor(HexColor("#D9BA75"))
    c.roundRect(16 * mm, 17 * mm, 178 * mm, 81 * mm, 4 * mm, fill=1, stroke=1)
    words(c, "Our map: start at the box", 24 * mm, 90 * mm, 150 * mm, 12, 16)
    # Route connectors live in the gaps between object drawings.
    arrow(c, 57, 70, 87, 70)
    arrow(c, 117, 70, 148, 70)
    arrow(c, 179, 66, 179, 49)
    arrow(c, 148, 33, 117, 33)
    arrow(c, 87, 33, 57, 33)
    names = [(42, 70, "Box"), (103, 70, "Bell"), (164, 70, "Card"),
             (164, 33, "Curtain"), (103, 33, "Shelves"), (42, 33, "Star Door")]
    for i, (x, y, name) in enumerate(names):
        c.setFont("BookText", 10)
        c.setFillColor(INK)
        c.drawCentredString(x * mm, (y + 12) * mm, name)
        if i < 5:
            hollow_star(c, (x - 13) * mm, y * mm, 2.7)
        if i == 0:
            open_box(c, (x - 10) * mm, (y - 8) * mm, 20 * mm)
        elif i == 1:
            emoji(c, "1F514", (x - 9) * mm, (y - 10) * mm, 18 * mm)
        elif i == 2:
            emoji(c, "2B1C", (x - 9) * mm, (y - 10) * mm, 18 * mm)
        elif i == 3:
            curtain(c, (x - 8) * mm, (y - 9) * mm, 16 * mm)
        elif i == 4:
            shelves(c, (x - 10) * mm, (y - 10) * mm, 20 * mm)
        else:
            emoji(c, "1F6AA", (x - 9) * mm, (y - 10) * mm, 18 * mm)
    words(c, "ROOMSTAR", 164 * mm, 20 * mm, 28 * mm, 5.5, 7, HexColor("#8A7046"))


def main():
    book = json.loads((BOOK / "source/book-v3.0.0.json").read_text())
    for asset in ("e01-enter-v3.0.0.png", "e01-note-held-v3.0.0.png"):
        if not (ART / asset).exists():
            raise FileNotFoundError(ART / asset)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    opening = SCRATCH / "opening-pages.pdf"
    c = canvas.Canvas(str(opening), pagesize=(SIZE, SIZE))
    c.setTitle("Something Is Here - opening development pages")
    c.setAuthor(book["author"])
    for page in book["pages"][:8]:
        n = page["page"]
        if n == 1:
            c.drawImage(str(OLD / "e01-cover-v2.0.0.png"), 0, 0, SIZE, SIZE)
            words(c, "A Star Rooms adventure · Book 1", 18 * mm, 196 * mm, 177 * mm, 12, 16, HexColor("#FFE098"))
            words(c, "Something is here", 18 * mm, 181 * mm, 177 * mm, 31, 36, white)
            words(c, page["subtext"], 18 * mm, 165 * mm, 177 * mm, 20, 26, HexColor("#FFE098"))
            words(c, book["author"], 18 * mm, 150 * mm, 177 * mm, 13, 17, white)
            words(c, "Development excerpt · Pages 1–12", 18 * mm, 7 * mm, 175 * mm, 9, 12, white)
        elif n == 2:
            page_base(c, page)
            words(c, page["subtext"], 16 * mm, 164 * mm, 178 * mm, 16, 23)
            for j, code in enumerate(("1F4DD", "1F9F8", "1F514")):
                emoji(c, code, (23 + j * 60) * mm, 85 * mm, 43 * mm)
            words(c, "Version 3.0.0 development · 12 September 2026\nThis excerpt contains pages 1–12 of a 32-page manuscript.\nText: Maria & Matthew Smith, CC BY 4.0.\nEmoji: OpenMoji project and contributors, CC BY-SA 4.0.\nCharacter illustrations made with AI image generation.\nOpen-box, curtain and shelf diagrams are drawn in code.", 16 * mm, 62 * mm, 178 * mm, 10, 16)
            footer(c, n)
        elif n == 3:
            page_base(c, page)
            picture(c, ART / "e01-enter-v3.0.0.png")
            footer(c, n)
        elif n == 4:
            page_base(c, page)
            picture(c, OLD / "e01-opening-meet-v2.0.0.png")
            # Labels occupy the calm area immediately above each head.
            for x, y, name in [(53, 126, "Mia"), (96, 104, "Tavi"), (150, 106, "Sol")]:
                c.setFillColor(CREAM)
                c.roundRect((x - 10) * mm, (y - 2) * mm, 20 * mm, 8 * mm, 3 * mm, fill=1, stroke=0)
                c.setFillColor(INK)
                c.setFont("BookText", 11)
                c.drawCentredString(x * mm, y * mm, name)
            footer(c, n)
        elif n == 5:
            page_base(c, page)
            picture(c, OLD / "e01-cover-v2.0.0.png")
            c.setFillColor(HexColor("#D3A24F"))
            c.setStrokeColor(HexColor("#754C1F"))
            c.roundRect(169 * mm, 64 * mm, 21 * mm, 7 * mm, 1 * mm, fill=1, stroke=1)
            c.setFillColor(HexColor("#403627"))
            c.rect(171 * mm, 66 * mm, 17 * mm, 3 * mm, fill=1, stroke=0)
            footer(c, n)
        elif n == 6:
            page_base(c, page)
            picture(c, OLD / "e01-note-arrives-v2.0.0.png")
            emoji(c, "1F4DD", 103 * mm, 24 * mm, 25 * mm)
            emoji(c, "1F4D5", 19 * mm, 26 * mm, 22 * mm)
            emoji(c, "1F5FA", 164 * mm, 27 * mm, 22 * mm)
            footer(c, n)
        elif n == 7:
            page_base(c, page)
            picture(c, ART / "e01-note-held-v3.0.0.png")
            emoji(c, "1F4DD", 88 * mm, 42 * mm, 35 * mm)
            c.setFillColor(CREAM)
            c.roundRect(93 * mm, 78 * mm, 22 * mm, 7 * mm, 2 * mm, fill=1, stroke=0)
            words(c, "Note", 99 * mm, 80 * mm, 40 * mm, 10, 13)
            footer(c, n)
        else:
            page_base(c, page)
            c.setFillColor(white)
            c.setStrokeColor(HexColor("#DBC59A"))
            c.roundRect(16 * mm, 107 * mm, 178 * mm, 65 * mm, 4 * mm, fill=1, stroke=1)
            note = "\n".join(page["read_aloud_note"])
            words(c, note, 25 * mm, 160 * mm, 160 * mm, 18, 25)
            route_map(c)
            footer(c, n)
        c.showPage()
    c.save()
    # Preserve the completed four-page proof rather than rebuilding old work.
    box = OUT / "SFT-E01-Box-Sequence-Layout-Proof-v3.0.0.pdf"
    if len(PdfReader(box).pages) != 4:
        raise ValueError("Expected the reviewed four-page box proof")
    writer = PdfWriter()
    writer.append(opening)
    writer.append(box)
    writer.page_layout = "/SinglePage"
    writer.add_metadata({"/Title": "Something Is Here - development excerpt, pages 1–12", "/Author": book["author"]})
    target = OUT / "SFT-E01-Opening-and-Box-Development-v3.0.0.pdf"
    writer.write(target)
    sections = []
    for page in book["pages"][:12]:
        lines = [page["text"]]
        if page.get("subtext"):
            lines.append(page["subtext"])
        lines.extend(page.get("read_aloud_note", []))
        content = html.escape("\n".join(lines)).replace("\n", "<br>")
        sections.append(f'<section><h2>Page {page["page"]}</h2><p>{content}</p><p><strong>Picture description:</strong> {html.escape(page["alt"])}</p></section>')
    accessible = OUT / "opening-and-box-accessible.html"
    accessible.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Something Is Here - development excerpt</title><style>body{font:1.25rem/1.6 sans-serif;max-width:44rem;margin:auto;padding:1.5rem;background:#fff9eb;color:#203448}section{margin:3rem 0;border-top:1px solid #c9b77b}</style></head><body><h1>Something Is Here</h1><p>Maria &amp; Matthew Smith · Development excerpt, pages 1–12. Not a complete edition.</p>' + ''.join(sections) + '</body></html>', encoding="utf-8")
    print(target)
    print(accessible)


if __name__ == "__main__":
    main()
