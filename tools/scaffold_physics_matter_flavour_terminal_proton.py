#!/usr/bin/env python3
"""Scaffold terminal proton/electron claim and experiment packages."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.matter_flavour_terminal_proton_laws_v1 import TERMINAL_PROTON_SPEC as SPEC  # noqa: E402
from sft.physics.matter_flavour_terminal_proton_validation_v1 import EMPIRICAL_SPEC  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402
from tools.scaffold_physics_measurement_claims import experiment_registration  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    package = ROOT / "claims" / SPEC.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": SPEC.claim_id,
        "title": SPEC.title,
        "branch": "physics",
        "status": "registered",
        "statement": SPEC.statement,
        "dependencies": list(SPEC.dependencies),
        "provenance_classes": [row.value for row in SPEC.provenance],
        "candidate_grammar": {
            "generator": SPEC.generation_rule,
            "boundary": SPEC.grammar_boundary,
            "completeness_certificate": sha256_identity(completeness_record(SPEC)),
        },
        "excluded_inputs": list(SPEC.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "intended_certificate": "One engine receipt requiring all 2,048 typed forms, one survivor, implementation-distinct exact reconstruction, target-inaccessible sealed prediction and the complete CODATA interval.",
        "empirical_protocol": f"experiments/physics/{EMPIRICAL_SPEC.experiment_id}/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-24",
    }
    axes = "\n".join(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in SPEC.axes)
    witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in SPEC.witnesses)
    exclusions = "\n".join(f"- {row}" for row in SPEC.exclusions)
    note = f"""# {SPEC.claim_id}: WHY / DERIVATION / CHECK

## WHY

{SPEC.statement}

The earlier non-overlap is retained permanently. This successor uses the
observational-derivation empirical prediction protocol: observation informs an
explicit candidate law, the target is then inaccessible to execution, the
engine seals the unique generated consequence, and comparison occurs afterward.

## DERIVATION

Grammar boundary: {SPEC.grammar_boundary}

The complete eleven-axis grammar contains 2,048 forms. Exactly one survives:

`{survivor_id(SPEC)}`

{axes}

Base: {SPEC.induction_base}

Successor: {SPEC.induction_step}

Exact result: {SPEC.exact_result}

## CHECK

{witnesses}

The engine regenerates all 2,048 forms, retains one survivor, passes four
hostile controls, requires an implementation-distinct exact reconstruction,
seals the target-free algebraic prediction and only then releases the complete
CODATA row. The empirical result does not erase the earlier adverse receipt.

## EXCLUSIONS

{exclusions}
"""
    execution = '''"""Official execution binding for terminal proton/electron precision."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_proton_execution_v1 import build_terminal_proton_execution


def build_execution(root: Path):
    return build_terminal_proton_execution(root, Path(__file__))
'''
    write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "execution.py", execution)
    write(package / "STATUS.md", f"# {SPEC.claim_id}\n\nStatus: `registered`\n")
    experiment = ROOT / "experiments" / "physics" / EMPIRICAL_SPEC.experiment_id
    write(experiment / "registration.json", json.dumps(experiment_registration(EMPIRICAL_SPEC), indent=2) + "\n")
    print(f"scaffolded {SPEC.claim_id}")


if __name__ == "__main__":
    main()
