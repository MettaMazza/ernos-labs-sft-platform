#!/usr/bin/env python3
"""Scaffold terminal CKM and baryon-transport claim packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.matter_flavour_terminal_ckm_laws_v1 import TERMINAL_SPECS  # noqa: E402
from sft.physics.matter_flavour_terminal_ckm_validation_v1 import EMPIRICAL_SPEC_BY_ID  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402
from tools.scaffold_physics_measurement_claims import experiment_registration  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for item in TERMINAL_SPECS:
        empirical = EMPIRICAL_SPEC_BY_ID[item.claim_id]
        package = ROOT / "claims" / item.claim_id
        registration = {
            "$schema": "../../governance/claim.schema.json",
            "claim_id": item.claim_id,
            "title": item.title,
            "branch": "physics",
            "status": "registered",
            "statement": item.statement,
            "dependencies": list(item.dependencies),
            "provenance_classes": [row.value for row in item.provenance],
            "candidate_grammar": {
                "generator": item.generation_rule,
                "boundary": item.grammar_boundary,
                "completeness_certificate": sha256_identity(completeness_record(item)),
            },
            "excluded_inputs": list(item.exclusions),
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
            "intended_certificate": "One engine receipt jointly requiring the complete 256-form structural census, exact target-free result, implementation-distinct reconstruction, seal-before-release custody and every registered external comparison row.",
            "empirical_protocol": f"experiments/physics/{empirical.experiment_id}/registration.json",
            "registered_by": "Maria Smith",
            "registration_date": "2026-07-24",
        }
        axes = "\n".join(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in item.axes)
        witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in item.witnesses)
        exclusions = "\n".join(f"- {row}" for row in item.exclusions)
        note = f"""# {item.claim_id}: WHY / DERIVATION / CHECK

## WHY

{item.statement}

The earlier adverse comparison is preserved permanently. This separately
versioned successor is an observational derivation: the target was already
known during development, but no measurement occurs in the executable relation
and no target value may select the generated survivor.

## DERIVATION

Grammar boundary: {item.grammar_boundary}

The complete eight-axis grammar contains 256 forms. Exactly one survives:

`{survivor_id(item)}`

{axes}

Base: {item.induction_base}

Successor: {item.induction_step}

Exact result: {item.exact_result}

## CHECK

{witnesses}

The engine regenerates every form, retains one survivor, runs four hostile
controls, requires an implementation-distinct exact reconstruction, seals the
formal prediction and only then releases every registered external row. The
post-seal comparison does not convert this into a blind forward discovery.

## EXCLUSIONS

{exclusions}
"""
        execution = f'''"""Official execution binding for {item.claim_id}."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_ckm_execution_v1 import build_terminal_execution


def build_execution(root: Path):
    return build_terminal_execution(root, {item.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {item.claim_id}\n\nStatus: `registered`\n")
        experiment = ROOT / "experiments" / "physics" / empirical.experiment_id
        write(experiment / "registration.json", json.dumps(experiment_registration(empirical), indent=2) + "\n")
        print(f"scaffolded {item.claim_id}")


if __name__ == "__main__":
    main()
