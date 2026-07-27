#!/usr/bin/env python3
"""Render the local branch-roadmap successor set as branded archival PDFs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

from pypdf import PdfReader
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

import render_platform_paper as base


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication/branch_roadmap_successor_versions.json"

OUTPUT_NAMES = {
    "methods": "there-is-no-nothing-methods-paper-00-v0.3.pdf",
    "foundation": "from-nothing-to-fold-foundation-paper-001-v1.3.pdf",
    "mathematics": "from-fold-to-mathematics-branch-paper-001-v1.4.pdf",
    "information_science": "from-distinction-to-information-branch-paper-001-v1.3.pdf",
    "computation": "after-turing-fold-machine-branch-paper-001-v1.3.pdf",
    "quantum_computation": "quantum-fold-machine-branch-paper-001-v1.3.pdf",
    "physics": "from-fold-to-physics-branch-paper-001-v1.2.pdf",
    "materials": "from-fold-to-materials-branch-paper-001-v1.2.pdf",
}

BRANCH_LABELS = {
    "methods": "METHODS PAPER 00",
    "foundation": "FOUNDATION BRANCH PAPER 001",
    "mathematics": "MATHEMATICS BRANCH PAPER 001",
    "information_science": "INFORMATION SCIENCE BRANCH PAPER 001",
    "computation": "CLASSICAL COMPUTATION BRANCH PAPER 001",
    "quantum_computation": "REVERSIBLE AND QUANTUM COMPUTATION PAPER 001",
    "physics": "PHYSICS BRANCH PAPER 001",
    "materials": "MATERIALS SCIENCE BRANCH PAPER 001",
}

SUBTITLE_OVERRIDES = {
    "physics": "An Exact, Parameter-Free and Machine-Closed Reconstruction of Physical Science from Smithian Fold Theory",
    "materials": "An Exact, Parameter-Free and Machine-Closed Reconstruction of Materials Science from Smithian Fold Theory",
}


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def paper_title(branch: str, source: Path) -> tuple[str, str]:
    lines = source.read_text(encoding="utf-8").splitlines()
    title = next(line[2:].strip() for line in lines if line.startswith("# "))
    subtitle = SUBTITLE_OVERRIDES.get(
        branch,
        next((line[3:].strip() for line in lines if line.startswith("## ")), "Smithian Fold Theory"),
    )
    return title, subtitle


def cover(branch: str, version: str, title_text: str, subtitle_text: str, authorized: bool, doi: str):
    title = ParagraphStyle("RoadmapCoverTitle", fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    subtitle = ParagraphStyle("RoadmapCoverSubtitle", fontName="Helvetica", fontSize=12, leading=17, textColor=base.INK, alignment=TA_CENTER)
    kicker = ParagraphStyle("RoadmapCoverKicker", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=base.ACCENT, alignment=TA_CENTER)
    author = ParagraphStyle("RoadmapCoverAuthor", fontName="Times-Roman", fontSize=12, leading=18, textColor=base.INK, alignment=TA_CENTER)
    note = ParagraphStyle("RoadmapCoverNote", fontName="Times-Roman", fontSize=9, leading=13, textColor=base.MUTED, alignment=TA_CENTER, leftIndent=18 * mm, rightIndent=18 * mm)
    warning = ParagraphStyle("RoadmapCoverWarning", fontName="Helvetica-Bold", fontSize=9, leading=13, textColor=base.ACCENT_DARK, alignment=TA_CENTER)
    return [
        Spacer(1, 18 * mm),
        Paragraph(f"SMITHIAN FOLD THEORY - {BRANCH_LABELS[branch]}", kicker),
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
        Paragraph(f"{'Published' if authorized else 'Local'} same-paper roadmap successor version {version}<br/>27 July 2026<br/>{'DOI: ' + doi + '<br/>' if doi else ''}Paper: CC BY 4.0 - Code: Apache-2.0", note),
        Spacer(1, 8 * mm),
        Paragraph("PUBLISHED OPEN-ACCESS VERSION" if authorized else "LOCAL SUCCESSOR - REMOTE PUBLICATION NOT AUTHORIZED", warning),
    ]


def render(record: dict[str, object]) -> dict[str, object]:
    branch = str(record["branch"])
    authorized = bool(record.get("publication_authorized", False))
    source = ROOT / str(record["successor"])
    output = ROOT / "output/pdf" / OUTPUT_NAMES[branch]
    title_text, subtitle_text = paper_title(branch, source)
    doi_match = re.search(r"10\.5281/zenodo\.\d+", source.read_text(encoding="utf-8")[:5000])
    doi = doi_match.group(0) if doi_match else ""
    output.parent.mkdir(parents=True, exist_ok=True)

    def draw_page(canvas, doc):
        canvas.saveState()
        width, height = A4
        if doc.page > 1:
            canvas.setStrokeColor(base.RULE)
            canvas.setLineWidth(0.4)
            canvas.line(18 * mm, height - 15 * mm, width - 18 * mm, height - 15 * mm)
            canvas.setFont("Helvetica", 7.1)
            canvas.setFillColor(base.MUTED)
            canvas.drawString(18 * mm, height - 11.8 * mm, f"{title_text.upper()} - ERNOS LABS")
            canvas.drawRightString(width - 18 * mm, 11 * mm, str(doc.page))
            status = "PUBLISHED VERSION" if authorized else "LOCAL SUCCESSOR"
            canvas.drawString(18 * mm, 11 * mm, f"Maria Smith - 2026 - CC BY 4.0 - {status}")
        canvas.restoreState()

    document = BaseDocTemplate(
        str(output), pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=21 * mm, bottomMargin=18 * mm, title=title_text,
        author="Maria Smith", subject=f"{BRANCH_LABELS[branch]} full-field roadmap successor",
        creator="Ernos Labs roadmap-successor renderer",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    document.build(
        cover(branch, str(record["successor_version"]), title_text, subtitle_text, authorized, doi)
        + [PageBreak()]
        + base.body_story(source.read_text(encoding="utf-8"))
    )
    result = dict(record)
    result["rendered_pdf"] = output.relative_to(ROOT).as_posix()
    result["rendered_pdf_sha256"] = sha(output)
    result["rendered_page_count"] = len(PdfReader(str(output)).pages)
    return result


def main() -> None:
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rendered = []
    for record in payload["papers"]:
        branch = str(record["branch"])
        if branch == "chemistry":
            item = dict(record)
            path = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.2.pdf"
            item["rendered_pdf"] = path.relative_to(ROOT).as_posix()
            item["rendered_pdf_sha256"] = sha(path)
            item["rendered_page_count"] = len(PdfReader(str(path)).pages)
            rendered.append(item)
        else:
            rendered.append(render(record))
    payload["papers"] = rendered
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"rendered {len(rendered)} local successor PDFs and updated {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
