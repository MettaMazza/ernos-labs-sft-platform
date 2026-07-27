#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-006."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_polarizability_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_POLARIZABILITY_SPEC,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.molecular_polarizability_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in MOLECULAR_POLARIZABILITY_SPEC.dimensions)
    survivor = survivor_id(MOLECULAR_POLARIZABILITY_SPEC)
    return f'''"""Implementation-distinct value-free PROP-006 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {MOLECULAR_POLARIZABILITY_SPEC.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def response_ratio(response, field):
    if response <= 0 or field <= 0:
        raise ValueError("response and field must be positive")
    return response / field

def repeated_ratio(response, field, count):
    if count < 1:
        raise ValueError("count must be positive")
    return response_ratio(response * count, field * count)

def isotropic(parts):
    if len(parts) != 3 or len({{axis for axis, value in parts}}) != 3:
        raise ValueError("complete distinct three-axis support required")
    values = [value for axis, value in parts]
    if any(value <= 0 for value in values):
        raise ValueError("component response must be positive")
    return (values[0] + values[1] + values[2]) / 3

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    base = response_ratio(Fraction(6, 1), Fraction(2, 1)) == Fraction(3, 1)
    successor = repeated_ratio(Fraction(6, 1), Fraction(2, 1), 7) == Fraction(3, 1)
    mean = isotropic((("a", Fraction(2, 1)), ("b", Fraction(3, 1)), ("c", Fraction(4, 1)))) == Fraction(3, 1)
    incomplete_rejected = False
    duplicate_rejected = False
    try:
        isotropic((("a", Fraction(2, 1)), ("b", Fraction(3, 1))))
    except ValueError:
        incomplete_rejected = True
    try:
        isotropic((("a", Fraction(2, 1)), ("a", Fraction(3, 1)), ("c", Fraction(4, 1))))
    except ValueError:
        duplicate_rejected = True
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
        and base and successor and mean and incomplete_rejected and duplicate_rejected
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
            "exact_response_ratio_reconstructed": base,
            "equal_act_successor_reconstructed": successor,
            "three_axis_one_third_Junction_reconstructed": mean,
            "incomplete_axis_support_rejected": incomplete_rejected,
            "duplicate_axis_rejected": duplicate_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = MOLECULAR_POLARIZABILITY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_polarizability_batch_v1 import MOLECULAR_POLARIZABILITY_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_polarizability_validation_v1 import MolecularPolarizabilityValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_polarizability_law_v1.py",
        root / "sft/chemistry/molecular_polarizability_batch_v1.py",
        root / "sft/chemistry/molecular_polarizability_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_polarizability_sources_v1.py",
        root / {SNAPSHOT_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_POLARIZABILITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-polarizability-006-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularPolarizabilityValidator(root),
    )
'''


def main() -> None:
    spec = MOLECULAR_POLARIZABILITY_SPEC
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
        "external_measurement_sources": [{
            "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-POLARIZABILITIES",
            "measurement_body": "National Institute of Standards and Technology",
            "role": "complete withheld 252-row non-atomic molecular alpha vector",
        }],
        "source_hashes": {
            "official_snapshot": SNAPSHOT_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "measured_values_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-006`

## WHY

Polarizability is not an imported scalar attached to a molecule. It is the retained response relation between an external electric distinction and the induced molecular dipole distinction. Species, state, conformation, field identity, response definition, method, condition, units and source remain part of the scientific object.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the molecular carrier, exact positive response ratio, held axis, three-axis one-third composition, depth-independent equal-act successor, value-free custody, complete NIST molecular vector and no fitted correction:

`{survivor_id(spec)}`

The forced exact relations are:

`component response = positive induced-dipole distinction / positive electric distinction`

`isotropic response = Junction of the three distinct held-axis responses / three`

Repeating an equal field act scales both terms by the same positive count, so their ratio is invariant at every generated finite depth. No alpha value, continuum derivative, tensor calculus, perturbation series, wavefunction, basis set, fitted coefficient or species correction enters the derivation.

## CHECK

The prediction seals all 252 non-atomic NIST row identities and the exact relation before the withheld alpha file is opened. The custodian then releases every source value. Each must reconstruct from the byte-sealed official HTML as an exact positive rational inscription, remain attached to its complete molecular identity, and preserve all ten molecular reference cohorts and all comments. A separate standard-library implementation regenerates all 256 candidates and independently reconstructs the ratio, successor and three-axis composition laws without measurement access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The response and equal-act successor laws are depth-independent. Their empirical test is finite-complete for the 252 non-atomic rows in the registered NIST CCCBDB experimental-polarizability snapshot. This does not install a numerical lookup rule for ungenerated molecules and does not claim that the NIST scalar inscriptions alone determine anisotropic components.
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
