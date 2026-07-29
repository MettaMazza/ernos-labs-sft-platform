#!/usr/bin/env python3
"""Add missing current claim statements and receipts to publication papers.

The current model-admitted census is authoritative. This additive reconciliation
does not rewrite historical prose; it exposes exact current statement and
receipt strings that an earlier successor manuscript omitted or paraphrased.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADING = "## Current authoritative statement and receipt reconciliation"


@dataclass(frozen=True)
class Target:
    branch: str
    path: str


TARGETS = (
    Target("mathematics", "publications/successors/mathematics/FROM_FOLD_TO_MATHEMATICS_PAPER_001_V1_5.md"),
    Target("information_science", "publications/successors/information_science/FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md"),
    Target("computation", "publications/successors/computation/AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md"),
    Target("quantum_computation", "publications/successors/quantum_computation/THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md"),
    Target("physics", "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_3.md"),
    Target("chemistry", "publications/successors/chemistry/FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md"),
    Target("materials", "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md"),
)


def current_claims() -> dict[str, list[dict]]:
    document = json.loads((ROOT / "census/claims.json").read_text())
    result: dict[str, list[dict]] = {}
    for claim in document["claims"]:
        if claim.get("model_admitted"):
            result.setdefault(claim["branch"], []).append(claim)
    return result


def gaps(text: str, claims: list[dict]) -> list[dict]:
    result = []
    for claim in claims:
        statement_missing = claim["statement"] not in text
        receipt_missing = claim["receipt_hash"] not in text
        if statement_missing or receipt_missing:
            result.append(
                {
                    **claim,
                    "statement_missing": statement_missing,
                    "receipt_missing": receipt_missing,
                }
            )
    return result


def appendix(rows: list[dict]) -> str:
    lines = [
        HEADING,
        "",
        "The current model-admitted census is authoritative at claim level. The",
        "entries below expose exact current statement or receipt strings that the",
        "earlier successor prose omitted or paraphrased. Historical wording remains",
        "preserved elsewhere in the paper; this reconciliation does not retroactively",
        "rewrite a prediction, chronology, evidence class, result or receipt.",
        "",
    ]
    for row in rows:
        missing = []
        if row["statement_missing"]:
            missing.append("exact statement")
        if row["receipt_missing"]:
            missing.append("receipt hash")
        lines.extend(
            [
                f"### `{row['claim_id']}`",
                "",
                f"Earlier display gap: {', '.join(missing)}.",
                "",
                f"Current exact statement: {row['statement']}",
                "",
                f"Formal closure status: `{row['closure_status']}`.",
                "",
                f"Current external status: `{row['external_status']}`.",
                "",
                f"Model-admitted receipt: `{row['receipt_hash']}`.",
                "",
                f"Receipt path: `{row['receipt_path']}`.",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    claims_by_branch = current_claims()
    total = 0
    changed = 0
    for target in TARGETS:
        path = ROOT / target.path
        text = path.read_text(encoding="utf-8")
        rows = gaps(text, claims_by_branch[target.branch])
        total += len(rows)
        print(
            f"{target.branch}: {len(rows)} reconciliation entries; "
            f"{sum(row['statement_missing'] for row in rows)} statements; "
            f"{sum(row['receipt_missing'] for row in rows)} receipts"
        )
        if not args.apply or not rows or HEADING in text:
            continue
        marker = "## Data and code availability"
        if text.count(marker) != 1:
            raise SystemExit(f"data/code marker mismatch: {target.path}")
        text = text.replace(marker, appendix(rows) + marker, 1)
        path.write_text(text, encoding="utf-8")
        changed += 1
    action = "updated" if args.apply else "would update"
    print(f"claim-record reconciliation v1: {action} {changed} papers; {total} entries")


if __name__ == "__main__":
    main()
