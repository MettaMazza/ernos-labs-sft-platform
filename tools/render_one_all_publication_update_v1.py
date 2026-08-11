#!/usr/bin/env python3
"""Render the One/All standalone paper and four same-lineage successors."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re

import fitz
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Frame, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents

from render_full_preliminary_toe import (
    ACCENT,
    ACCENT_DARK,
    INK,
    MUTED,
    RULE,
    ToEDocTemplate,
    body_story,
    inline_markup,
    register_fonts,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output/pdf/one-all-publication-update-2026-08-11"
RENDER_MANIFEST = OUTPUT_DIR / "PDF_RENDER_MANIFEST.json"


PAPERS = (
    {
        "paper_id": "one_all_standalone",
        "title": "What the Universe Is Made Of",
        "subtitle": "The One, the All, and pure consciousness in Smithian Fold Theory",
        "version": "1.0.0",
        "source": "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0.md",
        "pdf": "what-the-universe-is-made-of-the-one-and-all-v1.0.0.pdf",
        "lineage": "Included in the existing Foundation Zenodo lineage - no new post",
    },
    {
        "paper_id": "methods",
        "title": "There Is No Nothing",
        "subtitle": "One/All ontological integration and methods boundary",
        "version": "0.5.0",
        "source": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_5.md",
        "pdf": "sft-methods-v0.5.0.pdf",
        "lineage": "Existing concept DOI 10.5281/zenodo.21514889",
    },
    {
        "paper_id": "foundation",
        "title": "From Nothing to Fold",
        "subtitle": "The One as pure consciousness and the One/All foundation",
        "version": "1.5.0",
        "source": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_5.md",
        "pdf": "sft-foundation-v1.5.0.pdf",
        "lineage": "Existing concept DOI 10.5281/zenodo.21515628",
    },
    {
        "paper_id": "consciousness_cognitive_science",
        "title": "From Fold to Consciousness",
        "subtitle": "Pure consciousness before differentiation and differentiated conscious systems",
        "version": "1.2.0",
        "source": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_2.md",
        "pdf": "sft-consciousness-cognitive-science-v1.2.0.pdf",
        "lineage": "Existing concept DOI 10.5281/zenodo.21636396",
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "subtitle": "One/All ontological integration across the complete 2,778-claim surface",
        "version": "0.3.0",
        "source": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3.md",
        "pdf": "sft-theory-of-everything-v0.3.0.pdf",
        "lineage": "Existing concept DOI 10.5281/zenodo.21717583",
    },
)


class PublicationDocTemplate(ToEDocTemplate):
    def beforeDocument(self):
        super().beforeDocument()
        self._last_outline_level = -1

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        requested = {"ToeH1": 0, "ToeH2": 1, "ToeH3": 2}.get(flowable.style.name)
        if requested is None:
            return
        level = max(0, min(requested, self._last_outline_level + 1))
        text = flowable.getPlainText()
        key = f"heading-{self._bookmark_count}"
        self._bookmark_count += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
        self.notify("TOCEntry", (level, text, self.page, key))
        self._last_outline_level = level


def digest(path: Path) -> str:
    h = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def cover_story(paper: dict[str, str]):
    title = ParagraphStyle(
        "OneAllCoverTitle",
        fontName="ToeSerifBold",
        fontSize=25,
        leading=30,
        textColor=ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle = ParagraphStyle(
        "OneAllCoverSubtitle",
        fontName="ToeSerif",
        fontSize=12.5,
        leading=17,
        textColor=INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "OneAllCoverKicker",
        fontName="ToeSerifBold",
        fontSize=9,
        leading=12,
        textColor=ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "OneAllCoverAuthor",
        fontName="ToeSerif",
        fontSize=11,
        leading=16,
        textColor=INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "OneAllCoverNote",
        fontName="ToeSerif",
        fontSize=8.4,
        leading=12,
        textColor=MUTED,
        alignment=TA_CENTER,
        leftIndent=16 * mm,
        rightIndent=16 * mm,
    )
    status = ParagraphStyle(
        "OneAllCoverStatus",
        fontName="ToeSerifBold",
        fontSize=9,
        leading=13,
        textColor=ACCENT_DARK,
        alignment=TA_CENTER,
        borderColor=ACCENT,
        borderWidth=0.8,
        borderPadding=6,
    )
    return [
        Spacer(1, 16 * mm),
        Paragraph("SMITHIAN FOLD THEORY V3", kicker),
        Spacer(1, 5 * mm),
        Paragraph(inline_markup(paper["title"]), title),
        Spacer(1, 6 * mm),
        Paragraph(inline_markup(paper["subtitle"]), subtitle),
        Spacer(1, 9 * mm),
        Table(
            [[""]],
            colWidths=[76 * mm],
            rowHeights=[1.5 * mm],
            style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), ACCENT)]),
        ),
        Spacer(1, 10 * mm),
        Paragraph("Maria Smith", author),
        Paragraph("Independent researcher and founder, Ernos Labs", author),
        Paragraph("Maria.Smith.Sftoe@gmail.com", author),
        Spacer(1, 10 * mm),
        Paragraph(
            f"Version {paper['version']}<br/>11 August 2026<br/>"
            f"{paper['lineage']}<br/>Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "2,778 model-admitted claims<br/>"
            "New claim: 192 candidates - one survivor - four controls<br/>"
            "No new Lean PASS claimed for the expanded census",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            paper.get(
                "publication_status",
                "PUBLICATION AUTHORIZED<br/>ZENODO NEW-VERSION ROUTE ONLY - NO NEW POST",
            ),
            status,
        ),
    ]


def render_one(paper: dict[str, str]) -> dict[str, object]:
    source_path = ROOT / paper["source"]
    output_path = OUTPUT_DIR / paper["pdf"]
    partial = output_path.with_suffix(".partial.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial.unlink(missing_ok=True)

    def draw_page(canvas, document):
        canvas.saveState()
        width, height = A4
        if document.page > 1:
            canvas.setStrokeColor(RULE)
            canvas.setLineWidth(0.4)
            canvas.line(17 * mm, height - 13 * mm, width - 17 * mm, height - 13 * mm)
            canvas.setFont("ToeSerif", 7.1)
            canvas.setFillColor(MUTED)
            header = paper["title"]
            if len(header) > 72:
                header = header[:69].rstrip() + "..."
            canvas.drawString(17 * mm, height - 10.2 * mm, header)
            canvas.drawRightString(width - 17 * mm, height - 10.2 * mm, f"v{paper['version']}")
            canvas.drawString(17 * mm, 9 * mm, "Maria Smith - Ernos Labs - 2026 - CC BY 4.0")
            canvas.drawRightString(width - 17 * mm, 9 * mm, str(document.page))
        canvas.restoreState()

    document = PublicationDocTemplate(
        str(partial),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title=paper["title"],
        author="Maria Smith",
        subject=paper["subtitle"],
        creator="Ernos Labs One/All publication renderer",
        keywords="Smithian Fold Theory, One, All, pure consciousness, observation, universe",
    )
    frame = Frame(document.leftMargin, document.bottomMargin, document.width, document.height, id="body")
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    source = source_path.read_text(encoding="utf-8")
    body, styles = body_story(source, audit=False, page_size=A4)
    toc = TableOfContents()
    toc.levelStyles = [styles["toc_h1"], styles["toc_h2"], styles["toc_h3"]]
    story = cover_story(paper) + [PageBreak(), Paragraph("Contents", styles["h1"]), Spacer(1, 4), toc, PageBreak()] + body
    document.multiBuild(story)
    os.replace(partial, output_path)
    with fitz.open(output_path) as pdf:
        pages = pdf.page_count
        metadata = pdf.metadata
    return {
        "paper_id": paper["paper_id"],
        "title": paper["title"],
        "version": paper["version"],
        "source": paper["source"],
        "source_sha256": digest(source_path),
        "pdf": output_path.relative_to(ROOT).as_posix(),
        "pdf_sha256": digest(output_path),
        "pdf_bytes": output_path.stat().st_size,
        "page_count": pages,
        "metadata": metadata,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-id", action="append", default=[])
    arguments = parser.parse_args()
    selected = set(arguments.paper_id)
    papers = [paper for paper in PAPERS if not selected or paper["paper_id"] in selected]
    missing = selected - {paper["paper_id"] for paper in papers}
    if missing:
        raise SystemExit("unknown paper IDs: " + ", ".join(sorted(missing)))
    register_fonts()
    prior = {}
    if RENDER_MANIFEST.is_file():
        prior = {row["paper_id"]: row for row in json.loads(RENDER_MANIFEST.read_text())["papers"]}
    for index, paper in enumerate(papers, 1):
        print(f"[{index}/{len(papers)}] rendering {paper['paper_id']}", flush=True)
        prior[paper["paper_id"]] = render_one(paper)
        RENDER_MANIFEST.write_text(
            json.dumps(
                {
                    "schema": "sft-v3-one-all-pdf-render-manifest/1",
                    "date": "2026-08-11",
                    "publication_authorized": True,
                    "new_zenodo_record_authorized": False,
                    "paper_count": len(prior),
                    "papers": sorted(prior.values(), key=lambda row: row["paper_id"]),
                    "status": "PASS" if len(prior) == len(PAPERS) else "IN_PROGRESS",
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"render manifest: {RENDER_MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
