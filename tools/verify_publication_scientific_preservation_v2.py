#!/usr/bin/env python3
"""Final scientific-preservation gate after current-record reconciliation.

Version 1's initial halt remains preserved. Version 2 requires every current
authoritative claim statement and receipt to be displayed while retaining all
pre-editorial claim IDs, SHA-256 identities and code literals.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict

import verify_publication_scientific_preservation_v1 as v1


def main() -> int:
    document = json.loads((v1.ROOT / "census/claims.json").read_text())
    by_branch: dict[str, list[dict]] = defaultdict(list)
    for claim in document["claims"]:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].append(claim)

    reports = []
    for paper in v1.PAPERS:
        path = v1.ROOT / paper.path
        text = path.read_text(encoding="utf-8")
        baseline = v1.git_head_text(paper.path)
        branch_claims = by_branch[paper.branch]
        missing_ids = sorted(c["claim_id"] for c in branch_claims if c["claim_id"] not in text)
        missing_statements = sorted(c["claim_id"] for c in branch_claims if c["statement"] not in text)
        missing_receipts = sorted(c["claim_id"] for c in branch_claims if c["receipt_hash"] not in text)

        original_shas = set(v1.SHA.findall(baseline))
        current_shas = set(v1.SHA.findall(text))
        original_literals = set(v1.BACKTICK.findall(baseline))
        current_literals = set(v1.BACKTICK.findall(text))
        original_claim_ids = set(v1.CLAIM_ID.findall(baseline))
        current_claim_ids = set(v1.CLAIM_ID.findall(text))

        refs = Counter(v1.CLAUSE_REF.findall(text))
        headings = {
            clause_id: int(count)
            for clause_id, count in v1.CLAUSE_HEADING.findall(text)
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

        failures = []
        if missing_ids:
            failures.append(f"{len(missing_ids)} live claim IDs absent")
        if missing_statements:
            failures.append(f"{len(missing_statements)} authoritative statements absent")
        if missing_receipts:
            failures.append(f"{len(missing_receipts)} receipt hashes absent")
        if not original_shas.issubset(current_shas):
            failures.append(f"{len(original_shas-current_shas)} original SHA-256 identities absent")
        if not original_literals.issubset(current_literals):
            failures.append(f"{len(original_literals-current_literals)} original code literals absent")
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
                "original_sha256_identities_preserved": original_shas.issubset(current_shas),
                "original_literals_preserved": original_literals.issubset(current_literals),
                "claim_id_set_unchanged": original_claim_ids == current_claim_ids,
                "shared_clause_count": len(headings),
                "shared_clause_reference_failures": clause_failures,
                "failures": failures,
                "status": "PASS" if not failures else "HALT",
            }
        )

    result = {
        "schema": "sft-v3-publication-scientific-preservation/2",
        "preserved_v1_halt": "audits/FINAL_PUBLICATION_SCIENTIFIC_PRESERVATION_V1_2026-07-29.json",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(r["status"] == "PASS" for r in reports),
            "halts": sum(r["status"] != "PASS" for r in reports),
        },
    }
    output = v1.ROOT / "audits/FINAL_PUBLICATION_SCIENTIFIC_PRESERVATION_V2_2026-07-29.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"publication scientific preservation v2: {result['summary']['passes']}/{result['summary']['papers']} pass")
    return 0 if result["summary"]["halts"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
