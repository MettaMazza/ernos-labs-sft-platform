#!/usr/bin/env python3
"""Final manuscript-level publication-guidance gate for seven SFT V3 papers.

This gate combines the corrected v2 structural expectations with live-census
statement/receipt checks, preservation against Git HEAD, current DOI lineage,
literal-aware British prose review, conclusion/frontier checks, Markdown
integrity and repetition control. PDF and deposit checks remain separate gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import apply_british_prose_v2 as british
import audit_publication_guidance_v1 as structural_v1
import audit_publication_guidance_v2 as structural_v2
import deduplicate_publication_claim_clauses_v1 as dedup
import verify_publication_scientific_preservation_v1 as preservation


ROOT = Path(__file__).resolve().parents[1]

CONCEPT_DOIS = {
    "mathematics": "10.5281/zenodo.21516145",
    "information_science": "10.5281/zenodo.21516915",
    "computation": "10.5281/zenodo.21518310",
    "quantum_computation": "10.5281/zenodo.21518312",
    "physics": "10.5281/zenodo.21520880",
    "chemistry": "10.5281/zenodo.21531454",
    "materials": "10.5281/zenodo.21532481",
}

TERMINOLOGY = (
    "Theorem",
    "Law",
    "Claim",
    "Constitution",
    "Derivation",
    "Prediction",
    "Observation",
    "Measurement",
    "Reconstruction",
    "Exact numerical correspondence",
    "Structural correspondence",
    "Boundary correspondence",
    "Compatibility",
    "Support",
    "Confirmation",
    "Validation",
    "Adverse result",
    "Unresolved result",
    "Implementation identity",
    "Foundational closure",
    "Field-wide closure",
    "Current-evidence closure",
    "Extension openness",
)

STALE_CURRENT_WORDING = (
    "PUBLICATION-READY",
    "PUBLISHED OPEN-ACCESS",
    "READY TO PUBLISH",
    "1,490 total V3 claims",
    "1,983 V3 claims",
    "Mathematics 1.3 publication",
)

CLAIM_MARKERS = (
    "candidate",
    "survivor",
    "control",
    "receipt",
    "dependency",
    "falsification",
    "source",
)


def section(text: str, name_pattern: str) -> str:
    headings = list(
        re.finditer(rf"(?im)^##\s+[^\n]*{name_pattern}[^\n]*$", text)
    )
    if not headings:
        return ""
    start = headings[-1].start()
    following = re.search(r"(?m)^##\s+", text[headings[-1].end() :])
    end = headings[-1].end() + following.start() if following else len(text)
    return text[start:end]


def delimiter_balance(text: str) -> dict[str, object]:
    pairs = {
        "inline_math": (text.count(r"\("), text.count(r"\)")),
        "display_math": (text.count(r"\["), text.count(r"\]")),
        "fenced_code": (text.count("```"), text.count("```") % 2),
    }
    return {
        "counts": {name: list(values) for name, values in pairs.items()},
        "balanced": (
            pairs["inline_math"][0] == pairs["inline_math"][1]
            and pairs["display_math"][0] == pairs["display_math"][1]
            and pairs["fenced_code"][1] == 0
        ),
    }


def duplicate_word_lines(text: str) -> list[dict[str, object]]:
    findings = []
    fenced = False
    pattern = re.compile(r"\b([A-Za-z]{3,})\s+\1\b", re.IGNORECASE)
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        stripped = line.lstrip()
        if fenced or stripped.startswith(("#", "-", "|", ">")):
            continue
        if any(
            marker in line
            for marker in (
                "**Theorem.",
                "Current exact statement:",
                "exact observation:",
                "Claim identity:",
            )
        ):
            continue
        match = pattern.search(line)
        if match:
            findings.append(
                {"line": number, "word": match.group(1), "text": line[:300]}
            )
    return findings


def preservation_report(paper, text: str, claims: list[dict]) -> dict:
    baseline = preservation.git_head_text(paper.path)
    original_shas = set(preservation.SHA.findall(baseline))
    current_shas = set(preservation.SHA.findall(text))
    original_literals = set(preservation.BACKTICK.findall(baseline))
    current_literals = set(preservation.BACKTICK.findall(text))
    original_claim_ids = set(preservation.CLAIM_ID.findall(baseline))
    current_claim_ids = set(preservation.CLAIM_ID.findall(text))

    refs = Counter(preservation.CLAUSE_REF.findall(text))
    headings = {
        clause_id: int(count)
        for clause_id, count in preservation.CLAUSE_HEADING.findall(text)
    }
    clause_failures = [
        f"{clause_id}: {refs[clause_id]} references; declared {declared}"
        for clause_id, declared in headings.items()
        if refs[clause_id] != declared
    ]
    clause_failures.extend(
        f"{clause_id}: reference has no appendix clause"
        for clause_id in refs
        if clause_id not in headings
    )

    result = {
        "missing_claim_ids": sorted(
            claim["claim_id"] for claim in claims if claim["claim_id"] not in text
        ),
        "missing_authoritative_statements": sorted(
            claim["claim_id"] for claim in claims if claim["statement"] not in text
        ),
        "missing_receipt_hashes": sorted(
            claim["claim_id"] for claim in claims if claim["receipt_hash"] not in text
        ),
        "original_sha256_identities_preserved": original_shas.issubset(current_shas),
        "original_literals_preserved": original_literals.issubset(current_literals),
        "claim_id_set_unchanged": original_claim_ids == current_claim_ids,
        "shared_clause_reference_failures": clause_failures,
    }
    result["pass"] = not any(
        (
            result["missing_claim_ids"],
            result["missing_authoritative_statements"],
            result["missing_receipt_hashes"],
            not result["original_sha256_identities_preserved"],
            not result["original_literals_preserved"],
            not result["claim_id_set_unchanged"],
            result["shared_clause_reference_failures"],
        )
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claim_document = json.loads((ROOT / "census/claims.json").read_text())
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in claim_document["claims"]:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    proofreading_record = ROOT / "audits/FINAL_PUBLICATION_PROOFREADING_REVIEW_2026-07-29.md"
    reports = []

    for paper in structural_v2.PAPERS:
        path = ROOT / paper.path
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        claims = by_branch[paper.branch]
        structural = structural_v1.audit_paper(paper, {c["claim_id"] for c in claims})
        preserved = preservation_report(paper, text, claims)
        concept_doi = CONCEPT_DOIS[paper.branch]
        british_review = british.v1.process(path, apply=False)
        conclusion = section(text, r"Conclusion")
        limitations = section(text, r"Limitations?|falsification and extension|Dated completion")
        abstract = section(text, r"Abstract")
        status = section(text, r"Current status")
        delimiters = delimiter_balance(text)
        duplicates = duplicate_word_lines(text)
        stale = [wording for wording in STALE_CURRENT_WORDING if wording.lower() in text.lower()]
        eligible_repetitions = dedup.selected_clauses(text)

        checks = {
            "authoritative_context": len(claims) == paper.claims and preserved["pass"],
            "scientific_preservation": preserved["pass"],
            "scientific_change_control": "### Editorial change control" in text and not stale,
            "house_style": (
                british_review["safe_change_count"] == 0
                and "Copyright © 2026 Maria Smith" in text[:4000]
                and "29 July 2026" in text[:4000]
            ),
            "terminology": all(term in text for term in TERMINOLOGY),
            "proof_and_evidence_verbs": (
                "Proof language is reserved for formal closure" in text
                and "confirmation only where" in text
            ),
            "paper_structure": structural["status"] == "PASS",
            "narrative_spine": (
                "dependency" in text.lower()
                and "family" in text.lower()
                and "boundary" in text.lower()
            ),
            "repetition_control": (
                "## Shared claim-record clauses" in text
                and len(eligible_repetitions) == 0
            ),
            "claim_sections": (
                preserved["pass"]
                and all(marker in text.lower() for marker in CLAIM_MARKERS)
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
            "authorship_and_open_science": (
                "Maria Smith" in text
                and "Ernos Labs" in text
                and "CC BY 4.0" in text
                and "Apache-2.0" in text
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
        "schema": "sft-v3-final-publication-manuscript-audit/3",
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
            "lines_read": sum(
                (ROOT / report["path"]).read_text(encoding="utf-8").count("\n") + 1
                for report in reports
            ),
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
        f"publication manuscript audit v3: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['live_claims_verified']:,} live claims verified"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
