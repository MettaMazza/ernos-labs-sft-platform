#!/usr/bin/env python3
"""Fail-closed mechanical audit of the 20 Lean-verified publication PDFs."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

import fitz


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RENDER_MANIFEST = (
    ROOT / "output/pdf/lean4_verified_2026-08-02/PDF_RENDER_MANIFEST.json"
)
DEFAULT_SUITE_MANIFEST = (
    ROOT
    / "publications/lean4_verification"
    / "LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"
)
DEFAULT_CENSUS = ROOT / "census/claims.json"
DEFAULT_JSON = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_PDF_AUDIT_2026-08-02.json"
DEFAULT_MD = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_PDF_AUDIT_2026-08-02.md"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
A4_WIDTH = 595.276
A4_HEIGHT = 841.890


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalise_text(value: str) -> str:
    translations = str.maketrans(
        {
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
            "\u00a0": " ",
        }
    )
    return re.sub(r"\s+", " ", value.translate(translations)).strip().lower()


def compact_text(value: str) -> str:
    return re.sub(r"\s+", "", value).lower()


def relevant_claims_for_paper(paper: dict, claims: list[dict]) -> list[dict]:
    if paper["paper_id"] == "theory_of_everything":
        return claims
    if paper["paper_id"] in ("methods", "lean4_whole_model_verification"):
        return [
            claim
            for claim in claims
            if claim["claim_id"] == "SFT-ROOT-THERE-IS-NO-NOTHING"
        ]
    branches = set(paper.get("branches", []))
    return [claim for claim in claims if claim["branch"] in branches]


def scan_pdf(record: dict, paper: dict, claims: list[dict]) -> dict:
    lean_report_sha256 = file_sha256(LEAN_REPORT)
    path = ROOT / record["pdf"]
    failures: list[str] = []
    blank_pages: list[int] = []
    non_a4_pages: list[int] = []
    clipped_blocks: list[dict] = []
    replacement_glyph_pages: list[int] = []
    very_short_pages: list[int] = []
    declared_fonts: set[str] = set()
    all_text_parts: list[str] = []

    if not path.is_file():
        return {"paper_id": paper["paper_id"], "status": "FAIL", "failures": ["missing PDF"]}
    actual_sha = f"sha256:{file_sha256(path)}"
    if actual_sha != record.get("pdf_sha256"):
        failures.append("PDF SHA-256 differs from render manifest")

    with fitz.open(path) as document:
        if document.needs_pass:
            failures.append("PDF is encrypted")
        if document.page_count != record.get("page_count"):
            failures.append("page count differs from render manifest")
        metadata = document.metadata or {}
        expected_metadata = {
            "title": paper["title"],
            "author": "Maria Smith",
            "subject": paper["subtitle"],
            "creator": "Ernos Labs Lean-verified publication-suite renderer",
        }
        metadata_mismatches = {
            key: {"expected": expected, "actual": metadata.get(key)}
            for key, expected in expected_metadata.items()
            if metadata.get(key) != expected
        }
        if metadata_mismatches:
            failures.append("PDF metadata mismatch")

        for page_index in range(document.page_count):
            page = document[page_index]
            page_number = page_index + 1
            rectangle = page.rect
            if (
                abs(rectangle.width - A4_WIDTH) > 0.75
                or abs(rectangle.height - A4_HEIGHT) > 0.75
            ):
                non_a4_pages.append(page_number)
            text = page.get_text("text", sort=True)
            all_text_parts.append(text)
            if "\ufffd" in text:
                replacement_glyph_pages.append(page_number)
            words = page.get_text("words")
            images = page.get_images(full=True)
            if not words and not images and not page.get_drawings():
                blank_pages.append(page_number)
            if len(text.strip()) < 20 and not images:
                very_short_pages.append(page_number)
            for block in page.get_text("blocks", sort=True):
                x0, y0, x1, y1 = block[:4]
                if x0 < -2 or y0 < -2 or x1 > rectangle.width + 2 or y1 > rectangle.height + 2:
                    if len(clipped_blocks) < 100:
                        clipped_blocks.append(
                            {
                                "page": page_number,
                                "bbox": [round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)],
                                "sample": str(block[4])[:160],
                            }
                        )
            for font in document.get_page_fonts(page_index, full=True):
                declared_fonts.add(font[3])

        all_text = "\n".join(all_text_parts)
        normalised = normalise_text(all_text)
        compact = compact_text(all_text)
        cover_text = normalise_text(all_text_parts[0] if all_text_parts else "")
        cover_requirements = {
            "title": normalise_text(paper["title"]),
            "author": "maria smith",
            "version": normalise_text(f"Version {paper['version']}"),
            "local DOI status": "doi: not assigned - local publication candidate",
            "publication status": "unpublished local publication candidate",
            "confirmation control": "maria smith's explicit confirmation is required before release",
            "Lean report SHA-256": lean_report_sha256,
        }
        missing_cover_requirements = [
            label for label, required in cover_requirements.items() if required not in cover_text
        ]
        if missing_cover_requirements:
            failures.append("cover is missing required publication-control text")
        if lean_report_sha256 not in compact:
            failures.append("Lean report SHA-256 is absent from extracted PDF text")

        relevant_claims = relevant_claims_for_paper(paper, claims)
        missing_claim_ids = [
            claim["claim_id"]
            for claim in relevant_claims
            if compact_text(claim["claim_id"]) not in compact
        ]
        missing_receipts = [
            claim["receipt_hash"]
            for claim in relevant_claims
            if compact_text(claim["receipt_hash"]) not in compact
        ]
        if missing_claim_ids:
            failures.append("one or more relevant claim IDs are absent from PDF text")
        if missing_receipts:
            failures.append("one or more relevant receipt hashes are absent from PDF text")
        if blank_pages:
            failures.append("blank page detected")
        if non_a4_pages:
            failures.append("non-A4 page detected")
        if clipped_blocks:
            failures.append("text or image block extends outside page bounds")
        if replacement_glyph_pages:
            failures.append("replacement glyph detected")

        return {
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "version": paper["version"],
            "pdf": record["pdf"],
            "pdf_sha256": actual_sha,
            "pdf_bytes": path.stat().st_size,
            "page_count": document.page_count,
            "a4_page_count": document.page_count - len(non_a4_pages),
            "relevant_claim_count": len(relevant_claims),
            "missing_claim_ids": missing_claim_ids,
            "missing_receipt_hashes": missing_receipts,
            "blank_pages": blank_pages,
            "non_a4_pages": non_a4_pages,
            "clipped_blocks": clipped_blocks,
            "replacement_glyph_pages": replacement_glyph_pages,
            "very_short_pages_for_review": very_short_pages,
            "declared_fonts": sorted(declared_fonts),
            "metadata": metadata,
            "metadata_mismatches": metadata_mismatches,
            "missing_cover_requirements": missing_cover_requirements,
            "extracted_characters": len(all_text),
            "failures": failures,
            "status": "PASS" if not failures else "FAIL",
        }


def write_markdown(payload: dict, path: Path) -> None:
    lines = [
        "# Lean 4 verified publication PDF audit — 2 August 2026",
        "",
        f"Status: **{payload['status']}**",
        "",
        "This local, fail-closed audit opens and scans every rendered page. It checks file",
        "identity, PDF metadata, A4 geometry, nonblank content, page-boundary clipping,",
        "replacement glyphs, mandatory cover controls, Lean-report identity and the",
        "presence of every branch-relevant claim ID and engine receipt hash. Exact claim",
        "statement preservation remains independently checked by the manuscript guidance",
        "audit. Visual contact-sheet review is recorded separately.",
        "",
        f"- PDFs: {payload['summary']['paper_count']}",
        f"- Pages scanned: {payload['summary']['page_count']:,}",
        f"- Bytes scanned: {payload['summary']['pdf_bytes']:,}",
        f"- Relevant claim identities checked: {payload['summary']['relevant_claim_identity_checks']:,}",
        f"- Relevant receipt identities checked: {payload['summary']['relevant_receipt_identity_checks']:,}",
        f"- Failures: {payload['summary']['failure_count']}",
        "",
        "| Paper | Version | Pages | Relevant claims | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for paper in payload["papers"]:
        lines.append(
            f"| {paper['paper_id']} | {paper['version']} | {paper['page_count']:,} | "
            f"{paper['relevant_claim_count']:,} | {paper['status']} |"
        )
    lines.extend(
        [
            "",
            "No publication, upload, DOI action, release or remote repository mutation was",
            "performed. Maria Smith remains the sole publication authority.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-manifest", type=Path, default=DEFAULT_RENDER_MANIFEST)
    parser.add_argument("--suite-manifest", type=Path, default=DEFAULT_SUITE_MANIFEST)
    parser.add_argument("--census", type=Path, default=DEFAULT_CENSUS)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD)
    arguments = parser.parse_args()

    render_manifest_path = arguments.render_manifest.resolve()
    suite_manifest_path = arguments.suite_manifest.resolve()
    render_manifest = json.loads(render_manifest_path.read_text(encoding="utf-8"))
    suite_manifest = json.loads(suite_manifest_path.read_text(encoding="utf-8"))
    claims = json.loads(arguments.census.resolve().read_text(encoding="utf-8"))["claims"]
    render_by_id = {item["paper_id"]: item for item in render_manifest["papers"]}
    papers = []
    for index, paper in enumerate(suite_manifest["papers"], start=1):
        print(f"[{index}/{len(suite_manifest['papers'])}] auditing {paper['paper_id']}", flush=True)
        record = render_by_id.get(paper["paper_id"])
        if record is None:
            papers.append(
                {"paper_id": paper["paper_id"], "status": "FAIL", "failures": ["missing render record"]}
            )
            continue
        papers.append(scan_pdf(record, paper, claims))

    complete_records = [paper for paper in papers if "page_count" in paper]
    failure_count = sum(len(paper.get("failures", [])) for paper in papers)
    payload = {
        "schema": "sft.lean4_verified_publication_pdf_audit.v1",
        "date": "2026-08-02",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "render_manifest": str(render_manifest_path.relative_to(ROOT)),
        "render_manifest_sha256": f"sha256:{file_sha256(render_manifest_path)}",
        "suite_manifest": str(suite_manifest_path.relative_to(ROOT)),
        "suite_manifest_sha256": f"sha256:{file_sha256(suite_manifest_path)}",
        "lean_report_sha256": f"sha256:{file_sha256(LEAN_REPORT)}",
        "papers": papers,
        "summary": {
            "paper_count": len(papers),
            "page_count": sum(paper["page_count"] for paper in complete_records),
            "pdf_bytes": sum(paper["pdf_bytes"] for paper in complete_records),
            "relevant_claim_identity_checks": sum(
                paper["relevant_claim_count"] for paper in complete_records
            ),
            "relevant_receipt_identity_checks": sum(
                paper["relevant_claim_count"] for paper in complete_records
            ),
            "failure_count": failure_count,
            "blank_page_count": sum(len(paper["blank_pages"]) for paper in complete_records),
            "non_a4_page_count": sum(len(paper["non_a4_pages"]) for paper in complete_records),
            "clipped_block_count": sum(len(paper["clipped_blocks"]) for paper in complete_records),
            "replacement_glyph_page_count": sum(
                len(paper["replacement_glyph_pages"]) for paper in complete_records
            ),
        },
        "publication_authorized": False,
        "remote_actions_performed": [],
        "status": "PASS" if not failure_count and len(papers) == 20 else "FAIL",
    }
    arguments.json_output.resolve().write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, arguments.markdown_output.resolve())
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
