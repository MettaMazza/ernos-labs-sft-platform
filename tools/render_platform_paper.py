#!/usr/bin/env python3
"""Render the canonical repository landing paper to an archival PDF.

This optional publication tool is not part of SFT derivational authority. It
uses ReportLab to typeset README.md and emits only a presentation artifact.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "README.md"
DEFAULT_OUTPUT = ROOT / "output" / "pdf" / "there-is-no-nothing-sft-open-science-platform.pdf"

INK = colors.HexColor("#17212B")
ACCENT = colors.HexColor("#0C6B58")
ACCENT_DARK = colors.HexColor("#074A3D")
PALE = colors.HexColor("#EAF5F1")
RULE = colors.HexColor("#A6B8B1")
MUTED = colors.HexColor("#55645F")


def inline_markup(text: str) -> str:
    """Escape text while retaining the small Markdown subset used by the paper."""

    tokens: list[str] = []

    def hold(value: str) -> str:
        tokens.append(value)
        return f"@@TOKEN{len(tokens) - 1}@@"

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+|[^)]+\.md(?:#[^)]*)?|[^)]+\.json|[^)]+\.pdf)\)",
        lambda match: hold(
            f'<link href="{html.escape(match.group(2), quote=True)}" color="#0C6B58">'
            f"{html.escape(match.group(1))}</link>"
        ),
        text,
    )
    text = re.sub(r"`([^`]+)`", lambda match: hold(f'<font name="Courier">{html.escape(match.group(1))}</font>'), text)
    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    text = text.replace("&lt;br&gt;", "<br/>")
    for index, token in enumerate(tokens):
        text = text.replace(f"@@TOKEN{index}@@", token)
    return text


def styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.4,
            leading=13.2, textColor=INK, spaceAfter=6, alignment=TA_LEFT,
        ),
        "abstract": ParagraphStyle(
            "Abstract", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.2,
            leading=13.2, textColor=INK, leftIndent=8 * mm, rightIndent=8 * mm,
            spaceAfter=7,
        ),
        "h1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=17,
            leading=20, textColor=ACCENT_DARK, spaceBefore=12, spaceAfter=7,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12,
            leading=15, textColor=ACCENT_DARK, spaceBefore=9, spaceAfter=5,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10,
            leading=13, textColor=ACCENT, spaceBefore=7, spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Times-Roman", fontSize=9.2,
            leading=12.8, leftIndent=6 * mm, firstLineIndent=-3.5 * mm, textColor=INK,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "Quote", parent=base["BodyText"], fontName="Times-Italic", fontSize=9.5,
            leading=13.2, leftIndent=7 * mm, rightIndent=5 * mm, borderColor=ACCENT,
            borderWidth=1.5, borderPadding=6, backColor=PALE, textColor=INK,
            spaceBefore=5, spaceAfter=7,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="Courier", fontSize=7.4,
            leading=10, leftIndent=4 * mm, rightIndent=4 * mm, borderColor=RULE,
            borderWidth=0.5, borderPadding=5, backColor=colors.HexColor("#F4F7F6"),
            spaceBefore=4, spaceAfter=7,
        ),
        "table": ParagraphStyle(
            "TableCell", parent=base["BodyText"], fontName="Helvetica", fontSize=7.1,
            leading=9.2, textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "TableHead", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=7.2,
            leading=9.2, textColor=colors.white,
        ),
    }


def draw_page(canvas, doc):
    canvas.saveState()
    width, height = A4
    if doc.page > 1:
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(20 * mm, height - 11.8 * mm, "THERE IS NO NOTHING · ERNOS LABS METHODS PAPER 001")
        canvas.drawRightString(width - 20 * mm, 11 * mm, f"{doc.page}")
        canvas.drawString(20 * mm, 11 * mm, "Maria Smith · 2026 · CC BY 4.0 · doi:10.5281/zenodo.21514890")
    canvas.restoreState()


def cover_story():
    width, height = A4
    story = [Spacer(1, 30 * mm)]
    title = ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=31, leading=35, textColor=ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("CoverSubtitle", fontName="Helvetica", fontSize=15, leading=20, textColor=INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("CoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=8)
    author = ParagraphStyle("CoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=INK, alignment=TA_CENTER)
    note = ParagraphStyle("CoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=MUTED, alignment=TA_CENTER, leftIndent=25 * mm, rightIndent=25 * mm)
    story.extend([
        Paragraph("METHODS AND FOUNDATION PAPER 001", kicker),
        Paragraph("There Is No Nothing", title),
        Spacer(1, 8 * mm),
        Paragraph("A Premise-Free Operational Foundation and an Open Verification Platform for Smithian Fold Theory", subtitle),
        Spacer(1, 12 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)])),
        Spacer(1, 12 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Smithian Fold Theory Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 18 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 22 * mm),
        Paragraph("Third clean-room reconstruction · Inaugural methods release<br/>doi:10.5281/zenodo.21514890 · Version 0.1.0 · 23 July 2026<br/>Canonical source: repository README · Code: Apache-2.0 · Paper: CC BY 4.0", note),
    ])
    return story


def parse_table(lines: list[str], style_map):
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(cells)
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
        rows.pop(1)
    count = max(len(row) for row in rows)
    normalized = [row + [""] * (count - len(row)) for row in rows]
    data = []
    for row_index, row in enumerate(normalized):
        cell_style = style_map["table_head"] if row_index == 0 else style_map["table"]
        data.append([Paragraph(inline_markup(cell), cell_style) for cell in row])
    usable = A4[0] - 40 * mm
    if count == 2:
        widths = [usable * 0.29, usable * 0.71]
    elif count == 3:
        widths = [usable * 0.22, usable * 0.43, usable * 0.35]
    elif count == 4:
        widths = [usable * 0.18, usable * 0.18, usable * 0.24, usable * 0.40]
    else:
        widths = [usable / count] * count
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_DARK),
        ("GRID", (0, 0), (-1, -1), 0.35, RULE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7F6")]),
    ]))
    return table


def body_story(source: str):
    style_map = styles()
    lines = source.splitlines()
    start = next(index for index, line in enumerate(lines) if line.strip() == "## Abstract")
    lines = lines[start:]
    story = []
    paragraph: list[str] = []
    code: list[str] = []
    in_code = False
    abstract_mode = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            chosen = style_map["abstract"] if abstract_mode else style_map["body"]
            story.append(Paragraph(inline_markup(" ".join(item.strip() for item in paragraph)), chosen))
            paragraph = []

    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                story.append(XPreformatted(html.escape("\n".join(code)), style_map["code"])); code = []
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code.append(line); index += 1; continue
        if stripped.startswith("|") and index + 1 < len(lines) and lines[index + 1].strip().startswith("|"):
            flush_paragraph()
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index]); index += 1
            story.extend([parse_table(table_lines, style_map), Spacer(1, 5)])
            continue
        if stripped.startswith("## "):
            flush_paragraph()
            abstract_mode = stripped == "## Abstract"
            story.append(Paragraph(inline_markup(stripped[3:]), style_map["h1"]))
        elif stripped.startswith("### "):
            flush_paragraph(); abstract_mode = False
            story.append(Paragraph(inline_markup(stripped[4:]), style_map["h2"]))
        elif stripped.startswith("#### "):
            flush_paragraph(); abstract_mode = False
            story.append(Paragraph(inline_markup(stripped[5:]), style_map["h3"]))
        elif stripped.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), style_map["quote"]))
        elif re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            flush_paragraph()
            match = re.match(r"^([-*]|\d+\.)\s+(.*)", stripped)
            marker = "•" if match.group(1) in ("-", "*") else match.group(1)
            story.append(Paragraph(f"{marker}&nbsp;&nbsp;{inline_markup(match.group(2))}", style_map["bullet"]))
        elif stripped in ("---", ""):
            flush_paragraph()
            if stripped == "---":
                story.append(Spacer(1, 4))
        elif stripped.startswith("# "):
            pass
        else:
            paragraph.append(stripped)
        index += 1
    flush_paragraph()
    return story


def render(source_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = source_path.read_text(encoding="utf-8")
    doc = BaseDocTemplate(
        str(output_path), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm, title="There Is No Nothing",
        author="Maria Smith", subject="Smithian Fold Theory Open Source Science Platform",
        creator="Ernos Labs publication renderer",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="body")
    doc.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    doc.build(cover_story() + [PageBreak()] + body_story(source))
    print(f"rendered {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
