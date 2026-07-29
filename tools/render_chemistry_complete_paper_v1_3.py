#!/usr/bin/env python3
"""Render the exhaustive Chemistry v1.3 successor manuscript."""
from pathlib import Path
import sys

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path: sys.path.insert(0, str(ROOT / "tools"))
import render_platform_paper as base  # noqa: E402

SOURCE = ROOT / "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md"
OUTPUT = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.3.pdf"


def cover():
    title = ParagraphStyle("ChemistryCoverTitle", fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("ChemistryCoverSubtitle", fontName="Helvetica", fontSize=13, leading=18, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("ChemistryCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("ChemistryCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("ChemistryCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("ChemistryCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    return [
        Spacer(1, 18 * mm), Paragraph("SMITHIAN FOLD THEORY - CHEMISTRY BRANCH PAPER 001", kicker),
        Paragraph("From Fold to Chemistry", title), Spacer(1, 7 * mm),
        Paragraph("An Exact, Parameter-Free and Machine-Closed Reconstruction of Chemical Science from Smithian Fold Theory", subtitle),
        Spacer(1, 10 * mm), Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm), Paragraph("Ernos Labs", kicker), Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 13 * mm), Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 13 * mm), Paragraph("Version 1.3 - complete to the registered current standard and open to lawful extension<br/>272/272 obligations - 281 claims - 71,936 candidates - 1,124 controls<br/>29 July 2026<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
        Spacer(1, 8 * mm), Paragraph("FINAL PUBLICATION CANDIDATE - RELEASE NOT YET AUTHORISED", warning),
    ]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    def draw_page(canvas, doc):
        canvas.saveState(); width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE); canvas.setLineWidth(0.4); canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1); canvas.setFillColor(base.MUTED)
            canvas.drawString(18 * mm, height - 11.8 * mm, "FROM FOLD TO CHEMISTRY - ERNOS LABS CHEMISTRY PAPER 001 V1.3")
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page)); canvas.drawString(18 * mm, 11 * mm, "Maria Smith - 2026 - CC BY 4.0 - FINAL CANDIDATE / UNRELEASED")
        canvas.restoreState()
    document = BaseDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm, topMargin=21 * mm, bottomMargin=18 * mm, title="From Fold to Chemistry", author="Maria Smith", subject="Complete-current-standard Chemistry reconstruction in Smithian Fold Theory", creator="Ernos Labs publication renderer")
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover() + [PageBreak()] + base.body_story(SOURCE.read_text()))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__": main()
