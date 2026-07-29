#!/usr/bin/env python3
"""Verify scientific preservation after the seven-paper editorial pass."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Paper:
    branch: str
    path: str
    version: str
    current_doi: str
    concept_doi: str


PAPERS = (
    Paper("mathematics", "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md", "1.5.0", "10.5281/zenodo.21627708", "10.5281/zenodo.21516145"),
    Paper("information_science", "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md", "1.4.0", "10.5281/zenodo.21627717", "10.5281/zenodo.21516915"),
    Paper("computation", "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md", "1.4.0", "10.5281/zenodo.21627721", "10.5281/zenodo.21518310"),
    Paper("quantum_computation", "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md", "1.4.0", "10.5281/zenodo.21627748", "10.5281/zenodo.21518312"),
    Paper("physics", "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md", "1.3.0", "10.5281/zenodo.21627765", "10.5281/zenodo.21520880"),
    Paper("chemistry", "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md", "1.3.0", "10.5281/zenodo.21627782", "10.5281/zenodo.21531454"),
    Paper("materials", "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md", "1.3.0", "10.5281/zenodo.21629306", "10.5281/zenodo.21532481"),
)


SHA = re.compile(r"sha256:[0-9a-f]{64}")
CLAIM_ID = re.compile(r"\bSFT-[A-Z0-9]+(?:-[A-Z0-9]+)+\b")
BACKTICK = re.compile(r"`([^`\n]+)`")
CLAUSE_REF = re.compile(r"Shared claim-record clause `([A-Z]+-S\d{3})` applies")
CLAUSE_HEADING = re.compile(
    r"(?m)^### `([A-Z]+-S\d{3})` — applied at (\d+) claim locations$"
)


def git_head_text(path: str) -> str:
    completed = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return completed.stdout.decode("utf-8")


def digest(values: set[str]) -> str:
    data = "\n".join(sorted(values)).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> int:
    claims_document = json.loads((ROOT / "census/claims.json").read_text())
    claims = claims_document["claims"]
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in claims:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    reports = []
    for paper in PAPERS:
        path = ROOT / paper.path
        text = path.read_text(encoding="utf-8")
        baseline = git_head_text(paper.path)
        branch_claims = by_branch[paper.branch]

        missing_ids = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if claim["claim_id"] not in text
        )
        missing_statements = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if claim["statement"] not in text
        )
        missing_receipts = sorted(
            claim["claim_id"]
            for claim in branch_claims
            if claim["receipt_hash"] not in text
        )

        original_shas = set(SHA.findall(baseline))
        current_shas = set(SHA.findall(text))
        original_literals = set(BACKTICK.findall(baseline))
        current_literals = set(BACKTICK.findall(text))
        original_claim_ids = set(CLAIM_ID.findall(baseline))
        current_claim_ids = set(CLAIM_ID.findall(text))

        refs = Counter(CLAUSE_REF.findall(text))
        headings = {
            clause_id: int(count)
            for clause_id, count in CLAUSE_HEADING.findall(text)
        }
        clause_failures = []
        for clause_id, declared in headings.items():
            if refs[clause_id] != declared:
                clause_failures.append(
                    f"{clause_id}: {refs[clause_id]} references; declared {declared}"
                )
        for clause_id in refs:
            if clause_id not in headings:
                clause_failures.append(f"{clause_id}: reference has no appendix clause")

        failures = []
        if missing_ids:
            failures.append(f"{len(missing_ids)} live claim IDs absent")
        if missing_statements:
            failures.append(f"{len(missing_statements)} authoritative statements absent")
        if missing_receipts:
            failures.append(f"{len(missing_receipts)} receipt hashes absent")
        if not original_shas.issubset(current_shas):
            failures.append(
                f"{len(original_shas-current_shas)} original SHA-256 identities absent"
            )
        if not original_literals.issubset(current_literals):
            failures.append(
                f"{len(original_literals-current_literals)} original code literals absent"
            )
        if original_claim_ids != current_claim_ids:
            failures.append("complete manuscript claim-ID set changed")
        if paper.version not in text:
            failures.append("candidate version absent")
        if paper.current_doi not in text or paper.concept_doi not in text:
            failures.append("existing DOI lineage absent")
        if clause_failures:
            failures.append(f"{len(clause_failures)} shared-clause reference failures")

        reports.append(
            {
                "branch": paper.branch,
                "path": paper.path,
                "live_claims": len(branch_claims),
                "missing_claim_ids": missing_ids,
                "missing_authoritative_statements": missing_statements,
                "missing_receipt_hashes": missing_receipts,
                "original_sha256_set_digest": digest(original_shas),
                "current_sha256_set_digest": digest(current_shas),
                "original_sha256_identities_preserved": original_shas.issubset(current_shas),
                "original_literal_set_digest": digest(original_literals),
                "current_literal_set_digest": digest(current_literals),
                "original_literals_preserved": original_literals.issubset(current_literals),
                "claim_id_set_unchanged": original_claim_ids == current_claim_ids,
                "shared_clause_count": len(headings),
                "shared_clause_reference_failures": clause_failures,
                "failures": failures,
                "status": "PASS" if not failures else "HALT",
            }
        )

    result = {
        "schema": "sft-v3-publication-scientific-preservation/1",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "halts": sum(report["status"] != "PASS" for report in reports),
        },
    }
    output = ROOT / "audits/FINAL_PUBLICATION_SCIENTIFIC_PRESERVATION_V1_2026-07-29.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(
        f"publication scientific preservation v1: "
        f"{result['summary']['passes']}/{result['summary']['papers']} pass"
    )
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
