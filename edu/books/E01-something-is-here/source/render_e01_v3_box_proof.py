#!/usr/bin/env python3
"""First four-page layout proof for the new book, not a complete release.

The open-box diagram has explicit inside/outside state. Stable OpenMoji items
are never replaced by generated copies. Historical renderers stay untouched.
"""
import argparse
import html
import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[4]
BOOK = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "edu/assets/openmoji/16.0.0/color/png-512"
SIZE = 210 * mm
INK = HexColor("#203448")
CREAM = HexColor("#FFF9EB")
TEAL = HexColor("#23796F")
GOLD = HexColor("#E4AD29")
FONT_PATH = ROOT / "edu/games/companion-adventures/node_modules/@vercel/og/dist/noto-sans-v27-latin-regular.ttf"
pdfmetrics.registerFont(TTFont("BookText", str(FONT_PATH)))


def polygon(c, points, fill, stroke="#35291F", width=1.7):
    p = c.beginPath()
    p.moveTo(*points[0])
    for point in points[1:]:
        p.lineTo(*point)
    p.close()
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke))
    c.setLineWidth(width)
    c.drawPath(p, fill=1, stroke=1)


def emoji(c, code, x, y, size):
    c.drawImage(str(ITEMS / f"{code}.png"), x, y, size, size, mask="auto")


def open_box(c, x, y, width, teddy_inside=False):
    """x/y is the diagram bottom left; bounds include all four flaps.

    Back walls, light interior floor, and front walls are separate layers. The
    teddy's feet are occluded by the near rim only when inside the box.
    """
    c.saveState()
    c.translate(x, y)
    c.scale(width / 108, width / 108)
    # Rear open flaps point away from the cavity; there is no lid across it.
    polygon(c, [(14, 48), (54, 69), (40, 82), (0, 61)], "#F4BD6D")
    polygon(c, [(54, 69), (94, 48), (108, 61), (68, 82)], "#FFD798")
    # Interior cavity: dark back walls and a distinct, fully visible base.
    polygon(c, [(14, 48), (54, 69), (94, 48), (54, 27)], "#9D602E")
    polygon(c, [(14, 48), (54, 69), (54, 49), (30, 36)], "#B97B3D")
    polygon(c, [(54, 69), (94, 48), (78, 36), (54, 49)], "#C58C4E")
    polygon(c, [(30, 36), (54, 49), (78, 36), (54, 23)], "#FFE0A7")
    if teddy_inside:
        emoji(c, "1F9F8", 27, 27, 54)
    # Solid front faces cover only the bottom of an inside teddy.
    polygon(c, [(14, 48), (54, 27), (54, 0), (14, 21)], "#E7A74B")
    polygon(c, [(54, 27), (94, 48), (94, 21), (54, 0)], "#C48637")
    # Front flaps fold outward and never cover the cavity.
    polygon(c, [(14, 48), (54, 27), (40, 14), (0, 35)], "#FFD798")
    polygon(c, [(54, 27), (94, 48), (108, 35), (68, 14)], "#F4BD6D")
    c.restoreState()


def wrapped(text, max_width, size=20):
    result = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if line and pdfmetrics.stringWidth(candidate, "BookText", size) > max_width:
                result.append(line)
                line = word
            else:
                line = candidate
        result.append(line)
    return result


def text_block(c, page):
    c.setFillColor(TEAL)
    c.setFont("BookText", 10)
    caption = "The first discovery"
    if page["page"] == 9:
        caption += " · Maria & Matthew Smith"
    c.drawString(16 * mm, 197 * mm, caption)
    lines = wrapped(page["text"], 178 * mm)
    if len(lines) > 5:
        raise ValueError(f"Page {page['page']}: header has {len(lines)} lines")
    c.setFillColor(INK)
    c.setFont("BookText", 20)
    y = 184 * mm
    for line in lines:
        c.drawString(16 * mm, y, line)
        y -= 25
    if y < 140 * mm:
        raise ValueError(f"Page {page['page']}: text enters picture area")


def scene(c, path):
    """Book vignette, not a fullscreen game screen; preserve whole width.

    Square source: discard only upper blank reserve, not bodies on the rug.
    Landscape source: fit the complete composition without stretching.
    """
    im = ImageReader(str(path))
    iw, ih = im.getSize()
    x, y, w, h = 12 * mm, 33 * mm, 186 * mm, 125 * mm
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(x, y, w, h, 5 * mm)
    c.clipPath(clip, stroke=0)
    scale = w / iw
    draw_h = ih * scale
    if iw / ih > 1.25:
        c.drawImage(im, x, y + (h - draw_h) / 2, w, draw_h, mask="auto")
    else:
        c.drawImage(im, x, y - 3 * mm, w, draw_h, mask="auto")
    c.restoreState()


def map_stars(c, count):
    c.setFillColor(HexColor("#F3E4BD"))
    c.roundRect(53 * mm, 8 * mm, 104 * mm, 20 * mm, 3 * mm, fill=1, stroke=0)
    c.setFont("BookText", 9)
    c.setFillColor(INK)
    c.drawCentredString(105 * mm, 23 * mm, "Our map")
    for i in range(5):
        x = (65 + i * 18) * mm
        if i < count:
            emoji(c, "2B50", x, 10 * mm, 8 * mm)
        else:
            import math
            pts = []
            for j in range(10):
                a = math.pi / 2 + j * math.pi / 5
                r = (3.6 if j % 2 == 0 else 1.6) * mm
                pts.append((x + 4 * mm + r * math.cos(a), 14 * mm + r * math.sin(a)))
            polygon(c, pts, "#FFF9EB", "#786851", 1)


def label(c, text, x, y):
    c.setFillColor(INK)
    c.setFont("BookText", 14)
    c.drawCentredString(x, y, text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reveal-art", type=Path, required=True)
    args = parser.parse_args()
    if not args.reveal_art.is_file():
        raise FileNotFoundError(args.reveal_art)
    book = json.loads((BOOK / "source/book-v3.0.0.json").read_text())
    pages = book["pages"][8:12]
    out = ROOT / "output/pdf/edu/SFT-EDU-E01-SOMETHING-IS-HERE/3.0.0-development"
    out.mkdir(parents=True, exist_ok=True)
    target = out / "SFT-E01-Box-Sequence-Layout-Proof-v3.0.0.pdf"
    c = canvas.Canvas(str(target), pagesize=(SIZE, SIZE))
    c.setTitle("Something Is Here - four-page layout proof, pages 9–12")
    c.setAuthor(book["author"])
    for page in pages:
        c.setFillColor(CREAM)
        c.rect(0, 0, SIZE, SIZE, fill=1, stroke=0)
        text_block(c, page)
        number = page["page"]
        if number in (9, 12):
            old = BOOK / "art/v2.0.0/story/e01-box-rug-v2.0.0.png"
            scene(c, old if number == 9 else args.reveal_art)
            open_box(c, 72 * mm, 39 * mm, 60 * mm, teddy_inside=number == 9)
            if number == 12:
                emoji(c, "1F9F8", 139 * mm, 40 * mm, 30 * mm)
        else:
            c.setFillColor(HexColor("#F4E7C7"))
            c.ellipse(17 * mm, 43 * mm, 193 * mm, 84 * mm, fill=1, stroke=0)
            if number == 10:
                open_box(c, 58 * mm, 58 * mm, 94 * mm, teddy_inside=True)
            else:
                label(c, "Box", 66 * mm, 130 * mm)
                label(c, "Teddy", 158 * mm, 130 * mm)
                open_box(c, 20 * mm, 56 * mm, 92 * mm)
                emoji(c, "1F9F8", 135 * mm, 57 * mm, 46 * mm)
        map_stars(c, page["stars"])
        c.setFillColor(INK)
        c.setFont("BookText", 9)
        c.drawRightString(197 * mm, 13 * mm, str(number))
        c.setFont("BookText", 7)
        c.drawString(16 * mm, 4 * mm, "Development layout proof · Not a complete edition")
        c.showPage()
    c.save()
    accessible = out / "box-sequence-accessible.html"
    items = []
    for page in pages:
        items.append(f'<section><h2>Page {page["page"]}</h2><p>{html.escape(page["text"]).replace(chr(10), "<br>")}</p><p><em>Picture description:</em> {html.escape(page["alt"])}</p></section>')
    accessible.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Book 1 box-sequence proof</title><style>body{font:1.25rem/1.65 sans-serif;max-width:42rem;margin:auto;padding:1.5rem;color:#203448;background:#fff9eb}section{border-top:1px solid #b5aa91;margin-top:2rem}</style><h1>Something Is Here</h1><p>Maria &amp; Matthew Smith · Development layout proof, not a complete edition.</p>' + ''.join(items) + '</html>', encoding="utf-8")
    print(target)
    print(accessible)


if __name__ == "__main__":
    main()
