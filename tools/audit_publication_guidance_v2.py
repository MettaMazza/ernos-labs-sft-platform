#!/usr/bin/env python3
"""Corrected v2 editorial audit for the seven complete-field papers.

Version 1 is preserved with its initial halted Physics expectation. Version 2
corrects only that declared expectation: the current Physics paper and machine
surface contain 257,776 generated candidates because its registered grammars
are not uniformly 256-wide. All audit logic and every other expectation remain
unchanged from v1.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import audit_publication_guidance_v1 as v1


PAPERS = tuple(
    replace(paper, candidates=257_776)
    if paper.branch == "physics"
    else paper
    for paper in v1.PAPERS
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    claims_data = json.loads((v1.ROOT / "census/claims.json").read_text())
    claims = claims_data if isinstance(claims_data, list) else claims_data["claims"]
    by_branch: dict[str, set[str]] = defaultdict(set)
    for claim in claims:
        if claim.get("model_admitted"):
            by_branch[claim["branch"]].add(claim["claim_id"])

    reports = [v1.audit_paper(paper, by_branch[paper.branch]) for paper in PAPERS]
    result = {
        "schema": "sft-v3-publication-guidance-editorial-audit/2",
        "supersedes_audit_logic": "tools/audit_publication_guidance_v1.py",
        "preserved_v1_halt": "audits/FINAL_PUBLICATION_PASS_BASELINE_2026-07-29.json",
        "correction": {
            "branch": "physics",
            "field": "expected_totals.candidates",
            "v1_incorrect_value": 94_208,
            "v2_authoritative_value": 257_776,
            "basis": "current Physics successor paper and heterogeneous registered candidate grammars",
        },
        "guidance": "publication guidance.md",
        "scope": "seven complete field-wide successor papers",
        "papers": reports,
        "summary": {
            "papers": len(reports),
            "passes": sum(report["status"] == "PASS" for report in reports),
            "requires_revision": sum(
                report["status"] != "PASS" for report in reports
            ),
            "bytes_read": sum(report["bytes"] for report in reports),
            "lines_read": sum(report["lines"] for report in reports),
            "words_read": sum(report["words"] for report in reports),
        },
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.json_out:
        destination = args.json_out
        if not destination.is_absolute():
            destination = v1.ROOT / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered)
    else:
        print(rendered, end="")

    print(
        f"publication guidance audit v2: {result['summary']['passes']}/"
        f"{result['summary']['papers']} pass; "
        f"{result['summary']['lines_read']:,} lines read"
    )
    return 0 if result["summary"]["requires_revision"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
