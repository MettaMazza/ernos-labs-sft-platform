#!/usr/bin/env python3
"""Mechanical and text-surface QA for seven final-candidate PDFs.

The audit checks every rendered page, PDF metadata and A4 geometry, cover
status, blank/clipped/replacement-glyph conditions, live claim IDs, exact
current statements after whitespace normalisation and receipt identities.
Visual montage review remains a separate human/agent gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paper:
    branch: str
    label: str
    version: str
    claims: int
    candidates: int
    controls: int
    pdf: str
    title: str


PAPERS = (
    Paper("mathematics", "Mathematics", "1.5", 323, 97_280, 1_292, "output/pdf/from-fold-to-mathematics-branch-paper-001-v1.5.pdf", "From Fold to Mathematics"),
    Paper("information_science", "Information Science", "1.4", 262, 75_776, 1_048, "output/pdf/from-distinction-to-information-branch-paper-001-v1.4.pdf", "From Distinction to Information"),
    Paper("computation", "Classical Computation", "1.4", 369, 94_464, 1_476, "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf", "After Turing: The Fold Machine"),
    Paper("quantum_computation", "Reversible and Quantum Computation", "1.4", 288, 73_728, 1_152, "output/pdf/the-quantum-fold-machine-branch-paper-001-v1.4.pdf", "The Quantum Fold Machine"),
    Paper("physics", "Physics", "1.3", 368, 257_776, 1_472, "output/pdf/from-fold-to-physics-branch-paper-001-v1.3.pdf", "From Fold to Physics"),
    Paper("chemistry", "Chemistry", "1.3", 281, 71_936, 1_124, "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.3.pdf", "From Fold to Chemistry"),
    Paper("materials", "Materials Science", "1.3", 289, 73_984, 1_156, "output/pdf/from-fold-to-materials-branch-paper-001-v1.3.pdf", "From Fold to Materials"),
)


def normal(text: str) -> str:
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claims_document = json.loads((ROOT / "census/claims.json").read_text())
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in claims_document["claims"]:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    reports = []
    for paper in PAPERS:
        path = ROOT / paper.pdf
        raw = path.read_bytes()
        document = fitz.open(path)
        pages = []
        page_texts = []
        blank_pages = []
        clipped_blocks = []
        replacement_glyph_pages = []
        non_a4_pages = []

        for index, page in enumerate(document):
            text = page.get_text("text")
            page_texts.append(text)
            stripped = text.strip()
            if len(stripped) < 20:
                blank_pages.append(index + 1)
            if "�" in text or "\ufffd" in text:
                replacement_glyph_pages.append(index + 1)

            rect = page.rect
            if abs(rect.width - 595.276) > 0.2 or abs(rect.height - 841.89) > 0.2:
                non_a4_pages.append(index + 1)

            page_clipped = []
            for block in page.get_text("blocks"):
                x0, y0, x1, y1 = block[:4]
                if x0 < -0.5 or y0 < -0.5 or x1 > rect.width + 0.5 or y1 > rect.height + 0.5:
                    page_clipped.append([round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)])
            if page_clipped:
                clipped_blocks.append({"page": index + 1, "blocks": page_clipped})
            pages.append(
                {
                    "page": index + 1,
                    "characters": len(stripped),
                    "words": len(re.findall(r"\S+", stripped)),
                    "blocks": len(page.get_text("blocks")),
                }
            )

        complete_text = "\n".join(page_texts)
        normal_pdf = normal(complete_text)
        branch_claims = by_branch[paper.branch]
        missing_ids = sorted(
            claim["claim_id"] for claim in branch_claims if claim["claim_id"] not in complete_text
        )
        missing_statements = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if normal(claim["statement"]) not in normal_pdf
        )
        missing_receipts = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if claim["receipt_hash"] not in complete_text
        )

        first = normal(page_texts[0]) if page_texts else ""
        last = normal(page_texts[-1]) if page_texts else ""
        cover_checks = {
            "title": paper.title in first,
            "author": "Maria Smith" in first,
            "version": f"Version {paper.version}" in first,
            "claims": f"{paper.claims:,}" in first,
            "candidates": f"{paper.candidates:,}" in first,
            "controls": f"{paper.controls:,}" in first,
            "candidate_status": (
                "FINAL PUBLICATION CANDIDATE" in first
                and "NOT YET AUTHORISED" in first
            ),
        }
        metadata = document.metadata
        metadata_checks = {
            "title": metadata.get("title") == paper.title,
            "author": metadata.get("author") == "Maria Smith",
            "creator": metadata.get("creator") == "Ernos Labs publication renderer",
        }
        failures = []
        if len(branch_claims) != paper.claims:
            failures.append("live claim count mismatch")
        if missing_ids:
            failures.append(f"{len(missing_ids)} live claim IDs absent from PDF text")
        if missing_statements:
            failures.append(f"{len(missing_statements)} exact current statements absent from PDF text")
        if missing_receipts:
            failures.append(f"{len(missing_receipts)} current receipt hashes absent from PDF text")
        if blank_pages:
            failures.append(f"{len(blank_pages)} blank or near-blank pages")
        if clipped_blocks:
            failures.append(f"{len(clipped_blocks)} pages contain out-of-page text blocks")
        if replacement_glyph_pages:
            failures.append(f"{len(replacement_glyph_pages)} pages contain replacement glyphs")
        if non_a4_pages:
            failures.append(f"{len(non_a4_pages)} pages are not A4")
        if not all(cover_checks.values()):
            failures.append("cover content mismatch")
        if not all(metadata_checks.values()):
            failures.append("PDF metadata mismatch")

        reports.append(
            {
                "branch": paper.branch,
                "path": paper.pdf,
                "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "page_count": len(document),
                "page_character_min": min(page["characters"] for page in pages),
                "page_character_max": max(page["characters"] for page in pages),
                "blank_pages": blank_pages,
                "clipped_blocks": clipped_blocks,
                "replacement_glyph_pages": replacement_glyph_pages,
                "non_a4_pages": non_a4_pages,
                "cover_checks": cover_checks,
                "metadata": metadata,
                "metadata_checks": metadata_checks,
                "last_page_excerpt": last[:1000],
                "live_claims": len(branch_claims),
                "missing_claim_ids": missing_ids,
                "missing_authoritative_statements": missing_statements,
                "missing_receipt_hashes": missing_receipts,
                "failures": failures,
                "status": "PASS" if not failures else "HALT",
            }
        )
        document.close()

    result = {
        "schema": "sft-v3-final-publication-pdf-mechanical-audit/1",
        "scope": "seven complete field-wide final-candidate PDFs",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "halts": sum(report["status"] != "PASS" for report in reports),
            "pages_inspected": sum(report["page_count"] for report in reports),
            "live_claims_verified": sum(report["live_claims"] for report in reports),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        f"publication PDF audit v1: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['pages_inspected']:,} pages inspected"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
