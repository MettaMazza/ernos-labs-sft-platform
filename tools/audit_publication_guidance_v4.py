#!/usr/bin/env python3
"""Corrected final manuscript gate following the preserved v3 halt.

V3 correctly exposed the need for an explicit Physics closure qualification,
but its generic section matcher also treated the technical heading “Fold
abstract-machine law” as the paper Abstract. V4 corrects that matcher and
classifies exact current theorem statements as protected for British-spelling
review. Every other v3 requirement is preserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import audit_publication_guidance_v3 as v3


def exact_section(text: str, kind: str) -> str:
    patterns = {
        "abstract": r"(?im)^##\s+Abstract\s*$",
        "status": r"(?im)^##\s+Current status[^\n]*$",
        "conclusion": r"(?im)^##\s+(?:\d+\.\s+)?(?:Complete-field\s+)?Conclusion\s*$",
        "limitations": r"(?im)^##\s+(?:\d+\.\s+)?(?:Scope,\s+)?Limitations?[^\n]*$|^##\s+(?:\d+\.\s+)?Dated completion, falsification and extension\s*$|^##\s+Reproducibility, falsification and extension boundary\s*$",
    }
    matches = list(re.finditer(patterns[kind], text))
    if not matches:
        return ""
    match = matches[-1]
    following = re.search(r"(?m)^##\s+", text[match.end() :])
    end = match.end() + following.start() if following else len(text)
    return text[match.start() : end]


def remaining_safe_british_changes(path: Path) -> dict:
    """Run the v2 proposal while treating exact theorem displays as literal."""
    old = v3.british.v1.PROTECTED_RECORD_MARKERS
    v3.british.v1.PROTECTED_RECORD_MARKERS = re.compile(
        old.pattern + r"|\*\*Theorem\.\*\*", re.IGNORECASE
    )
    try:
        return v3.british.v1.process(path, apply=False)
    finally:
        v3.british.v1.PROTECTED_RECORD_MARKERS = old


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claim_document = json.loads((v3.ROOT / "census/claims.json").read_text())
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in claim_document["claims"]:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    proofreading_record = v3.ROOT / "audits/FINAL_PUBLICATION_PROOFREADING_REVIEW_2026-07-29.md"
    reports = []

    for paper in v3.structural_v2.PAPERS:
        path = v3.ROOT / paper.path
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        claims = by_branch[paper.branch]
        structural = v3.structural_v1.audit_paper(
            paper, {claim["claim_id"] for claim in claims}
        )
        preserved = v3.preservation_report(paper, text, claims)
        british_review = remaining_safe_british_changes(path)
        abstract = exact_section(text, "abstract")
        status = exact_section(text, "status")
        conclusion = exact_section(text, "conclusion")
        limitations = exact_section(text, "limitations")
        delimiters = v3.delimiter_balance(text)
        duplicates = v3.duplicate_word_lines(text)
        stale = [
            wording
            for wording in v3.STALE_CURRENT_WORDING
            if wording.lower() in text.lower()
        ]
        eligible_repetitions = v3.dedup.selected_clauses(text)
        concept_doi = v3.CONCEPT_DOIS[paper.branch]

        checks = {
            "authoritative_context": len(claims) == paper.claims and preserved["pass"],
            "scientific_preservation": preserved["pass"],
            "scientific_change_control": "### Editorial change control" in text and not stale,
            "house_style": (
                british_review["safe_change_count"] == 0
                and "Copyright © 2026 Maria Smith" in text[:4000]
                and "29 July 2026" in text[:4000]
            ),
            "terminology": all(term in text for term in v3.TERMINOLOGY),
            "proof_and_evidence_verbs": (
                "Proof language is reserved for formal closure" in text
                and "confirmation only where" in text
            ),
            "paper_structure": structural["status"] == "PASS",
            "narrative_spine": all(
                word in text.lower() for word in ("dependency", "family", "boundary")
            ),
            "repetition_control": (
                "## Shared claim-record clauses" in text
                and len(eligible_repetitions) == 0
            ),
            "claim_sections": (
                preserved["pass"]
                and all(marker in text.lower() for marker in v3.CLAIM_MARKERS)
            ),
            "abstract": (
                bool(abstract)
                and f"{paper.claims:,}" in abstract
                and "open" in abstract.lower()
            ),
            "headline_findings": structural["required_surfaces"]["headline_findings"],
            "status_boxes": (
                bool(status)
                and "Formal status" in status
                and "Empirical status" in status
                and "Publication status" in status
            ),
            "adverse_corrected_updated": (
                "adverse" in text.lower()
                and any(word in text.lower() for word in ("correct", "halt", "supersed", "unresolved"))
            ),
            "mathematical_formatting": delimiters["balanced"],
            "tables": len(structural["table_shape_findings"]) == 0,
            "sources_and_references": (
                structural["required_surfaces"]["references"]
                and structural["required_surfaces"]["source_surface"]
                and not structural["broken_relative_links"]
            ),
            "prose_proofreading": (
                proofreading_record.exists()
                and not duplicates
                and not stale
                and "(c) 2026 Maria Smith" not in text[:4000]
            ),
            "template_rhythm": len(eligible_repetitions) == 0,
            "human_audit_machine_layers": "### Three reading levels" in text,
            "authorship_and_open_science": all(
                item in text for item in ("Maria Smith", "Ernos Labs", "CC BY 4.0", "Apache-2.0")
            ),
            "conclusion": (
                bool(conclusion)
                and f"{paper.claims:,}" in conclusion
                and "open" in conclusion.lower()
                and any(word in conclusion.lower() for word in ("adverse", "unresolved", "correction", "halt"))
            ),
            "limitations_and_frontier": (
                bool(limitations)
                and "open" in text.lower()
                and any(phrase in text.lower() for phrase in ("not permanent", "not permanently", "not the end", "dated completion"))
            ),
            "candidate_metadata_and_lineage": (
                paper.version in text
                and paper.published_doi in text
                and concept_doi in text
                and "FINAL PUBLICATION CANDIDATE" in text[:4000]
                and "NOT YET APPROVED OR DEPOSITED" in text[:4000]
            ),
        }
        failures = [name for name, passed in checks.items() if not passed]
        reports.append(
            {
                "branch": paper.branch,
                "path": paper.path,
                "candidate_version": paper.version,
                "current_record_doi": paper.published_doi,
                "concept_doi": concept_doi,
                "sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
                "live_claims": len(claims),
                "checks": checks,
                "preservation": preserved,
                "british_prose": british_review,
                "delimiter_balance": delimiters,
                "duplicate_word_findings": duplicates,
                "stale_current_wording": stale,
                "eligible_repeated_clauses": len(eligible_repetitions),
                "failures": failures,
                "status": "PASS" if not failures else "HALT",
            }
        )

    result = {
        "schema": "sft-v3-final-publication-manuscript-audit/4",
        "supersedes_gate_logic": "tools/audit_publication_guidance_v3.py",
        "preserved_v3_halt": "audits/FINAL_PUBLICATION_MANUSCRIPT_AUDIT_V3_2026-07-29.json",
        "corrections": [
            "match the paper Abstract heading exactly, not abstract-machine headings",
            "treat exact current theorem displays as protected spelling literals",
            "require the explicit Physics dated/non-permanent closure qualification",
        ],
        "guidance": "publication guidance.md",
        "scope": "seven complete field-wide successor manuscripts",
        "excludes": [
            "versioned release package regeneration",
            "PDF mechanical and visual QA",
            "Maria Smith final approval",
            "Zenodo publication",
        ],
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "halts": sum(report["status"] != "PASS" for report in reports),
            "live_claims_verified": sum(report["live_claims"] for report in reports),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = v3.ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    print(
        f"publication manuscript audit v4: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['live_claims_verified']:,} live claims verified"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
