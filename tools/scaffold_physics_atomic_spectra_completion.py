#!/usr/bin/env python3
"""Scaffold same-strength atomic-spectrum claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.atomic_spectra_completion_laws_v1 import ATOMIC_SPECS  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for spec in ATOMIC_SPECS:
        package = ROOT / "claims" / spec.claim_id
        cardinality = 2 ** len(spec.axes)
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": spec.claim_id,
            "title": spec.title,
            "branch": "physics",
            "status": "registered",
            "statement": spec.statement,
            "dependencies": list(spec.dependencies),
            "provenance_classes": [row.value for row in spec.provenance],
            "candidate_grammar": {
                "generator": spec.generation_rule,
                "boundary": spec.grammar_boundary,
                "completeness_certificate": sha256_identity(completeness_record(spec)),
            },
            "excluded_inputs": list(spec.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": f"Complete {cardinality}-form census, one survivor, four hostile controls and implementation-distinct exact reconstruction.",
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

This is a clean V3 same-strength reconstruction of registered V1/V2 observational material. The observation identifies the required law; it does not enter the executable relation or select the survivor. External atomic comparison remains a separate capability-gated claim.

## DERIVATION

Grammar boundary: {spec.grammar_boundary}

The complete {len(spec.axes)}-axis grammar contains {cardinality} forms. Exactly one survives:

`{survivor_id(spec)}`

{axes}

Base: {spec.induction_base}

Successor: {spec.induction_step}

Exact result: {spec.exact_result}

## CHECK

{witnesses}

The engine regenerates all {cardinality} forms, retains one survivor, passes four hostile controls and requires a separate exact implementation to reconstruct the result without target access.

## EXCLUSIONS

{exclusions}
"""
        execution = f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
from sft.physics.atomic_spectra_completion_execution_v1 import build_atomic_spectra_execution


def build_execution(root: Path):
    return build_atomic_spectra_execution(root, {spec.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
