#!/usr/bin/env python3
"""Render the two computation branch manuscripts to archival PDFs."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]


def cover(kicker_text: str, title_text: str, subtitle_text: str, statistics: str):
    title = ParagraphStyle("ComputationCoverTitle", fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("ComputationCoverSubtitle", fontName="Helvetica", fontSize=13, leading=18, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("ComputationCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("ComputationCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("ComputationCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("ComputationCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    return [
        Spacer(1, 20 * mm),
        Paragraph(kicker_text, kicker),
        Paragraph(title_text, title),
        Spacer(1, 7 * mm),
        Paragraph(subtitle_text, subtitle),
        Spacer(1, 10 * mm),
        Table([[""]], colWidths=[70 * mm], rowHeights=[1.5 * mm], style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)])),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 13 * mm),
        Paragraph("Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 13 * mm),
        Paragraph(statistics + "<br/>23 July 2026<br/>Paper: CC BY 4.0 - Code: Apache-2.0", note),
        Spacer(1, 8 * mm),
        Paragraph("LOCAL PREPUBLICATION MANUSCRIPT - PUBLICATION NOT YET AUTHORIZED", warning),
    ]


def render(source: Path, output: Path, title: str, subtitle: str, kicker: str, header: str, subject: str, statistics: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    def draw_page(canvas, doc):
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE)
            canvas.setLineWidth(0.4)
            canvas.line(20 * mm, height - 15 * mm, width - 20 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1)
            canvas.setFillColor(base.MUTED)
            canvas.drawString(20 * mm, height - 11.8 * mm, header)
            canvas.drawRightString(width - 20 * mm, 11 * mm, str(doc.page))
            canvas.drawString(20 * mm, 11 * mm, "Maria Smith - 2026 - CC BY 4.0 - LOCAL PREPUBLICATION")
        canvas.restoreState()

    document = BaseDocTemplate(
        str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm, title=title, author="Maria Smith",
        subject=subject, creator="Ernos Labs publication renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(cover(kicker, title, subtitle, statistics) + [PageBreak()] + base.body_story(source.read_text(encoding="utf-8")))
    print(f"rendered {output}")


def main() -> None:
    render(
        ROOT / "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md",
        ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001.pdf",
        "After Turing: The Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Classical Computational Science from Smithian Fold Theory",
        "SMITHIAN FOLD THEORY - CLASSICAL COMPUTATION BRANCH PAPER 001",
        "AFTER TURING: THE FOLD MACHINE - ERNOS LABS CLASSICAL COMPUTATION PAPER 001",
        "Completed Smithian Fold Theory Classical Computation branch",
        "Third clean-room reconstruction - Classical Computation inventory complete<br/>113 admitted derivations - 28,928 generated candidates",
    )
    render(
        ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md",
        ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001.pdf",
        "The Quantum Fold Machine",
        "An Exact, Parameter-Free and Machine-Closed Derivation of Reversible and Quantum Computation from Smithian Fold Theory",
        "SMITHIAN FOLD THEORY - REVERSIBLE AND QUANTUM COMPUTATION BRANCH PAPER 001",
        "THE QUANTUM FOLD MACHINE - ERNOS LABS QUANTUM COMPUTATION PAPER 001",
        "Completed Smithian Fold Theory Reversible and Quantum Computation branch",
        "Third clean-room reconstruction - Quantum Computation inventory complete<br/>21 admitted derivations - 5,376 generated candidates",
    )


if __name__ == "__main__":
    main()
