#!/usr/bin/env python3
"""Generate claim packages for omitted matter/flavour completion laws."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.matter_flavour_completion_laws_v1 import BARYON_PHOTON_SPEC, MIXING_CORRESPONDENCE_SPEC  # noqa: E402
from sft.physics.matter_flavour_completion_laws_v2 import REMAINING_SPECS  # noqa: E402
from sft.physics.structural_constants import completeness_record, survivor_id  # noqa: E402


COMPLETION_SPECS = (BARYON_PHOTON_SPEC, MIXING_CORRESPONDENCE_SPEC) + REMAINING_SPECS


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    for item in COMPLETION_SPECS:
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
        axes = "\n".join(f"- `{axis.key}`: `{axis.survivor.name}` — {axis.survivor.reason}" for axis in item.axes)
        witnesses = "\n".join(f"- `{row.name}`: {row.statement}" for row in item.witnesses)
        exclusions = "\n".join(f"- {row}" for row in item.exclusions)
        note = f"""# {item.claim_id}: WHY / DERIVATION / CHECK

## WHY

{item.statement}

The prior result is a mandatory reconstruction target, never an executable premise or survivor selector.

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

The engine regenerates all 256 forms, retains one survivor, passes four hostile controls and requires an implementation-distinct reconstruction.

## EXCLUSIONS

{exclusions}
"""
        v2 = item.claim_id not in {{BARYON_PHOTON_SPEC.claim_id, MIXING_CORRESPONDENCE_SPEC.claim_id}}
        execution_import = "from sft.physics.matter_flavour_completion_execution_v2 import build_completion_execution_v2" if v2 else "from sft.physics.matter_flavour_completion_execution_v1 import build_completion_execution"
        execution_call = "build_completion_execution_v2" if v2 else "build_completion_execution"
        execution = f'''"""Official execution binding for {item.claim_id}."""

from pathlib import Path
{execution_import}


def build_execution(root: Path):
    return {execution_call}(root, {item.claim_id!r}, Path(__file__))
'''
        write(package / "registration.json", json.dumps(registration, indent=2) + "\n")
        write(package / "WHY_DERIVATION_CHECK.md", note)
        write(package / "execution.py", execution)
        write(package / "STATUS.md", f"# {item.claim_id}\n\nStatus: `registered`\n")
        print(f"scaffolded {item.claim_id}")


if __name__ == "__main__":
    main()
