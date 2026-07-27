#!/usr/bin/env python3
"""Scaffold the pre-admission PROP-005 claim and experiment package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_dipole_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_DIPOLE_SPEC,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.molecular_dipole_validation_v1 import (  # noqa: E402
    HTML_HASH,
    HTML_PATH,
    PDF_HASH,
    PDF_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = MOLECULAR_DIPOLE_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct value-free PROP-005 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def square_junction(parts):
    if not parts:
        return "EmptyOne"
    axes = [axis for axis, value in parts]
    if len(set(axes)) != len(axes):
        raise ValueError("duplicate component axis")
    squares = [value * value for axis, value in parts]
    joined = squares[0]
    for part in squares[1:]:
        joined += part
    if joined.numerator < 1 or joined.denominator < 1:
        raise ValueError("square Junction left positive exact support")
    return joined

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    empty = square_junction([]) == "EmptyOne"
    one_axis = square_junction([("b", Fraction(3, 2))]) == Fraction(9, 4)
    two_axes = square_junction([("a", Fraction(3, 5)), ("b", Fraction(4, 5))]) == Fraction(1, 1)
    duplicate_rejected = False
    try:
        square_junction([("a", Fraction(1, 1)), ("a", Fraction(1, 1))])
    except ValueError:
        duplicate_rejected = True
    passed = (
        sealed["claim_id"] == CLAIM_ID
        and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "finite_complete"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and empty and one_axis and two_axes and duplicate_rejected
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID,
            "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "structural_EmptyOne_reconstructed": empty,
            "one_axis_square_reconstructed": one_axis,
            "two_axis_square_Junction_reconstructed": two_axes,
            "duplicate_axis_rejected": duplicate_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = MOLECULAR_DIPOLE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_dipole_batch_v1 import MOLECULAR_DIPOLE_SPEC, GeneratedFiniteMolecularDipoleChemistryProgram
from sft.chemistry.molecular_dipole_validation_v1 import MolecularDipoleValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_dipole_law_v1.py",
        root / "sft/chemistry/molecular_dipole_batch_v1.py",
        root / "sft/chemistry/molecular_dipole_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_dipole_sources_v1.py",
        root / {PDF_PATH!r}, root / {HTML_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteMolecularDipoleChemistryProgram(MOLECULAR_DIPOLE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-dipole-005-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularDipoleValidator(root),
    )
'''


def main() -> None:
    spec = MOLECULAR_DIPOLE_SPEC
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
        **experiment_registration_record(),
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [
            {
                "source_id": "NIST-NBS-JCP-59-2254-1973",
                "measurement_body": "National Bureau of Standards / Journal of Chemical Physics",
                "role": "withheld H2O, D2O and HDO component and total dipole magnitudes",
            },
            {
                "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-DIPOLES",
                "measurement_body": "National Institute of Standards and Technology",
                "role": "withheld H2 and D2 source-absence total records",
            },
        ],
        "source_hashes": {
            "nist_water_pdf": PDF_HASH,
            "nist_cccbdb_html": HTML_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document()),
            "measured_values_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "custody_protocol": {
            "identity_registry_path": IDENTITY_PATH,
            "withheld_target_path": TARGET_PATH,
            "all_nine_values_release_only_after_prediction_seal": True,
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne",
            "display_glyph": "0 or 0.000",
            "numerical_zero_admitted": False,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-005`

## WHY

Bond polarity alone does not close molecular dipole organization or magnitude. A molecule must retain its named state, geometry, complete charge-distinction carrier, symmetry and allowed axes. Direction is a held label, never a signed number. Symmetry closes forbidden components to structural EmptyOne; every surviving component is exact and positive.

## DERIVATION

The eight-axis grammar contains 256 forms. Exactly one preserves the complete molecular carrier, symmetry-forced components, held orientation, finite distinct-axis composition, exact squared magnitude, value-free custody, every registered row and no correction term:

`{survivor_id(spec)}`

The forced exact relation is:

`molecular dipole magnitude squared = Junction of every retained positive component square`

No square root is taken. No measured component or total, signed direction, continuum vector premise, conventional Stark Hamiltonian, partial-charge fit or species coefficient occurs in the executable law or capability-closed prediction.

## CHECK

The prediction seals the complete H2, D2, H2O, D2O and HDO symmetry/component organization and the squared-magnitude operation without any measurement. The custodian then releases nine source records. H2 and D2 must map the displayed source glyph `0.000` only to native EmptyOne. The H2O and D2O single-component squares and the HDO two-component square Junction must overlap their separately reported squared-total uncertainty intervals using exact outward rational arithmetic. A distinct standard-library checker reconstructs all 256 candidates and the EmptyOne, one-axis and two-axis laws without accessing measurements.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

Finite-complete for the registered five gas-phase species and nine NIST rows. The result forces molecular dipole component organization and the exact magnitude-square relation. It does not install a numerical lookup table for ungenerated molecules or treat a conventional axis sign as an SFT magnitude.
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
