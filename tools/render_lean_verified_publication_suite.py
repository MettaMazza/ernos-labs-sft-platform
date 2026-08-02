#!/usr/bin/env python3
"""Render the complete local Lean-verified SFT publication suite.

This is a presentation-only operation.  It neither admits scientific claims
nor performs any remote publication action.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

import fitz
from reportlab.lib import colors
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
DEFAULT_MANIFEST = (
    ROOT
    / "publications/lean4_verification"
    / "LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"
)
DEFAULT_OUTPUT = ROOT / "output/pdf/lean4_verified_2026-08-02"
RENDER_MANIFEST = DEFAULT_OUTPUT / "PDF_RENDER_MANIFEST.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"


class SuiteDocTemplate(ToEDocTemplate):
    """Keep source heading depth while preventing invalid PDF outline jumps."""

    def beforeDocument(self):
        super().beforeDocument()
        self._last_outline_level = -1

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph):
            return
        requested_levels = {"ToeH1": 0, "ToeH2": 1, "ToeH3": 2}
        requested = requested_levels.get(flowable.style.name)
        if requested is None:
            return
        level = min(requested, self._last_outline_level + 1)
        level = max(0, level)
        text = flowable.getPlainText()
        key = f"heading-{self._bookmark_count}"
        self._bookmark_count += 1
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(text, key, level=level, closed=level > 0)
        self.notify("TOCEntry", (level, text, self.page, key))
        self._last_outline_level = level


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pdf_name(paper: dict) -> str:
    paper_id = re.sub(r"[^a-z0-9]+", "-", paper["paper_id"].lower()).strip("-")
    return f"sft-{paper_id}-v{paper['version']}.pdf"


def cover_story(paper: dict):
    lean_report_sha256 = file_sha256(LEAN_REPORT)
    publication_status = paper.get("publication_status", "local_candidate")
    if publication_status == "published_open_access":
        doi = paper["doi"]
        doi_line = f'DOI: <link href="https://doi.org/{doi}">{doi}</link>'
        status_line = "PUBLISHED OPEN ACCESS<br/>ZENODO RECORD VERIFIED"
    else:
        doi_line = "DOI: not assigned - local publication candidate"
        status_line = (
            "UNPUBLISHED LOCAL PUBLICATION CANDIDATE<br/>"
            "MARIA SMITH'S EXPLICIT CONFIRMATION IS REQUIRED BEFORE RELEASE"
        )
    title_style = ParagraphStyle(
        "SuiteCoverTitle",
        fontName="ToeSerifBold",
        fontSize=25,
        leading=30,
        textColor=ACCENT_DARK,
        alignment=TA_CENTER,
    )
    subtitle_style = ParagraphStyle(
        "SuiteCoverSubtitle",
        fontName="ToeSerif",
        fontSize=12.5,
        leading=17,
        textColor=INK,
        alignment=TA_CENTER,
    )
    kicker = ParagraphStyle(
        "SuiteCoverKicker",
        fontName="ToeSerifBold",
        fontSize=9,
        leading=12,
        textColor=ACCENT,
        alignment=TA_CENTER,
    )
    author = ParagraphStyle(
        "SuiteCoverAuthor",
        fontName="ToeSerif",
        fontSize=11,
        leading=16,
        textColor=INK,
        alignment=TA_CENTER,
    )
    note = ParagraphStyle(
        "SuiteCoverNote",
        fontName="ToeSerif",
        fontSize=8.4,
        leading=12,
        textColor=MUTED,
        alignment=TA_CENTER,
        leftIndent=16 * mm,
        rightIndent=16 * mm,
    )
    status = ParagraphStyle(
        "SuiteCoverStatus",
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
        Paragraph(inline_markup(paper["title"]), title_style),
        Spacer(1, 6 * mm),
        Paragraph(inline_markup(paper["subtitle"]), subtitle_style),
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
            f"Version {inline_markup(paper['version'])}<br/>"
            "2 August 2026<br/>"
            f"{doi_line}<br/>"
            "Paper: CC BY 4.0 - Code: Apache-2.0",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(
            "Lean 4 whole-model report: PASS<br/>"
            f"SHA-256 {lean_report_sha256}",
            note,
        ),
        Spacer(1, 8 * mm),
        Paragraph(status_line, status),
    ]


def render_one(paper: dict, output_path: Path) -> dict:
    source_path = ROOT / paper["output"]
    if not source_path.is_file():
        raise FileNotFoundError(f"missing manuscript: {source_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    partial_path = output_path.with_suffix(".partial.pdf")
    partial_path.unlink(missing_ok=True)
    source = source_path.read_text(encoding="utf-8")

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
            footer_status = (
                "published open access"
                if paper.get("publication_status") == "published_open_access"
                else "local candidate"
            )
            canvas.drawString(
                17 * mm,
                9 * mm,
                f"Maria Smith - Ernos Labs - 2026 - CC BY 4.0 - {footer_status}",
            )
            canvas.drawRightString(width - 17 * mm, 9 * mm, str(document.page))
        canvas.restoreState()

    document = SuiteDocTemplate(
        str(partial_path),
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=18 * mm,
        bottomMargin=15 * mm,
        title=paper["title"],
        author="Maria Smith",
        subject=paper["subtitle"],
        creator="Ernos Labs Lean-verified publication-suite renderer",
        keywords=(
            "Smithian Fold Theory, Lean 4, formal verification, exact arithmetic, "
            "unique survivor, reproducible science"
        ),
    )
    frame = Frame(
        document.leftMargin,
        document.bottomMargin,
        document.width,
        document.height,
        id="body",
    )
    document.addPageTemplates([PageTemplate(id="paper", frames=[frame], onPage=draw_page)])
    body, styles = body_story(source, audit=False, page_size=A4)
    toc = TableOfContents()
    toc.levelStyles = [styles["toc_h1"], styles["toc_h2"], styles["toc_h3"]]
    story = (
        cover_story(paper)
        + [PageBreak(), Paragraph("Contents", styles["h1"]), Spacer(1, 4), toc, PageBreak()]
        + body
    )
    document.multiBuild(story)
    os.replace(partial_path, output_path)
    with fitz.open(output_path) as pdf:
        page_count = pdf.page_count
        metadata = pdf.metadata
    return {
        "paper_id": paper["paper_id"],
        "title": paper["title"],
        "version": paper["version"],
        "source": paper["output"],
        "source_sha256": f"sha256:{file_sha256(source_path)}",
        "pdf": str(output_path.relative_to(ROOT)),
        "pdf_sha256": f"sha256:{file_sha256(output_path)}",
        "pdf_bytes": output_path.stat().st_size,
        "page_count": page_count,
        "metadata": metadata,
        "status": (
            "RENDERED_PUBLISHED"
            if paper.get("publication_status") == "published_open_access"
            else "RENDERED_LOCAL_CANDIDATE"
        ),
    }


def write_manifest(
    records: list[dict],
    suite_manifest_path: Path,
    render_manifest_path: Path,
    expected_count: int,
    publication_authorized: bool,
) -> None:
    payload = {
        "schema": "sft.lean4_verified_pdf_render_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "suite_manifest": str(suite_manifest_path.relative_to(ROOT)),
        "suite_manifest_sha256": f"sha256:{file_sha256(suite_manifest_path)}",
        "lean_report_sha256": f"sha256:{file_sha256(LEAN_REPORT)}",
        "paper_count": len(records),
        "papers": sorted(records, key=lambda item: item["paper_id"]),
        "pdf_render_complete": len(records) == expected_count,
        "publication_authorized": publication_authorized,
        "remote_actions_performed": [],
        "status": "PASS" if len(records) == expected_count else "IN_PROGRESS",
    }
    render_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    render_manifest_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_existing_records(render_manifest_path: Path) -> dict[str, dict]:
    if not render_manifest_path.is_file():
        return {}
    payload = json.loads(render_manifest_path.read_text(encoding="utf-8"))
    return {record["paper_id"]: record for record in payload.get("papers", [])}


def existing_record_is_current(record: dict, paper: dict, output_path: Path) -> bool:
    if not output_path.is_file():
        return False
    source_path = ROOT / paper["output"]
    return (
        record.get("source_sha256") == f"sha256:{file_sha256(source_path)}"
        and record.get("pdf_sha256") == f"sha256:{file_sha256(output_path)}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--paper-id", action="append", default=[])
    parser.add_argument("--force", action="store_true")
    arguments = parser.parse_args()

    manifest_path = arguments.manifest.resolve()
    output_dir = arguments.output_dir.resolve()
    render_manifest_path = output_dir / "PDF_RENDER_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    selected = set(arguments.paper_id)
    papers = [
        paper for paper in manifest["papers"]
        if not selected or paper["paper_id"] in selected
    ]
    missing = selected - {paper["paper_id"] for paper in papers}
    if missing:
        raise SystemExit(f"unknown paper IDs: {', '.join(sorted(missing))}")

    register_fonts()
    records = load_existing_records(render_manifest_path)
    for index, paper in enumerate(papers, start=1):
        output_path = output_dir / pdf_name(paper)
        prior = records.get(paper["paper_id"], {})
        if not arguments.force and existing_record_is_current(prior, paper, output_path):
            print(f"[{index}/{len(papers)}] current: {paper['paper_id']}", flush=True)
            continue
        print(f"[{index}/{len(papers)}] rendering: {paper['paper_id']}", flush=True)
        record = render_one(paper, output_path)
        records[paper["paper_id"]] = record
        write_manifest(
            list(records.values()),
            manifest_path,
            render_manifest_path,
            len(papers),
            bool(manifest.get("publication_authorized")),
        )
        print(
            f"[{index}/{len(papers)}] rendered: {paper['paper_id']} "
            f"({record['page_count']} pages, {record['pdf_sha256']})",
            flush=True,
        )
    write_manifest(
        list(records.values()),
        manifest_path,
        render_manifest_path,
        len(papers),
        bool(manifest.get("publication_authorized")),
    )
    print(f"render manifest: {render_manifest_path.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
