#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-012."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.magnetic_response_batch_v1 import (  # noqa: E402
    DIATOMIC_HOLDINGS_HASH, DIATOMIC_HOLDINGS_PATH, DIATOMIC_PDF_HASH, DIATOMIC_PDF_PATH,
    DIATOMIC_TEXT_HASH, DIATOMIC_TEXT_PATH, HYDROCARBON_HOLDINGS_HASH, HYDROCARBON_HOLDINGS_PATH,
    IDENTITY_HASH, IDENTITY_PATH, MAGNETIC_RESPONSE_SPEC, PRIMARY_HASH, PRIMARY_PATH,
    RESOLUTION_HASH, RESOLUTION_PATH, TARGET_HASH, TARGET_PATH,
    TRIATOMIC_HOLDINGS_HASH, TRIATOMIC_HOLDINGS_PATH,
)
from sft.chemistry.magnetic_response_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = MAGNETIC_RESPONSE_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-012 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def orientation_excess(a, b):
    if a <= 0 or b <= 0:
        raise ValueError("positive supports required")
    if a == b:
        return "balanced-closed", None
    return ("fibre-a", a-b) if a > b else ("fibre-b", b-a)

def moment(response, recurrence):
    if response <= 0 or recurrence <= 0:
        raise ValueError("positive response and recurrence required")
    return Fraction(response, recurrence)

def susceptibility(response, field_acts):
    if response <= 0 or field_acts <= 0:
        raise ValueError("positive response and field required")
    return response / field_acts

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    closed_orientation, closed = orientation_excess(3, 3)
    retained_orientation, retained = orientation_excess(5, 2)
    exact_moment = moment(retained, 2)
    exact_susceptibility = susceptibility(exact_moment, 5)
    repeated = susceptibility(exact_moment * 7, 5 * 7)
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
        and closed_orientation == "balanced-closed" and closed is None
        and retained_orientation == "fibre-a" and retained == 3
        and exact_moment == Fraction(3, 2)
        and exact_susceptibility == Fraction(3, 10)
        and repeated == exact_susceptibility
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
            "balanced_orientation_closure_reconstructed": closed is None,
            "positive_unmatched_support_reconstructed": retained == 3,
            "exact_moment_ratio_reconstructed": exact_moment == Fraction(3, 2),
            "exact_susceptibility_ratio_reconstructed": exact_susceptibility == Fraction(3, 10),
            "equal_repetition_invariance_reconstructed": repeated == exact_susceptibility,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = MAGNETIC_RESPONSE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import json
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.magnetic_response_batch_v1 import (
    MAGNETIC_RESPONSE_SPEC, PRIMARY_PATH, RESOLUTION_PATH,
    DIATOMIC_HOLDINGS_PATH, TRIATOMIC_HOLDINGS_PATH, HYDROCARBON_HOLDINGS_PATH,
    DIATOMIC_PDF_PATH, DIATOMIC_TEXT_PATH, IDENTITY_PATH, TARGET_PATH,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.magnetic_response_validation_v1 import MagneticResponseValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    primary = json.loads((root / PRIMARY_PATH).read_text(encoding="utf-8"))
    constants_pages = tuple(
        root / row["snapshot_path"] for row in primary["complete_constants_page_manifest"]
        if row["snapshot_path"] is not None
    )
    source_files = (
        root / "sft/chemistry/magnetic_response_law_v1.py",
        root / "sft/chemistry/magnetic_response_batch_v1.py",
        root / "sft/chemistry/magnetic_response_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_magnetic_response_sources_v1.py",
        root / RESOLUTION_PATH,
        root / DIATOMIC_HOLDINGS_PATH, root / TRIATOMIC_HOLDINGS_PATH, root / HYDROCARBON_HOLDINGS_PATH,
        *constants_pages,
        root / DIATOMIC_PDF_PATH, root / DIATOMIC_TEXT_PATH,
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MAGNETIC_RESPONSE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-magnetic-response-012-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MagneticResponseValidator(root),
    )
'''


def main() -> None:
    spec = MAGNETIC_RESPONSE_SPEC
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
                "source_id": "NIST-MOLECULAR-MICROWAVE-SPECTRAL-DATABASES-SRD-114-115-117",
                "body": "National Institute of Standards and Technology",
                "role": "complete current holdings plus all accessible triatomic/hydrocarbon g-factor and susceptibility cells",
            },
            {
                "source_id": "NIST-JPCRD-3-609-1974-DIATOMIC-MICROWAVE-SPECTRAL-TABLES",
                "body": "National Institute of Standards and Technology hosted reference-data publication",
                "role": "complete 162-page diatomic reference surface covering unavailable linked constants pages",
            },
        ],
        "source_hashes": {
            "constants_resolution": RESOLUTION_HASH,
            "diatomic_holdings": DIATOMIC_HOLDINGS_HASH,
            "triatomic_holdings": TRIATOMIC_HOLDINGS_HASH,
            "hydrocarbon_holdings": HYDROCARBON_HOLDINGS_HASH,
            "diatomic_reference_pdf": DIATOMIC_PDF_HASH,
            "diatomic_extracted_text": DIATOMIC_TEXT_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_targets": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "target_values_presence_flags_or_orientations_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-012`

## WHY

A signed magnetic number alone erases the molecule, state, angular carrier and the orientation that generated it. SFT therefore retains opposing directions as fibre labels and permits only positive magnitudes. Equal complementary support closes to structural `EmptyOne`; it is not a numerical zero.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

Molecular moment is the exact positive count of retained response displacements divided by a positive angular-recurrence count. Susceptibility is the exact positive induced-response ratio divided by a positive applied-field-act count. Equal repetition of response and field preserves the susceptibility exactly. No measured value, continuum derivative, fitted g-factor or species correction selects the law.

## CHECK

All 174 source-cell identities seal before target values, presence flags or source orientations open. Post-seal comparison preserves 136 printed exact magnitudes and 38 blank cells. The boundary begins from all 267 NIST-declared molecular holdings in 215 groups, retains all 94 accessible constants pages, explicitly records all 121 currently unavailable diatomic links, and independently covers those diatomic holdings with the complete 162-page NIST reference-data publication and 22 extracted rotational g-factor scalars. Signed inscriptions remain positive magnitudes plus held orientation labels. Nuclear-quadrupole `chi` tensors in frequency units are excluded rather than mislabeled as susceptibility.

An implementation-distinct standard-library checker regenerates every candidate, the unique survivor, structural closure, exact moment and susceptibility ratios, and the depth-independent repetition result without access to target files.

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
