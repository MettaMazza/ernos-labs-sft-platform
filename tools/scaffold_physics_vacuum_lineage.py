#!/usr/bin/env python3
"""Generate official claim packages for the V3 vacuum lineage batch."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402
from sft.physics.vacuum_lineage_laws_v1 import VACUUM_LINEAGE_SPECS  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for spec in VACUUM_LINEAGE_SPECS:
        package = ROOT / "claims" / spec.claim_id
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": spec.claim_id,
            "title": spec.title,
            "branch": "physics",
            "status": "registered",
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "provenance_classes": [item.value for item in spec.provenance],
            "candidate_grammar": {
                "generator": spec.generation_rule,
                "boundary": spec.grammar_boundary,
                "completeness_certificate": sha256_identity(completeness_record(spec)),
            },
            "excluded_inputs": list(spec.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": "Independent regeneration of all 256 registered forms, one survivor, exact arithmetic, hostile controls and depth-independent closure.",
            "empirical_protocol": None,
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-24",
        }
        axes = "\n".join(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in spec.axes)
        witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in spec.witnesses)
        exclusions = "\n".join(f"- {row}" for row in spec.exclusions)
        note = f"""# {spec.claim_id}: WHY / DERIVATION / CHECK

## WHY

{spec.statement}

The V1/V2 result is a mandatory reconstruction target but is never an executable premise or survivor selector. This V3 claim preserves the strongest prior statement at its exact scientific boundary. In the extraction lineage, the positive outward transfer and the complete returned-cycle ledger are separate claims so neither can be hidden by the other.

## DERIVATION

Grammar boundary: {spec.grammar_boundary}

The complete grammar contains 256 named forms. Exactly one retains every required coordinate:

`{survivor_id(spec)}`

{axes}

Base: {spec.induction_base}

Successor and termination: {spec.induction_step}

Exact result: {spec.exact_result}

## CHECK

{witnesses}

The engine must enumerate all 256 forms, retain one survivor, reject every changed-coordinate form, pass four hostile controls and receive an implementation-distinct exact reconstruction. External comparison occurs only in a separately sealed claim.

## EXCLUSIONS

{exclusions}
"""
        execution = f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
from sft.physics.vacuum_lineage_execution_v1 import build_vacuum_lineage_execution


def build_execution(root: Path):
    return build_vacuum_lineage_execution(root, {spec.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
