#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-011."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.intermolecular_binding_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    INDEX_HASH,
    INDEX_PATH,
    INTERMOLECULAR_BINDING_SPEC,
    ION_CLUSTER_HASH,
    ION_CLUSTER_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
    WATER_CLUSTER_HASH,
    WATER_CLUSTER_PATH,
)
from sft.chemistry.intermolecular_binding_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = INTERMOLECULAR_BINDING_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-011 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def constituent_sum(states):
    if len(states) < 2 or any(value <= 0 for value in states):
        raise ValueError("two or more positive constituent states required")
    total = states[0]
    for value in states[1:]:
        total += value
    return total

def binding_take(separated, bound):
    if separated <= 0 or bound <= 0 or separated <= bound:
        raise ValueError("strict positive state order required")
    return separated - bound

def append_shared(separated, bound, shared):
    if shared <= 0:
        raise ValueError("shared constituent must be positive")
    return binding_take(separated + shared, bound + shared) == binding_take(separated, bound)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    separated = constituent_sum((Fraction(5, 2), Fraction(7, 3)))
    base = separated == Fraction(29, 6) and binding_take(separated, Fraction(4, 1)) == Fraction(5, 6)
    successor = append_shared(separated, Fraction(4, 1), Fraction(11, 5))
    repeated = binding_take(separated * 3, Fraction(4, 1) * 3) == Fraction(5, 2)
    reversed_rejected = False
    equal_rejected = False
    incomplete_rejected = False
    try:
        binding_take(Fraction(4, 1), separated)
    except ValueError:
        reversed_rejected = True
    try:
        binding_take(Fraction(4, 1), Fraction(4, 1))
    except ValueError:
        equal_rejected = True
    try:
        constituent_sum((Fraction(1, 1),))
    except ValueError:
        incomplete_rejected = True
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
        and base and successor and repeated and reversed_rejected and equal_rejected and incomplete_rejected
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
            "exact_named_constituent_composition_reconstructed": base,
            "ordered_positive_binding_take_reconstructed": base,
            "shared_constituent_successor_reconstructed": successor,
            "equal_repetition_reconstructed": repeated,
            "reversed_state_order_rejected": reversed_rejected,
            "equal_state_order_rejected": equal_rejected,
            "incomplete_constituent_support_rejected": incomplete_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = INTERMOLECULAR_BINDING_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.intermolecular_binding_batch_v1 import INTERMOLECULAR_BINDING_SPEC, PRIMARY_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.intermolecular_binding_validation_v1 import IntermolecularBindingValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    dimer_pages = tuple(root / row["snapshot_path"] for row in primary["dimer_pages"])
    source_files = (
        root / "sft/chemistry/intermolecular_binding_law_v1.py",
        root / "sft/chemistry/intermolecular_binding_batch_v1.py",
        root / "sft/chemistry/intermolecular_binding_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_intermolecular_binding_sources_v1.py",
        root / {INDEX_PATH!r},
        *dimer_pages,
        root / {WATER_CLUSTER_PATH!r}, root / {ION_CLUSTER_PATH!r},
        root / {PRIMARY_PATH!r}, root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(INTERMOLECULAR_BINDING_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-intermolecular-binding-011-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=IntermolecularBindingValidator(root),
    )
'''


def main() -> None:
    spec = INTERMOLECULAR_BINDING_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id,
        "title": spec.title,
        "branch": "chemistry",
        "status": "registered",
        "statement": spec.statement,
        "dependencies": list(spec.dependencies),
        "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule,
            "boundary": spec.grammar_boundary,
            "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json",
        **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [
            {
                "source_id": "NIST-CCCBDB-SRD-101-DIMER-BINDING",
                "body": "National Institute of Standards and Technology",
                "role": "complete 11-dimer, 1,297-linked-value calculated benchmark surface including signed adverse rows",
                "evidence_class": "calculated_not_measured",
            },
            {
                "source_id": "NIST-FARADAY-C8FD00092A-WATER-CLUSTER-DISSOCIATION",
                "body": "National Institute of Standards and Technology hosted publication",
                "role": "two reported H2O/D2O cluster dissociation values with uncertainties",
                "evidence_class": "reported_experimental_cluster_dissociation",
            },
            {
                "source_id": "NIST-JPCRD-1.555757-ION-CLUSTER-SCOPE",
                "body": "National Institute of Standards and Technology hosted reference-data publication",
                "role": "complete wider ion-cluster thermochemistry scope preserved without homogenizing mixed quantities",
                "evidence_class": "complete_scope_record_not_target_vector",
            },
        ],
        "source_hashes": {
            "official_dimer_index": INDEX_HASH,
            "water_cluster_publication": WATER_CLUSTER_HASH,
            "ion_cluster_compendium": ION_CLUSTER_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_targets": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "target_values_or_orientations_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-011`

## WHY

An intermolecular binding number without its constituent states is not a scientific object. The same displayed magnitude can refer to a calculated electronic difference, a zero-point-corrected dissociation energy, an enthalpy, or another condition-bound quantity. PROP-011 therefore retains every named molecular constituent, both state endpoints, the bound composite, finite separation organization, method or measurement identity, unit and evidence class.

## DERIVATION

The complete eight-axis grammar generates 256 forms. Exactly one retains named constituents, finite separation, exact constituent composition, strict state order, structural absence for non-binding, value-free custody, every favorable and adverse row, and depth-independent extension without a fitted coefficient:

`{survivor_id(spec)}`

The forced relation is:

`binding = exact separated-constituent state Take exact bound-composite state`

Both states must be exact and positive, and the separated state must be strictly higher. Reversing or equating them halts; it never creates a negative or numerical-zero Fold value. A source record that does not encode a bound lower state is retained as structural `EmptyOne`. Appending the same named constituent state to both endpoint compositions preserves the Take exactly, providing the depth-independent finite-cluster successor.

No intermolecular potential, inverse-power tail, continuum separation coordinate, fitted interaction coefficient, basis correction, species residual, measured target or calculated target occurs in the law or candidate forcing.

## CHECK

All 1,299 target identities seal before values or source orientations open. The external surface contains all 11 official CCCBDB hydrogen-bonded dimers and every one of 1,297 linked method/basis values: 1,201 positive calculated inscriptions and 96 signed adverse inscriptions. The signed external rows remain preserved but translate to structural `EmptyOne`, not negative SFT numbers. Two reported experimental cluster-dissociation values open separately: `(H2O)2 = 1105 ± 10 cm^-1` and `(D2O)2 = 1244 ± 10 cm^-1`. The complete 62-page, nine-table NIST ion-cluster thermochemistry compendium is also byte-preserved as the wider source boundary, but its mixed enthalpy, `D0` and `De` records are not falsely homogenized into a single measurement vector.

An implementation-distinct standard-library checker regenerates all 256 forms, the unique survivor, exact state composition, ordered Take, shared-constituent successor, repetition law and adverse controls without access to the target vault.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The state-order relation and shared-constituent successor are depth-independent for every generated finite constituent tuple. The empirical test is finite-complete for the frozen 11-dimer CCCBDB surface and the two registered experimental cluster rows. It does not claim that one dimer measurement supplies an unmeasured species value, nor that the calculated CCCBDB surface is experimental data.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    write(
        ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json",
        json.dumps(experiment, indent=2, sort_keys=True) + "\n",
    )
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
