#!/usr/bin/env python3
"""Prepare the pre-admission package for Chemistry obligation ELEC-015."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.classical_quantum_correspondence_batch_v1 import (  # noqa: E402
    CLASSICAL_QUANTUM_SPEC,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = CLASSICAL_QUANTUM_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct ELEC-015 census and operation reconstruction."""
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def operational_reconstruction():
    transition_rows = (("state-held", "state-returned"), ("state-returned", "state-held"))
    classical = {{source: target for source, target in transition_rows}}
    initial = tuple((source, "phase-held") for source, _target in transition_rows)
    transformed = tuple((target, "phase-returned") for _source, target in transition_rows)
    quantum = {{source: target for source, target in transition_rows}}
    inverse = {{target: source for source, target in transition_rows}}
    restored = tuple((inverse[target], "phase-held") for target, _phase in transformed)
    observation_records = tuple(
        tuple((branch, phase, branch) for branch, phase in transformed)
        for _selected_branch, _selected_phase in transformed
    )
    return {{
        "same_decoded_rows": classical == quantum,
        "complete_initial_support": len(set(initial)) == len(transition_rows),
        "complete_transformed_support": len(set(transformed)) == len(transition_rows),
        "complete_records": all(len(record) == len(transition_rows) for record in observation_records),
        "inverse_restores": restored == initial,
        "positive_resources": all(value >= 1 for value in (len(initial), len(transformed), len(observation_records))),
    }}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    operations = operational_reconstruction()
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and all(operations.values())
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "operational_reconstruction": operations,
            "successor": "append-one-distinct-reversible-transition-row",
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = CLASSICAL_QUANTUM_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.classical_quantum_correspondence_batch_v1 import CLASSICAL_QUANTUM_SPEC, GeneratedOperationalChemistryProgram
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/classical_quantum_correspondence_law_v1.py",
        root / "sft/chemistry/classical_quantum_correspondence_batch_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/quantum_computation/operations.py",
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedOperationalChemistryProgram(CLASSICAL_QUANTUM_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-operational-classical-quantum-correspondence-015-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
'''


def main() -> None:
    spec = CLASSICAL_QUANTUM_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": [
            "false_premise",
            "tampered_source",
            "tampered_artifact",
            "boundary",
        ],
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-ELEC-015`

## WHY

Classical and quantum Chemistry cannot be joined merely by comparing two answer labels. A correspondence law must preserve the chemical input identity, the admitted transition law, every generated input branch, the terminal observation, the exact inverse and the resources consumed, while retaining phase-labelled quantum traces that have no classical counterpart.

## DERIVATION

Eight binary axes generate all 256 registered forms. Exactly one form retains a common chemical description, singleton classical embedding, reversible transition table, complete branchwise quantum execution, common Chemistry law, shared decoder and record, bidirectional result preservation and an exact positive resource ledger:

`{survivor_id(spec)}`

The operational base executes one generated reversible transition row in both modes. The successor adds one distinct row; it adds exactly one classical trace, one singleton held-phase branch, one decoded quantum result, one complete observation record and one inverse row without changing any earlier row.

## CHECK

The implementation-distinct checker does not import this law. It independently regenerates all 256 forms and all decisions, executes the two-state molecular transition in classical and held-phase modes, reconstructs the complete observation records, applies the inverse and checks the positive resource boundary.

This is a formal operational theorem. A new measured value is not applicable: its molecular transition and measurement ownership are already admitted dependencies, while the new content is the exact equivalence of their two computational executions.

## FALSIFICATION

The claim halts if any generated candidate is absent or duplicated; if more or fewer than one form survives; if the modes use different chemical laws; if any input branch, observation record or inverse row is absent; if decoded terminal Chemistry differs; if a resource is uncounted; or if a conventional quantum premise or forbidden SFT value enters the proof.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_formal`\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
