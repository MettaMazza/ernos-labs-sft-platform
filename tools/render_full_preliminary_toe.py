#!/usr/bin/env python3
"""Render the full SFT V3 preliminary ToE and its audit companions.

This is a presentation-only tool. It does not admit claims or publish files.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import html
from pathlib import Path
import re

from matplotlib.mathtext import math_to_image
from PIL import Image as PillowImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    LongTable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    XPreformatted,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = (
    ROOT
    / "publications/preliminary_toe"
    / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
)
DEFAULT_OUTPUT = (
    ROOT
    / "output/pdf"
    / "smithian-fold-theory-v3-preliminary-theory-of-everything-v0.1.0.pdf"
)

INK = colors.HexColor("#18232C")
ACCENT = colors.HexColor("#8A3C20")
ACCENT_DARK = colors.HexColor("#512415")
PALE = colors.HexColor("#F7EEE9")
RULE = colors.HexColor("#B9A69D")
MUTED = colors.HexColor("#5F625F")

FONT_DIR = Path("/System/Library/Fonts/Supplemental")
EQUATION_CACHE = ROOT / "tmp/pdfs/preliminary-toe-full/equations"


def register_fonts() -> None:
    fonts = {
        "ToeSerif": FONT_DIR / "Times New Roman.ttf",
        "ToeSerifBold": FONT_DIR / "Times New Roman Bold.ttf",
        "ToeSerifItalic": FONT_DIR / "Times New Roman Italic.ttf",
        "ToeSerifBoldItalic": FONT_DIR / "Times New Roman Bold Italic.ttf",
        "ToeMono": FONT_DIR / "Courier New.ttf",
        "ToeMonoBold": FONT_DIR / "Courier New Bold.ttf",
    }
    for name, source in fonts.items():
        if not source.is_file():
            raise RuntimeError(f"required publication font is missing: {source}")
        pdfmetrics.registerFont(TTFont(name, str(source)))
    pdfmetrics.registerFontFamily(
        "ToeSerif",
        normal="ToeSerif",
        bold="ToeSerifBold",
        italic="ToeSerifItalic",
        boldItalic="ToeSerifBoldItalic",
    )
    pdfmetrics.registerFontFamily(
        "ToeMono", normal="ToeMono", bold="ToeMonoBold"
    )


def ascii_publication_punctuation(text: str) -> str:
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def inline_markup(text: str) -> str:
    text = ascii_publication_punctuation(text)
    tokens: list[str] = []

    def hold(value: str) -> str:
        tokens.append(value)
        return f"@@TOE{len(tokens) - 1}@@"

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda match: hold(
            f'<link href="{html.escape(match.group(2), quote=True)}" '
            f'color="#8A3C20">{html.escape(match.group(1))}</link>'
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda match: hold(
            f'<font name="ToeMono">{html.escape(match.group(1))}</font>'
        ),
        text,
    )
    text = re.sub(
        r"\\\((.*?)\\\)",
        lambda match: hold(inline_math_markup(match.group(1))),
        text,
        flags=re.DOTALL,
    )
    text = html.escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<i>\1</i>", text)
    text = text.replace("&lt;br&gt;", "<br/>")
    for index, token in enumerate(tokens):
        text = text.replace(f"@@TOE{index}@@", token)
    return text


def inline_math_markup(expression: str) -> str:
    """Render the manuscript's small inline-TeX subset as readable markup."""
    def unwrap(value: str, command: str) -> str:
        marker = f"\\{command}{{"
        while marker in value:
            start = value.index(marker)
            cursor = start + len(marker)
            depth = 1
            while cursor < len(value) and depth:
                if value[cursor] == "{":
                    depth += 1
                elif value[cursor] == "}":
                    depth -= 1
                cursor += 1
            if depth:
                break
            inside = value[start + len(marker) : cursor - 1]
            value = value[:start] + inside + value[cursor:]
        return value

    raw = ascii_publication_punctuation(expression.strip())
    raw = unwrap(unwrap(raw, "mathrm"), "text")
    value = html.escape(raw)
    replacements = {
        r"\alpha": "&#945;",
        r"\beta": "&#946;",
        r"\gamma": "&#947;",
        r"\delta": "&#948;",
        r"\lambda": "&#955;",
        r"\Lambda": "&#923;",
        r"\pi": "&#960;",
        r"\pm": "&#177;",
        r"\times": " &#215; ",
        r"\cdot": " &#183; ",
        r"\leq": " &#8804; ",
        r"\geq": " &#8805; ",
        r"\rightarrow": " &#8594; ",
        r"\longrightarrow": " &#8594; ",
        r"\longmapsto": " &#8614; ",
        r"\leftrightarrow": " &#8596; ",
        r"\longleftrightarrow": " &#8596; ",
        r"\ldots": "...",
        r"\,": " ",
        r"\;": " ",
        r"\quad": "  ",
        r"\qquad": "   ",
    }
    for source, replacement in replacements.items():
        value = value.replace(source, replacement)
    value = re.sub(r"\^\{([^{}]+)\}", r"<super>\1</super>", value)
    value = re.sub(r"_\{([^{}]+)\}", r"<sub>\1</sub>", value)
    value = re.sub(r"\^([A-Za-z0-9+-]+)", r"<super>\1</super>", value)
    value = re.sub(r"_([A-Za-z0-9]+)", r"<sub>\1</sub>", value)
    return f'<font name="ToeSerifItalic">{value}</font>'


def normalise_display_math(expression: str) -> str:
    value = ascii_publication_punctuation(expression).strip()
    value = value.replace(r"\cfrac", r"\frac")
    value = re.sub(r"\\frac([A-Za-z0-9])([A-Za-z0-9])", r"\\frac{\1}{\2}", value)
    value = value.replace(r"\mathbin", "")
    value = re.sub(r"\\ge(?!q)", r"\\geq", value)
    value = value.replace(r"\longmapsto", r"\mapsto")
    value = value.replace(r"\longrightarrow", r"\rightarrow")
    value = value.replace(r"\longleftrightarrow", r"\leftrightarrow")
    value = re.sub(r"\\text\{([^{}]*)\}", r"\\mathrm{\1}", value)
    value = re.sub(r"\s+", " ", value)
    return value


def display_equation_flowable(expression: str, usable_width: float):
    """Typeset a display equation with Matplotlib's mathtext engine."""
    normalised = normalise_display_math(expression)
    identity = sha256(normalised.encode("utf-8")).hexdigest()
    EQUATION_CACHE.mkdir(parents=True, exist_ok=True)
    output = EQUATION_CACHE / f"{identity}.png"
    if not output.is_file():
        math_to_image(
            f"${normalised}$",
            str(output),
            dpi=240,
            format="png",
            color="#18232C",
        )
    with PillowImage.open(output) as raster:
        pixel_width, pixel_height = raster.size
    width = min(usable_width * 0.92, pixel_width * 72 / 240)
    height = width * pixel_height / pixel_width
    if height > 34 * mm:
        height = 34 * mm
        width = height * pixel_width / pixel_height
    rendered = Image(str(output), width=width, height=height)
    rendered.hAlign = "CENTER"
    return rendered


def style_map(audit: bool = False) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    body_size = 8.5 if audit else 9.5
    leading = 11.4 if audit else 13.2
    return {
        "body": ParagraphStyle(
            "ToeBody",
            parent=sample["BodyText"],
            fontName="ToeSerif",
            fontSize=body_size,
            leading=leading,
            textColor=INK,
            spaceAfter=5.5,
            alignment=TA_LEFT,
            allowWidows=0,
            allowOrphans=0,
        ),
        "abstract": ParagraphStyle(
            "ToeAbstract",
            parent=sample["BodyText"],
            fontName="ToeSerif",
            fontSize=9.2,
            leading=13.0,
            textColor=INK,
            leftIndent=8 * mm,
            rightIndent=8 * mm,
            spaceAfter=6,
        ),
        "h1": ParagraphStyle(
            "ToeH1",
            parent=sample["Heading1"],
            fontName="ToeSerifBold",
            fontSize=17,
            leading=20,
            textColor=ACCENT_DARK,
            spaceBefore=11,
            spaceAfter=7,
            # Keeping a branch heading with an entire following LongTable can
            # make ReportLab advance twice when the preceding table ends at a
            # page boundary, leaving an otherwise empty page.  Audit volumes
            # therefore let the splittable table control pagination; the
            # conceptual monograph retains ordinary heading custody.
            keepWithNext=not audit,
        ),
        "h2": ParagraphStyle(
            "ToeH2",
            parent=sample["Heading2"],
            fontName="ToeSerifBold",
            fontSize=12.3,
            leading=15,
            textColor=ACCENT_DARK,
            spaceBefore=8,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "ToeH3",
            parent=sample["Heading3"],
            fontName="ToeSerifBold",
            fontSize=10.2,
            leading=12.6,
            textColor=ACCENT,
            spaceBefore=6.5,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "ToeBullet",
            parent=sample["BodyText"],
            fontName="ToeSerif",
            fontSize=body_size,
            leading=leading,
            leftIndent=6 * mm,
            firstLineIndent=-3.5 * mm,
            textColor=INK,
            spaceAfter=3,
        ),
        "quote": ParagraphStyle(
            "ToeQuote",
            parent=sample["BodyText"],
            fontName="ToeSerifItalic",
            fontSize=9.2,
            leading=13,
            leftIndent=7 * mm,
            rightIndent=5 * mm,
            borderColor=ACCENT,
            borderWidth=1.3,
            borderPadding=6,
            backColor=PALE,
            textColor=INK,
            spaceBefore=4,
            spaceAfter=7,
        ),
        "code": ParagraphStyle(
            "ToeCode",
            parent=sample["Code"],
            fontName="ToeMono",
            fontSize=6.9 if audit else 7.4,
            leading=9.2 if audit else 10,
            leftIndent=3 * mm,
            rightIndent=3 * mm,
            borderColor=RULE,
            borderWidth=0.4,
            borderPadding=4,
            backColor=colors.HexColor("#F7F5F3"),
            spaceBefore=4,
            spaceAfter=6,
        ),
        "table": ParagraphStyle(
            "ToeTable",
            parent=sample["BodyText"],
            fontName="ToeSerif",
            fontSize=6.5 if audit else 7.0,
            leading=8.2 if audit else 9.0,
            textColor=INK,
        ),
        "table_head": ParagraphStyle(
            "ToeTableHead",
            parent=sample["BodyText"],
            fontName="ToeSerifBold",
            fontSize=6.5 if audit else 7.0,
            leading=8.2 if audit else 9.0,
            textColor=colors.white,
        ),
        "toc_h1": ParagraphStyle(
            "ToeTocH1",
            fontName="ToeSerif",
            fontSize=9.2,
            leading=12,
            leftIndent=0,
            firstLineIndent=0,
            textColor=INK,
        ),
        "toc_h2": ParagraphStyle(
            "ToeTocH2",
            fontName="ToeSerif",
            fontSize=8.5,
            leading=11,
            leftIndent=7 * mm,
            firstLineIndent=0,
            textColor=MUTED,
        ),
        "toc_h3": ParagraphStyle(
            "ToeTocH3",
            fontName="ToeSerif",
            fontSize=8.0,
            leading=10,
            leftIndent=14 * mm,
            firstLineIndent=0,
            textColor=MUTED,
        ),
    }


class ToEDocTemplate(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bookmark_count = 0

    def beforeDocument(self):
        # ``multiBuild`` repeats the document until the contents table settles.
        # Stable bookmark keys are therefore required on every pass.
        self._bookmark_count = 0

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        levels = {"ToeH1": 0, "ToeH2": 1, "ToeH3": 2}
        level = levels.get(flowable.style.name)
        if level is None:
            return
        text = flowable.getPlainText()
        key = f"heading-{self._bookmark_count}"
        self._bookmark_count += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
        self.notify("TOCEntry", (level, text, self.page, key))


def split_markdown_row(line: str) -> list[str]:
    payload = line.strip().strip("|")
    cells = re.split(r"(?<!\\)\|", payload)
    return [cell.replace("\\|", "|").strip() for cell in cells]


def table_widths(
    count: int, usable: float, audit: bool, headers: list[str] | None = None
) -> list[float]:
    if count == 2:
        return [usable * 0.30, usable * 0.70]
    if count == 3:
        return [usable * 0.22, usable * 0.40, usable * 0.38]
    if count == 4:
        return [usable * 0.18, usable * 0.19, usable * 0.25, usable * 0.38]
    if count == 5:
        return [usable * 0.16, usable * 0.14, usable * 0.20, usable * 0.22, usable * 0.28]
    if count == 7:
        weights = [0.13, 0.08, 0.22, 0.07, 0.09, 0.07, 0.34]
        return [usable * value for value in weights]
    if count == 8:
        weights = [0.18, 0.08, 0.08, 0.07, 0.09, 0.07, 0.07, 0.36]
        return [usable * value for value in weights]
    if audit and count == 9:
        if headers and len(headers) > 2 and headers[1].strip().lower() == "branch":
            weights = [0.03, 0.10, 0.19, 0.20, 0.08, 0.11, 0.06, 0.05, 0.18]
        else:
            weights = [0.04, 0.19, 0.08, 0.11, 0.08, 0.06, 0.05, 0.05, 0.34]
        return [usable * value for value in weights]
    return [usable / count] * count


def parse_table(
    lines: list[str], styles: dict[str, ParagraphStyle], page_size, audit: bool
):
    rows = [split_markdown_row(line) for line in lines]
    if len(rows) > 1 and all(
        re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]
    ):
        rows.pop(1)
    count = max(len(row) for row in rows)
    normalized = [row + [""] * (count - len(row)) for row in rows]
    data = []
    for row_index, row in enumerate(normalized):
        style = styles["table_head"] if row_index == 0 else styles["table"]
        data.append([Paragraph(inline_markup(cell), style) for cell in row])
    usable = page_size[0] - 30 * mm
    table = LongTable(
        data,
        colWidths=table_widths(count, usable, audit, normalized[0]),
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=True,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), ACCENT_DARK),
                ("GRID", (0, 0), (-1, -1), 0.3, RULE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#F8F5F3")],
                ),
            ]
        )
    )
    return table


def body_story(source: str, audit: bool, page_size):
    styles = style_map(audit=audit)
    lines = ascii_publication_punctuation(source).splitlines()
    story = []
    paragraph: list[str] = []
    code: list[str] = []
    math: list[str] = []
    in_code = False
    in_math = False
    abstract_mode = False
    title_seen = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            chosen = styles["abstract"] if abstract_mode else styles["body"]
            if any(item.endswith("  ") for item in paragraph):
                # ReportLab's Paragraph normaliser can collapse HTML break
                # elements while rebuilding a multi-pass document.  Separate
                # flowables preserve Markdown hard breaks deterministically.
                compact = ParagraphStyle(
                    f"{chosen.name}HardBreak",
                    parent=chosen,
                    spaceAfter=0,
                )
                for item_index, item in enumerate(paragraph):
                    line_style = chosen if item_index == len(paragraph) - 1 else compact
                    story.append(Paragraph(inline_markup(item.strip()), line_style))
            else:
                story.append(
                    Paragraph(
                        inline_markup(" ".join(item.strip() for item in paragraph)),
                        chosen,
                    )
                )
            paragraph = []

    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            if in_code:
                story.append(
                    XPreformatted(
                        html.escape("\n".join(code)), styles["code"]
                    )
                )
                code = []
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code.append(line)
            index += 1
            continue
        if stripped == "\\[":
            flush_paragraph()
            in_math = True
            math = []
            index += 1
            continue
        if in_math:
            if stripped == "\\]":
                expression = " ".join(item.strip() for item in math)
                try:
                    story.append(
                        display_equation_flowable(
                            expression,
                            page_size[0] - (34 * mm if not audit else 28 * mm),
                        )
                    )
                    story.append(Spacer(1, 5))
                except Exception:
                    # Preserve the exact expression if an uncommon TeX command
                    # lies outside mathtext's supported grammar.  The release
                    # visual gate will expose any fallback for editorial review.
                    story.append(
                        XPreformatted(html.escape(expression), styles["code"])
                    )
                in_math = False
                math = []
            else:
                math.append(line)
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines):
            next_row = lines[index + 1].strip()
            if next_row.startswith("|"):
                flush_paragraph()
                table_lines = []
                while index < len(lines) and lines[index].strip().startswith("|"):
                    table_lines.append(lines[index])
                    index += 1
                story.extend(
                    [
                        parse_table(table_lines, styles, page_size, audit),
                        Spacer(1, 4),
                    ]
                )
                continue
        if stripped.startswith("# "):
            flush_paragraph()
            if not title_seen:
                title_seen = True
            else:
                story.extend(
                    [PageBreak(), Paragraph(inline_markup(stripped[2:]), styles["h1"])]
                )
            abstract_mode = False
        elif stripped.startswith("## "):
            flush_paragraph()
            heading = stripped[3:]
            abstract_mode = heading == "Abstract"
            if heading.startswith("Part ") and story:
                story.append(PageBreak())
            story.append(Paragraph(inline_markup(heading), styles["h1"]))
        elif stripped.startswith("### "):
            flush_paragraph()
            abstract_mode = False
            story.append(Paragraph(inline_markup(stripped[4:]), styles["h2"]))
        elif stripped.startswith("#### "):
            flush_paragraph()
            abstract_mode = False
            story.append(Paragraph(inline_markup(stripped[5:]), styles["h3"]))
        elif stripped.startswith("> "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(stripped[2:]), styles["quote"]))
        elif re.match(r"^(?:[-*]|\d+\.)\s+", stripped):
            flush_paragraph()
            match = re.match(r"^([-*]|\d+\.)\s+(.*)", stripped)
            if match is None:
                raise RuntimeError("unreachable list parse")
            marker = "-" if match.group(1) in ("-", "*") else match.group(1)
            item_parts = [match.group(2).strip()]
            # Retain wrapped Markdown-list lines inside the same visual item.
            # Without this, a continuation can appear as a detached paragraph
            # and alter the apparent scope of a scientific qualification.
            while index + 1 < len(lines):
                continuation = lines[index + 1]
                continuation_stripped = continuation.strip()
                if not continuation_stripped:
                    break
                if not continuation[:1].isspace():
                    break
                if continuation_stripped.startswith(("#", "|", "```", "\\[")):
                    break
                item_parts.append(continuation_stripped)
                index += 1
            story.append(
                Paragraph(
                    f"{marker}&nbsp;&nbsp;{inline_markup(' '.join(item_parts))}",
                    styles["bullet"],
                )
            )
        elif stripped in ("---", ""):
            flush_paragraph()
            if stripped == "---":
                story.append(Spacer(1, 4))
        else:
            # Retain trailing spaces until ``flush_paragraph`` so Markdown
            # hard-line breaks in metadata are not silently collapsed.
            paragraph.append(line)
        index += 1
    flush_paragraph()
    return story, styles


def cover_story(title: str, subtitle: str, version: str, doi: str, audit: bool):
    title_style = ParagraphStyle(
        "ToeCoverTitle",
        fontName="ToeSerifBold",
        fontSize=28 if not audit else 24,
        leading=33 if not audit else 29,
        textColor=ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "ToeCoverSubtitle",
        fontName="ToeSerif",
        fontSize=13,
        leading=18,
        textColor=INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "ToeCoverKicker",
        fontName="ToeSerifBold",
        fontSize=9,
        leading=12,
        textColor=ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "ToeCoverAuthor",
        fontName="ToeSerif",
        fontSize=11.5,
        leading=17,
        textColor=INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "ToeCoverNote",
        fontName="ToeSerif",
        fontSize=8.7,
        leading=12.5,
        textColor=MUTED,
        alignment=TA_CENTER,
        leftIndent=20 * mm,
        rightIndent=20 * mm,
    )
    status = ParagraphStyle(
        "ToeCoverStatus",
        fontName="ToeSerifBold",
        fontSize=9,
        leading=13,
        textColor=ACCENT_DARK,
        alignment=TA_CENTER,
    )
    return [
        Spacer(1, 19 * mm),
        Paragraph("SMITHIAN FOLD THEORY V3", kicker),
        Spacer(1, 5 * mm),
        Paragraph(inline_markup(title), title_style),
        Spacer(1, 7 * mm),
        Paragraph(inline_markup(subtitle), subtitle_style),
        Spacer(1, 10 * mm),
        Table(
            [[""]],
            colWidths=[76 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)]),
        ),
        Spacer(1, 11 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 13 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>"
            "Maria.Smith.Sftoe@gmail.com",
            author,
        ),
        Spacer(1, 13 * mm),
        Paragraph(
            f"Version {inline_markup(version)} - first standalone V3 preliminary publication<br/>"
            f"31 July 2026<br/>Version DOI: {inline_markup(doi)}<br/>"
            "New standalone V3 concept record 21717583 - Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 9 * mm),
        Paragraph(
            "FULL-SCALE PRELIMINARY VERSION - COMPUTATIONAL PROGRAMMES CONTINUE",
            status,
        ),
    ]


def render(
    source_path: Path,
    output_path: Path,
    title: str,
    subtitle: str,
    version: str,
    doi: str,
    audit: bool,
) -> None:
    register_fonts()
    page_size = landscape(A4) if audit else A4
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = source_path.read_text(encoding="utf-8")

    def draw_page(canvas, document):
        canvas.saveState()
        width, height = page_size
        if document.page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.4)
            canvas.line(15 * mm, height - 13 * mm, width - 15 * mm, height - 13 * mm)
            canvas.setFont("ToeSerif", 7.2)
            canvas.setFillColor(MUTED)
            canvas.drawString(
                15 * mm,
                height - 10.2 * mm,
                "SFT V3 THEORY OF EVERYTHING - FULL PRELIMINARY VERSION 0.1.0",
            )
            canvas.drawRightString(width - 15 * mm, 9 * mm, str(document.page))
            canvas.drawString(
                15 * mm,
                9 * mm,
                f"Maria Smith - Ernos Labs - 2026 - CC BY 4.0 - DOI {doi}",
            )
        canvas.restoreState()

    document = ToEDocTemplate(
        str(output_path),
        pagesize=page_size,
        rightMargin=14 * mm if audit else 17 * mm,
        leftMargin=14 * mm if audit else 17 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title=title,
        author="Maria Smith",
        subject=subtitle,
        creator="Ernos Labs full preliminary ToE renderer",
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates(
        [PageTemplate(id="paper", frames=[frame], onPage=draw_page)]
    )
    body, styles = body_story(source, audit=audit, page_size=page_size)
    toc = TableOfContents()
    toc.levelStyles = [styles["toc_h1"], styles["toc_h2"], styles["toc_h3"]]
    toc_heading = Paragraph("Contents", styles["h1"])
    story = (
        cover_story(title, subtitle, version, doi, audit)
        + [PageBreak(), toc_heading, Spacer(1, 4), toc, PageBreak()]
        + body
    )
    document.multiBuild(story)
    print(f"rendered {output_path.relative_to(ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--title", default="The Smithian Fold Theory of Everything"
    )
    parser.add_argument(
        "--subtitle",
        default=(
            "An exhaustive preliminary monograph from There Is No Nothing to "
            "the current computational-proof frontier"
        ),
    )
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--doi", default="10.5281/zenodo.21717584")
    parser.add_argument("--audit", action="store_true")
    arguments = parser.parse_args()
    render(
        arguments.source.resolve(),
        arguments.output.resolve(),
        arguments.title,
        arguments.subtitle,
        arguments.version,
        arguments.doi,
        arguments.audit,
    )


if __name__ == "__main__":
    main()
