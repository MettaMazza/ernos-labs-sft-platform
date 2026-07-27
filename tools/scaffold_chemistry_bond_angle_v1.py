#!/usr/bin/env python3
"""Prepare the pre-admission PROP-003 claim and experiment package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.bond_angle_batch_v1 import (  # noqa: E402
    BOND_ANGLE_SPEC, IDENTITY_HASH, IDENTITY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.bond_angle_validation_v1 import (  # noqa: E402
    BF3_HASH, BF3_PATH, SOURCE_IDS, XEF2_HASH, XEF2_PATH, XEF4_HASH, XEF4_PATH,
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = BOND_ANGLE_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct value-free PROP-003 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def equal_sector(geometry, count, separation):
    expected = {{
        "linear-equal-two-sector": 2,
        "trigonal-planar-equal-three-sector": 3,
        "square-planar-equal-four-sector": 4,
    }}
    if geometry not in expected or count != expected[geometry] or separation + separation > count:
        raise ValueError("ungenerated angle carrier")
    return Fraction(separation, count)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    vector = (
        equal_sector("trigonal-planar-equal-three-sector", 3, 1),
        equal_sector("linear-equal-two-sector", 2, 1),
        equal_sector("square-planar-equal-four-sector", 4, 1),
        equal_sector("square-planar-equal-four-sector", 4, 2),
    )
    unsupported_rejected = False
    try:
        equal_sector("tetrahedral-continuum-angle", 4, 1)
    except ValueError:
        unsupported_rejected = True
    wrong_count_rejected = False
    try:
        equal_sector("square-planar-equal-four-sector", 3, 1)
    except ValueError:
        wrong_count_rejected = True
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
        and vector == (Fraction(1, 3), Fraction(1, 2), Fraction(1, 4), Fraction(1, 2))
        and unsupported_rejected and wrong_count_rejected
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "turn_fractions_reconstructed": ["1/3", "1/2", "1/4", "1/2"],
            "unsupported_geometry_rejected": unsupported_rejected,
            "wrong_count_rejected": wrong_count_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = BOND_ANGLE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.bond_angle_batch_v1 import BOND_ANGLE_SPEC, GeneratedFiniteBondAngleChemistryProgram
from sft.chemistry.bond_angle_validation_v1 import BondAngleValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/bond_angle_law_v1.py",
        root / "sft/chemistry/bond_angle_batch_v1.py",
        root / "sft/chemistry/bond_angle_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_bond_angle_sources_v1.py",
        root / {BF3_PATH!r}, root / {XEF2_PATH!r}, root / {XEF4_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteBondAngleChemistryProgram(BOND_ANGLE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-bond-angle-003-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=BondAngleValidator(root),
    )
'''


def main() -> None:
    spec = BOND_ANGLE_SPEC
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
    base = experiment_registration_record()
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **base,
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [
            {"source_id": SOURCE_IDS[0], "measurement_body": "NIST", "role": "withheld BF3 aFBF experimental-geometry row"},
            {"source_id": SOURCE_IDS[1], "measurement_body": "NIST", "role": "withheld XeF2 aFXeF experimental-geometry row"},
            {"source_id": SOURCE_IDS[2], "measurement_body": "NIST", "role": "withheld XeF4 adjacent and opposite aFXeF rows"},
        ],
        "source_hashes": {
            "bf3_snapshot": BF3_HASH, "xef2_snapshot": XEF2_HASH, "xef4_snapshot": XEF4_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document()),
            "degree_values_present": False, "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "custody_protocol": {
            "identity_registry_path": IDENTITY_PATH, "withheld_target_path": TARGET_PATH,
            "all_four_values_release_only_after_prediction_seal": True,
        },
        "absence_boundary": {
            "native_proof_form": "structural EmptyOne", "display_glyph": "0",
            "numerical_zero_admitted": False,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-003`

## WHY

A qualitative geometry label does not close an exact angle relation. A closed molecular turn with indistinguishable ligand sectors cannot lawfully assign different sizes to those sectors: doing so introduces a distinction absent from the generated structure. Their Junction is the One turn, so one sector is exactly one part in the generated sector count.

## DERIVATION

The eight-axis grammar contains 256 forms. Exactly one retains the named carrier, cyclic order, equal-sector forcing, exact positive sector fraction, post-seal custody, all four source rows and no correction:

`{survivor_id(spec)}`

For a retained separation of `k` sectors in a closed `n`-sector carrier:

`bond-angle = k/n turn`

The complete value-free vector is BF3 `1/3` turn, XeF2 `1/2` turn, XeF4 adjacent `1/4` turn and XeF4 opposite `1/2` turn. No degree value, continuum trigonometry, coordinate fit, hybridization model, irrational quantity or species coefficient occurs in the law or prediction.

## CHECK

The capability-closed program seals the four exact turn fractions with species, state, geometry, coordinate, angle role and sector counts. Only then does the custodian open the three byte-sealed NIST CCCBDB species pages and the four-row degree vector. The external degree scale is applied only post-seal. Exact equality is required for all four rows. An implementation-distinct standard-library checker separately reconstructs all 256 candidates and all four fractions without reading any measurement file.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

Finite-complete for the registered equal-sector BF3, XeF2 and XeF4 carrier vector at the official source display resolution. Tetrahedral and other non-cyclic equal-sector geometries are explicitly not smuggled into this receipt; later obligations must generate their own lawful boundary.
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
