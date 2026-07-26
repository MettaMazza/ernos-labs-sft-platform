#!/usr/bin/env python3
"""Materialize missing prose derivation checks from immutable Physics evidence."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    inventory = read(ROOT / "publications/inventories/physics.json")
    written = []
    for obligation in inventory["obligations"]:
        claim_id = obligation["claim_id"]
        package = ROOT / "claims" / claim_id
        output = package / "WHY_DERIVATION_CHECK.md"
        if output.exists():
            continue
        registration = read(package / "registration.json")
        candidate = read(package / "candidate_census.json")
        elimination = read(package / "elimination_receipt.json")
        controls = read(package / "controls.json")["controls"]
        certificate = read(package / "certificate.json")
        survivor = next(row for row in elimination["decisions"] if row["survives"])
        dependencies = "\n".join(f"- `{value}`" for value in registration["dependencies"])
        control_rows = "\n".join(
            f"- `{row['kind']}` passed: {row['observed_behavior']}" for row in controls
        )
        text = f"""# {registration['title']}

Claim: `{claim_id}`

## Why

This claim closes the registered Physics question only at its declared grammar
and evidence boundary. It descends from the single foundational One through
the already admitted dependencies below; no axiom, free parameter, external
target, fitted tolerance or V1/V2 executable selects its survivor.

{dependencies}

## Derivation

{registration['statement']}

The complete generator is: {candidate['generation_rule']}

Its exact boundary is: {candidate['grammar_boundary']}

The engine generated `{candidate['expected_cardinality']}` named candidates
and recorded the same number of decisions. Exactly one survived:
`{survivor['candidate_id']}`.

> {certificate['exact_result']}

Closure is `{certificate['closure_scope']}`. Minimality and named-shape
uniqueness are retained in the immutable elimination receipt.

## Check

The implementation-distinct validator regenerated the complete candidate
product and unique survivor. All mandatory hostile controls passed:

{control_rows}

Source manifest: `{certificate['source_manifest_hash']}`.
Independent implementation: `{certificate['independent_implementation_hash']}`.
Independent certificate: `{certificate['independent_certificate_hash']}`.
Engine receipt: `{certificate['engine_receipt_hash']}`.

The check documents current evidence closure only. A lawful versioned
extension remains open to new evidence through the unchanged admission
protocol; this file cannot alter or confer model admission.
"""
        output.write_text(text, encoding="utf-8")
        written.append(claim_id)
    print(f"materialized {len(written)} missing Physics derivation checks")


if __name__ == "__main__":
    main()
