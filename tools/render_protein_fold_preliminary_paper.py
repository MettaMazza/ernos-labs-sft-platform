#!/usr/bin/env python3
"""Render the SFT V3 Protein Fold preliminary-results paper to archival PDF."""

from pathlib import Path
import re
import sys

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import render_platform_paper as base  # noqa: E402


SOURCE = ROOT / "applications/frontier/v3_computational_proofs/protein_folding/paper/SMITHIAN_FOLD_THEORY_V3_PROTEIN_FOLD_COMPUTATIONAL_PROOF.md"
OUTPUT = ROOT / "output/pdf/sft-v3-protein-fold-computational-proof-preliminary-results-v0.9.4.pdf"
DOI = "10.5281/zenodo.21717581"


def publication_source(source: str) -> str:
    """Replace the six display-LaTeX blocks with renderer-safe display forms."""

    displays = {
        "\\[\nS=(a_1,a_2,\\ldots,a_n), \\qquad a_i\\in\\mathcal A,\n\\]":
            "> **Sequence carrier:** `S = (a_1, a_2, ..., a_n)`, with `a_i in A`.",
        "\\[\nk(S)=3(n-1)+r(S),\n\\]":
            "> **Word width:** `k(S) = 3(n - 1) + r(S)`.",
        "\\[\nN_{\\mathrm{word}}(S)=24^{k(S)}.\n\\]":
            "> **Raw word count:** `N_word(S) = 24^k(S)`.",
        "\\[\nN_{\\mathrm{pair}}=\\binom m2=\\frac{m(m-1)}2.\n\\]":
            "> **Unordered-pair count:** `N_pair = C(m, 2) = m(m - 1)/2`.",
        "\\[\nN_{\\mathrm{corr}}=m\\binom{m-1}{2}\n=\\frac{m(m-1)(m-2)}2.\n\\]":
            "> **Shared-atom correlation count:** `N_corr = m C(m - 1, 2) = m(m - 1)(m - 2)/2`.",
        "\\[\n\\sum_i (|L_i|-1)+(n-1)(|B|-1).\n\\]":
            "> **Successor count:** `sum_i(|L_i| - 1) + (n - 1)(|B| - 1)`.",
    }
    for source_form, display_form in displays.items():
        if source_form not in source:
            raise RuntimeError(f"missing registered display equation: {source_form}")
        source = source.replace(source_form, display_form)

    lines = source.splitlines()
    joined = []
    index = 0
    in_code = False
    while index < len(lines):
        line = lines[index]
        if line.strip().startswith("```"):
            in_code = not in_code
            joined.append(line)
            index += 1
            continue
        if not in_code and re.match(r"^(?:[-*]|\d+\.)\s+", line.strip()):
            item = line.strip()
            index += 1
            while index < len(lines):
                continuation = lines[index]
                stripped = continuation.strip()
                if (
                    not stripped
                    or stripped.startswith(("#", "|", ">", "```"))
                    or re.match(r"^(?:[-*]|\d+\.)\s+", stripped)
                ):
                    break
                item += " " + stripped
                index += 1
            joined.append(item)
            continue
        joined.append(line)
        index += 1
    return "\n".join(joined)


def cover():
    title = ParagraphStyle(
        "ProteinCoverTitle",
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=31,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "ProteinCoverSubtitle",
        fontName="Helvetica",
        fontSize=12.5,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "ProteinCoverKicker",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=base.ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "ProteinCoverAuthor",
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        textColor=base.INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "ProteinCoverNote",
        fontName="Times-Roman",
        fontSize=9,
        leading=13,
        textColor=base.MUTED,
        alignment=TA_CENTER,
        leftIndent=18 * mm,
        rightIndent=18 * mm,
    )
    status = ParagraphStyle(
        "ProteinCoverStatus",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=base.ACCENT_DARK,
        alignment=TA_CENTER,
    )
    return [
        Spacer(1, 14 * mm),
        Paragraph("SMITHIAN FOLD THEORY - COMPUTATIONAL PROOF PAPER 001", kicker),
        Paragraph("From Sequence to an Auditable Fold", title),
        Spacer(1, 7 * mm),
        Paragraph(
            "SFT V3 Protein Fold Computational Proof - Preliminary Results",
            subtitle,
        ),
        Spacer(1, 7 * mm),
        Paragraph(
            "Exact representation, certified frontier search and the restart of a generalised blind-parity programme",
            subtitle,
        ),
        Spacer(1, 9 * mm),
        Table(
            [[""]],
            colWidths=[70 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), base.ACCENT)]),
        ),
        Spacer(1, 10 * mm),
        Paragraph("Ernos Labs", kicker),
        Paragraph("Open Source Science Platform and Knowledge Tree", author),
        Spacer(1, 12 * mm),
        Paragraph(
            "Maria Smith<br/>Independent researcher and founder, Ernos Labs<br/>Maria.Smith.Sftoe@gmail.com",
            author,
        ),
        Spacer(1, 11 * mm),
        Paragraph(
            "Version 0.9.4 - updated preliminary results<br/>31 July 2026<br/>"
            f"DOI: {DOI}<br/>Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "UPDATED PRELIMINARY-RESULTS VERSION - INVESTIGATION CONTINUES",
            status,
        ),
    ]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    def draw_page(canvas, doc):
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE)
            canvas.setLineWidth(0.4)
            canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1)
            canvas.setFillColor(base.MUTED)
            canvas.drawString(
                18 * mm,
                height - 11.8 * mm,
                "SFT V3 PROTEIN FOLD - PRELIMINARY RESULTS V0.9.4",
            )
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            canvas.drawString(
                18 * mm,
                11 * mm,
                f"Maria Smith - 2026 - CC BY 4.0 - DOI {DOI}",
            )
        canvas.restoreState()

    document = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=21 * mm,
        bottomMargin=18 * mm,
        title="From Sequence to an Auditable Fold",
        author="Maria Smith",
        subject="Preliminary results from the SFT V3 Protein Fold computational proof programme",
        creator="Ernos Labs publication renderer",
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
    source = publication_source(SOURCE.read_text(encoding="utf-8"))
    document.build(cover() + [PageBreak()] + base.body_story(source))
    print(f"rendered {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
