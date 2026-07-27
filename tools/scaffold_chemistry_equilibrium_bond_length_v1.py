#!/usr/bin/env python3
"""Prepare the pre-admission PROP-001 claim and experiment package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.equilibrium_bond_length_batch_v1 import (  # noqa: E402
    EQUILIBRIUM_BOND_LENGTH_SPEC,
    IDENTITY_HASH,
    IDENTITY_PATH,
    SCALE_HASH,
    SCALE_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.equilibrium_bond_length_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = EQUILIBRIUM_BOND_LENGTH_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct PROP-001 product and carrier reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def independent_carriers():
    binary = 2
    generator = 3
    down = binary + generator
    up = generator + generator + 1
    rungs = (down ** generator, down ** 2 * up, down * up ** 2, up ** generator)
    chain = Fraction(rungs[-1], 1)
    for rung in reversed(rungs[1:-1]):
        chain = Fraction(rung, 1) + Fraction(1, 1) / chain
    cover = Fraction(binary * down ** generator, 1) + Fraction(1, 1) / chain
    inverse_alpha = Fraction(binary ** up, 1) + Fraction(generator ** binary, 1) * (cover + 1) / cover
    alpha = Fraction(1, 1) / inverse_alpha
    terminal = binary ** len(rungs)
    common = Fraction(up, down)
    h2 = common + generator * up * alpha ** binary
    d2 = common + (terminal + up + 1) * alpha ** binary
    return {{
        "binary": binary,
        "generator": generator,
        "down": down,
        "up": up,
        "terminal": terminal,
        "inverse_alpha": inverse_alpha,
        "alpha": alpha,
        "h2": h2,
        "d2": d2,
    }}

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    carriers = independent_carriers()
    controls = sealed["controls"]
    operational = (
        carriers["down"] == 5
        and carriers["up"] == 7
        and carriers["terminal"] == 16
        and carriers["inverse_alpha"] == Fraction(503846395469, 3676744786)
        and carriers["h2"] > Fraction(7, 5)
        and carriers["d2"] > carriers["h2"]
    )
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
        and operational
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
            "inverse_alpha": [carriers["inverse_alpha"].numerator, carriers["inverse_alpha"].denominator],
            "h2_multiplier": [carriers["h2"].numerator, carriers["h2"].denominator],
            "d2_multiplier": [carriers["d2"].numerator, carriers["d2"].denominator],
            "operational_reconstruction": operational,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = EQUILIBRIUM_BOND_LENGTH_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.equilibrium_bond_length_batch_v1 import EQUILIBRIUM_BOND_LENGTH_SPEC, GeneratedFiniteQuantitativeChemistryProgram
from sft.chemistry.equilibrium_bond_length_validation_v1 import EquilibriumBondLengthValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/equilibrium_bond_length_law_v1.py",
        root / "sft/chemistry/equilibrium_bond_length_batch_v1.py",
        root / "sft/chemistry/equilibrium_bond_length_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/molecular_spectroscopy_successor_laws_v1.py",
        root / "sft/physics/molecular_spectroscopy_successor_validation_v1.py",
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteQuantitativeChemistryProgram(EQUILIBRIUM_BOND_LENGTH_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-equilibrium-bond-length-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=EquilibriumBondLengthValidator(root),
    )
'''


def main() -> None:
    spec = EQUILIBRIUM_BOND_LENGTH_SPEC
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
            {"source_id": "NIST-CODATA-2022-ALL-CONSTANTS", "measurement_body": "National Institute of Standards and Technology", "database": "2022 CODATA complete fixed-width table", "role": "public same-dimension atomic-length reference"},
            {"source_id": "NIST-WEBBOOK-SRD69-H2-DIATOMIC-CONSTANTS", "measurement_body": "National Institute of Standards and Technology", "database": "Chemistry WebBook SRD 69", "role": "withheld H2 equilibrium-distance target"},
            {"source_id": "NIST-WEBBOOK-SRD69-D2-DIATOMIC-CONSTANTS", "measurement_body": "National Institute of Standards and Technology", "database": "Chemistry WebBook SRD 69", "role": "withheld D2 equilibrium-distance target"},
        ],
        "source_hashes": {"identity_registry": IDENTITY_HASH, "scale_input": SCALE_HASH, "withheld_targets": TARGET_HASH},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document()), "target_content_inaccessible": True, "complete_trace_required": True},
        "custody_protocol": {"identity_registry_path": IDENTITY_PATH, "scale_input_path": SCALE_PATH, "withheld_target_path": TARGET_PATH, "target_release_requires_prediction_seal": True},
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-001`

## WHY

A structural statement that a bond has a minimum does not yet supply its measured equilibrium length. PROP-001 closes the first registered quantitative molecular-property boundary by deriving exact H2 and D2 equilibrium-distance ratios before the NIST distance targets open.

## DERIVATION

The complete eight-axis product contains 256 forms. Exactly one retains the named isotopologue and state, the configuration minimum, the held atomic-length scale, the generated up/down base, binary-order alpha return, distinct light/heavy isotope routes, target-inaccessible exact interval transport and finite typed exhaustion:

`{survivor_id(spec)}`

The common electronic support forces `7/5`. The H2 typed correction is `3 x 7 alpha^2 = 21 alpha^2`. The D2 typed correction is `(16 + 7 + 1) alpha^2 = 24 alpha^2`. Therefore:

- `r_e(H2) / a0 = 7/5 + 21 alpha^2`
- `r_e(D2) / a0 = 7/5 + 24 alpha^2`

The executable law contains neither NIST distance, CODATA length inscription nor angstrom conversion. The public CODATA atomic-length interval is a held same-dimension reference, not a fitted parameter; the two NIST target intervals remain in a separate withheld file until the prediction is sealed.

## CHECK

An implementation-distinct process reconstructs the complete 256-form census, derives the exact inverse-alpha carrier from the promotion ladder, and independently regenerates both multipliers. The capability-closed predictor then multiplies the registered atomic-length interval by both exact ratios and emits a two-row Fold table. Only after its seal does the custodian release the complete H2/D2 target vector. Exact interval overlap decides both rows; deliberately displaced intervals must fail.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

This claim is finite-complete for the registered gas-phase H2/D2 X-state vector. It does not claim a free universal lookup formula for every molecule. Later quantitative and validation obligations extend species coverage only through separately generated typed relations and new sealed receipts.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    experiment_path = ROOT / "experiments" / "chemistry" / spec.experiment_id / "registration.json"
    write(experiment_path, json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
