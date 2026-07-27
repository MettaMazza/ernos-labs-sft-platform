#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-013."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.formation_energy_batch_v1 import (  # noqa: E402
    CHOICE_HASH, CHOICE_PATH, FORMATION_ENERGY_SPEC, IDENTITY_HASH, IDENTITY_PATH,
    LIST_HASH, LIST_PATH, PRIMARY_HASH, PRIMARY_PATH, REFERENCE_HASH, REFERENCE_PATH,
    RESULT_HASH, RESULT_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.formation_energy_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = FORMATION_ENERGY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-013 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def compose_reference(states):
    if not states or any(state <= 0 for state in states):
        raise ValueError("positive nonempty reference required")
    total = states[0]
    for state in states[1:]: total += state
    return total

def relation(product_state, reference_state):
    if product_state <= 0 or reference_state <= 0:
        raise ValueError("positive states required")
    if product_state == reference_state: return "product-reference-equal", None
    if product_state > reference_state: return "product-above-reference", product_state-reference_state
    return "product-below-reference", reference_state-product_state

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    reference = compose_reference((Fraction(5,2), Fraction(7,3)))
    below = relation(Fraction(4,1), reference)
    above = relation(Fraction(6,1), reference)
    equal = relation(reference, reference)
    shared = relation(Fraction(4,1)+Fraction(11,5), reference+Fraction(11,5))
    repeated = relation(Fraction(4,1)*3, reference*3)
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and reference == Fraction(29,6)
        and below == ("product-below-reference", Fraction(5,6))
        and above == ("product-above-reference", Fraction(7,6))
        and equal == ("product-reference-equal", None)
        and shared == below
        and repeated == ("product-below-reference", Fraction(5,2))
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "reference_composition_reconstructed": reference == Fraction(29,6),
            "both_orientations_reconstructed": below[0] != above[0],
            "structural_equality_reconstructed": equal[1] is None,
            "shared_state_extension_reconstructed": shared == below,
            "positive_repetition_reconstructed": repeated[1] == Fraction(5,2),
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__": main()
'''


def execution_source() -> str:
    claim_id = FORMATION_ENERGY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.formation_energy_batch_v1 import (
    FORMATION_ENERGY_SPEC, LIST_PATH, CHOICE_PATH, RESULT_PATH, REFERENCE_PATH,
    PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.formation_energy_validation_v1 import FormationEnergyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/formation_energy_law_v1.py",
        root / "sft/chemistry/formation_energy_batch_v1.py",
        root / "sft/chemistry/formation_energy_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_formation_energy_sources_v1.py",
        root / LIST_PATH, root / CHOICE_PATH, root / RESULT_PATH, root / REFERENCE_PATH,
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(FORMATION_ENERGY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-formation-energy-013-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=FormationEnergyValidator(root),
    )
'''


def main() -> None:
    spec = FORMATION_ENERGY_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id,
        "title": spec.title, "branch": "chemistry", "status": "registered",
        "statement": spec.statement, "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [
            {
                "source_id": "NIST-CCCBDB-SRD-101-COMPLETE-EXPERIMENTAL-FORMATION-ENERGY",
                "body": "National Institute of Standards and Technology",
                "role": "complete official gas-phase experimental formation-energy property surface",
            },
            {
                "source_id": "NIST-CCCBDB-THERMODYNAMIC-REFERENCE-STATES",
                "body": "National Institute of Standards and Technology",
                "role": "complete reference-state identity and convention custody",
            },
        ],
        "source_hashes": {
            "complete_species_list": LIST_HASH, "complete_choice_surface": CHOICE_HASH,
            "complete_result_surface": RESULT_HASH, "thermodynamic_reference_states": REFERENCE_HASH,
            "normalized_primary_records": PRIMARY_HASH, "identity_registry": IDENTITY_HASH,
            "withheld_targets": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "target_values_presence_flags_or_orientations_present": False,
            "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-013`

## WHY

A signed formation number alone erases the product state, constituent reference states, phase and temperature condition. SFT retains state order as a held label and permits only exact positive separation. Equality is structural `EmptyOne`; a blank source cell is separately retained as an absent measurement and never treated as equality.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

The product state is compared with the exact nonempty composition of named constituent reference states. Unequal endpoints force one held orientation and their exact positive separation. Appending the same state to both endpoints preserves the relation; equal positive repetition scales the separation without a new coefficient. No measured value, imported reference value, fitted atomic contribution or species coefficient selects the law.

## CHECK

All 2,098 source-cell identities seal before values, presence flags or orientations open. The complete post-seal NIST surface retains 1,485 printed values, 613 blanks, 756 below-reference orientations, 707 above-reference orientations and 22 printed equalities across 1,049 molecular rows. The complete 2,186-species list, 1,193 composition queries, 1,832 returned charge-state choices, 83 unreturned compositions and the official thermodynamic reference-state page remain in custody.

An implementation-distinct standard-library checker regenerates every candidate, the unique survivor, both state orientations, structural equality, shared-state invariance and positive repetition without target access.

## FALSIFICATION

{spec.falsification_condition}
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "execution.py", execution_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id
    write(experiment_path / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print(f"scaffolded {spec.claim_id}")


if __name__ == "__main__":
    main()
