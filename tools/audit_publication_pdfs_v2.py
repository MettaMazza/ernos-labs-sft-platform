#!/usr/bin/env python3
"""Corrected PDF gate after the preserved v1 halt.

V1 found a real multiplication-mark renderer defect and also showed that exact
statements spanning a page break cannot be compared while repeating page
headers and footers remain in the extracted text stream. V2 preserves every v1
page and metadata check, removes only renderer-generated running matter before
statement comparison and normalises Unicode script characters exactly as the
renderer does.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import fitz

import audit_publication_pdfs_v1 as v1


SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ", "0123456789+-=()ni")
SUBSCRIPT = str.maketrans("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ", "0123456789+-=()aehijklmnoprstuvx")


def rendered_form(text: str) -> str:
    text = re.sub(
        r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ]+",
        lambda match: "^" + match.group(0).translate(SUPERSCRIPT),
        text,
    )
    text = re.sub(
        r"[₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ]+",
        lambda match: "_" + match.group(0).translate(SUBSCRIPT),
        text,
    )
    return v1.normal(text)


def content_text(page_texts: list[str]) -> str:
    kept = []
    for page in page_texts:
        for line in page.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.isdigit():
                continue
            if stripped.startswith("Maria Smith - 2026 - CC BY 4.0 -"):
                continue
            if "ERNOS LABS" in stripped and "PAPER 001" in stripped:
                continue
            kept.append(stripped)
    return " ".join(kept)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claims_document = json.loads((v1.ROOT / "census/claims.json").read_text())
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in claims_document["claims"]:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    reports = []
    for paper in v1.PAPERS:
        path = v1.ROOT / paper.pdf
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
        cleaned_text = content_text(page_texts)
        branch_claims = by_branch[paper.branch]
        missing_ids = sorted(
            claim["claim_id"] for claim in branch_claims if claim["claim_id"] not in complete_text
        )
        missing_statements = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if rendered_form(claim["statement"]) not in cleaned_text
        )
        missing_receipts = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if claim["receipt_hash"] not in complete_text
        )

        first = v1.normal(page_texts[0]) if page_texts else ""
        last = v1.normal(page_texts[-1]) if page_texts else ""
        cover_checks = {
            "title": paper.title in first,
            "author": "Maria Smith" in first,
            "version": bool(re.search(rf"\bVersion {re.escape(paper.version)}(?:\.0)?\b", first)),
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
            failures.append(f"{len(missing_statements)} exact current statements absent from cleaned PDF text")
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
        "schema": "sft-v3-final-publication-pdf-mechanical-audit/2",
        "preserved_v1_halt": "audits/FINAL_PUBLICATION_PDF_MECHANICAL_AUDIT_V1_2026-07-29.json",
        "renderer_correction": "single-asterisk emphasis no longer consumes exact multiplication strings",
        "comparison_correction": "running headers, footers and page numbers removed before page-spanning statement comparison",
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
            destination = v1.ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        f"publication PDF audit v2: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['pages_inspected']:,} pages inspected"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
