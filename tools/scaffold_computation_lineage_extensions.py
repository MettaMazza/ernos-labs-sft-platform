#!/usr/bin/env python3
"""Preregister only the three same-strength Classical Computation extensions."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.computation.generated_law import completeness_record, survivor_id  # noqa: E402
from sft.computation.lineage_laws import LINEAGE_SPECS  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    write(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def module_name(spec) -> str:
    return f"sft.computation.{spec.group}.{spec.slug}.law"


def module_path(spec) -> str:
    return f"sft/computation/{spec.group}/{spec.slug}"


def render_execution(spec) -> str:
    return f'''"""Official execution binding for {spec.claim_id}."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.computation.generated_law import GeneratedComputationProgram
from {module_name(spec)} import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/computation/generated_law.py",
        root / "sft/computation/lineage_laws.py",
        root / "{module_path(spec)}/law.py",
        root / "claims/{spec.claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{spec.claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "{spec.claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
'''


def render_validator(spec) -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    return f'''"""Implementation-distinct product validator for {spec.claim_id}."""

from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}


def main() -> None:
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(coordinates) for coordinates in product(*DOMAINS)]
    received = [item["candidate_id"] for item in sealed["census"]["candidates"]]
    decisions = {{item["candidate_id"]: item["survives"] for item in sealed["decisions"]}}
    controls = sealed["controls"]; closure = sealed["closure"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated)
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and closure["scope"] == "depth_independent"
        and closure["minimality_passed"] is True
        and closure["named_shape_uniqueness_passed"] is True
        and {{item["kind"] for item in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(item["passed"] is True for item in controls)
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{"claim_id": CLAIM_ID, "generated_cardinality": len(generated), "unique_survivor": SURVIVOR if passed else None, "closure": "depth_independent" if passed else None}},
    }}, sort_keys=True))


if __name__ == "__main__": main()
'''


def render_why(spec) -> str:
    admitted = "\n".join(f"- `{d.key}` -> `{d.admitted_choice.name}`: {d.admitted_choice.reason}" for d in spec.dimensions)
    laws = "\n".join(f"- {law}" for law in spec.laws)
    witnesses = "\n".join(f"- `{w.name}`: {w.statement}" for w in spec.witnesses)
    exclusions = "\n".join(f"- {item}" for item in spec.boundary_exclusions)
    return f'''# {spec.title}

Claim: `{spec.claim_id}`

## WHY

{spec.why}

## DERIVATION

{spec.derivation}

Boundary:

> {spec.grammar_boundary}

The complete grammar contains 256 candidates across eight binary axes. Exactly one retains every requirement.

{admitted}

Forced result:

> {spec.exact_result}

Operational laws:

{laws}

Base:

> {spec.induction_base}

Successor:

> {spec.induction_step}

## CHECK

{spec.check}

{witnesses}

The false-premise, changed-source, changed-survivor and excluded-boundary controls must all reject. The independent validator regenerates the literal product without importing this scientific module.

## Exact limitation

{spec.limitations}

{exclusions}
'''


def main() -> None:
    for spec in LINEAGE_SPECS:
        module = ROOT / module_path(spec)
        write(module / "__init__.py", f'"""{spec.title}."""\n\nfrom .law import SPEC\n\n__all__ = ("SPEC",)\n')
        write(module / "law.py", f'"""{spec.title}."""\n\nfrom sft.computation.lineage_laws import LINEAGE_SPECS\n\nSPEC = next(item for item in LINEAGE_SPECS if item.claim_id == "{spec.claim_id}")\n\n__all__ = ("SPEC",)\n')
        claim = ROOT / "claims" / spec.claim_id
        write(claim / "execution.py", render_execution(spec))
        write(claim / "independent_validator.py", render_validator(spec))
        write(claim / "WHY_DERIVATION_CHECK.md", render_why(spec))
        write(claim / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered`\n")
        write_json(claim / "registration.json", {
            "$schema": "../../governance/claim.schema.json", "branch": "computation",
            "candidate_grammar": {"boundary": spec.grammar_boundary, "completeness_certificate": sha256_identity(completeness_record(spec)), "generator": spec.generation_rule},
            "claim_id": spec.claim_id, "dependencies": list(spec.dependencies), "empirical_protocol": None,
            "excluded_inputs": list(spec.boundary_exclusions), "intended_certificate": "Independent regeneration of all 256 candidates, the sole survivor, closure and controls.",
            "provenance_classes": ["forward_forcing"], "registered_by": "Maria Smith", "registration_date": "2026-07-24",
            "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"], "statement": spec.statement, "status": "registered", "title": spec.title,
        })
        print("scaffolded", spec.claim_id)


if __name__ == "__main__": main()
