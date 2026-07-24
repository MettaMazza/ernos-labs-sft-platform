#!/usr/bin/env python3
"""Generate official claim packages for matter/flavour successors."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.matter_flavour_laws_v1 import MATTER_FLAVOUR_SPECS  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for item in MATTER_FLAVOUR_SPECS:
        package = ROOT / "claims" / item.claim_id
        registration = {
            "$schema": "../../governance/claim.schema.json", "claim_id": item.claim_id,
            "title": item.title, "branch": "physics", "status": "registered",
            "statement": item.statement, "dependencies": list(item.dependencies),
            "provenance_classes": [row.value for row in item.provenance],
            "candidate_grammar": {"generator": item.generation_rule, "boundary": item.grammar_boundary, "completeness_certificate": sha256_identity(completeness_record(item))},
            "excluded_inputs": list(item.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": "Independent regeneration of 256 registered forms, one survivor, exact arithmetic, hostile controls and depth-independent closure.",
            "empirical_protocol": None, "registered_by": "Maria Smith", "registration_date": "2026-07-24",
        }
        axis_rows = "\n".join(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in item.axes)
        witness_rows = "\n".join(f"- `{row.name}`: {row.statement}" for row in item.witnesses)
        exclusion_rows = "\n".join(f"- {row}" for row in item.exclusions)
        note = f"""# {item.claim_id}: WHY / DERIVATION / CHECK

## WHY

{item.statement}

The earlier SFT statement is a mandatory reconstruction target, never an executable premise or survivor selector. This V3 successor preserves the strongest exact result established in its complete grammar and explicitly repairs the earlier numerical-zero neutrino floor.

## DERIVATION

Grammar boundary: {item.grammar_boundary}

The complete eight-axis grammar contains 256 forms. Exactly one preserves every required coordinate:

`{survivor_id(item)}`

{axis_rows}

Base: {item.induction_base}

Successor: {item.induction_step}

Exact result: {item.exact_result}

## CHECK

{witness_rows}

The engine regenerates all 256 forms, retains one survivor, rejects every changed-coordinate form, passes four hostile controls and requires implementation-distinct exact reconstruction. External particle tables remain inaccessible until after this seal.

## EXCLUSIONS

{exclusion_rows}
"""
        execution = f'''"""Official execution binding for {item.claim_id}."""

from pathlib import Path
from sft.physics.matter_flavour_execution_v1 import build_matter_flavour_execution


def build_execution(root: Path):
    return build_matter_flavour_execution(root, {item.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {item.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {item.claim_id}")


if __name__ == "__main__":
    main()
