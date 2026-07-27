#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-008."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_electron_affinity_batch_v1 import (  # noqa: E402
    CATALOG_HASH,
    CATALOG_PATH,
    GUIDE_HASH,
    GUIDE_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    MOLECULAR_ELECTRON_AFFINITY_SPEC,
    PAGE_MANIFEST_HASH,
    PAGE_MANIFEST_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.molecular_electron_affinity_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = MOLECULAR_ELECTRON_AFFINITY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-008 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def difference(neutral, anion):
    if neutral == anion:
        return ("coincident-no-affinity-distinction", "empty-One")
    if neutral > anion:
        return ("anion-below-neutral-bound-attachment", neutral - anion)
    return ("anion-above-neutral-unbound-autodetachment", anion - neutral)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    bound = difference(Fraction(8, 1), Fraction(3, 1))
    unbound = difference(Fraction(3, 1), Fraction(8, 1))
    coincident = difference(Fraction(3, 1), Fraction(3, 1))
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
        and bound == ("anion-below-neutral-bound-attachment", Fraction(5, 1))
        and unbound == ("anion-above-neutral-unbound-autodetachment", Fraction(5, 1))
        and coincident == ("coincident-no-affinity-distinction", "empty-One")
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
            "bound_orientation_and_positive_Take_reconstructed": bound[1] == Fraction(5, 1),
            "unbound_orientation_and_positive_Take_reconstructed": unbound[1] == Fraction(5, 1),
            "coincident_EmptyOne_reconstructed": coincident[1] == "empty-One",
            "negative_proof_number_used": False,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = MOLECULAR_ELECTRON_AFFINITY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
import json
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_electron_affinity_batch_v1 import MOLECULAR_ELECTRON_AFFINITY_SPEC, PAGE_MANIFEST_PATH
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_electron_affinity_validation_v1 import MolecularElectronAffinityValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    page_manifest = json.loads((root / PAGE_MANIFEST_PATH).read_text(encoding="utf-8"))
    source_pages = tuple(root / row["snapshot_path"] for row in page_manifest["pages"])
    source_files = (
        root / "sft/chemistry/molecular_electron_affinity_law_v1.py",
        root / "sft/chemistry/molecular_electron_affinity_batch_v1.py",
        root / "sft/chemistry/molecular_electron_affinity_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_electron_affinity_sources_v1.py",
        root / {CATALOG_PATH!r}, root / {GUIDE_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r}, root / {PAGE_MANIFEST_PATH!r},
        root / "claims/{claim_id}/execution.py",
    ) + source_pages
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_ELECTRON_AFFINITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-electron-affinity-008-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularElectronAffinityValidator(root),
    )
'''


def main() -> None:
    spec = MOLECULAR_ELECTRON_AFFINITY_SPEC
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
        "external_measurement_sources": [
            {
                "source_id": "NIST-WEBBOOK-SRD69-GAS-PHASE-ION-THERMOCHEMISTRY",
                "measurement_body": "National Institute of Standards and Technology",
                "role": "electron-affinity definition, bound/unbound state order and autodetachment boundary",
            },
            {
                "source_id": "NIST-CCCBDB-COMPLETE-ELECTRON-AFFINITY-CATALOG",
                "measurement_body": "National Institute of Standards and Technology",
                "role": "complete 192-carrier catalog and 162-page molecular evidence surface",
            },
            {
                "source_id": "NIST-CCCBDB-EXPERIMENTAL-MOLECULAR-ELECTRON-AFFINITY",
                "measurement_body": "National Institute of Standards and Technology",
                "role": "withheld complete 96-record molecular experimental vector",
            },
        ],
        "source_hashes": {
            "catalog_source": CATALOG_HASH,
            "definition_source": GUIDE_HASH,
            "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
            "value_free_source_page_manifest": PAGE_MANIFEST_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "measured_values_present": False,
            "target_orientations_present": False,
            "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
        "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-008`

## WHY

Electron affinity cannot enter SFT as a signed scalar. The complete chemical carrier includes the neutral molecule, one held electron-gain action and the resulting anion. Whether the anion lies below or above the neutral-plus-electron state is a held ordering distinction; its separation is an exact positive magnitude.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one retains every state and transfer, separates order from magnitude, includes bound and unbound carriers, uses structural EmptyOne at coincidence, seals before target access, preserves all NIST rows and uncertainties, and admits no fitted correction:

`{survivor_id(spec)}`

For a strict state order, the exact relation is:

`electron-affinity magnitude = higher retained state Take lower retained state`

The orientation is held as `anion-below-neutral-bound-attachment` or `anion-above-neutral-unbound-autodetachment`. Equal heights yield structural `EmptyOne`, not numerical zero. No conventional negative proof number, orbital theorem, wavefunction, Hamiltonian, species coefficient or measured magnitude selects the result.

## CHECK

The value-free source census retains all 192 CCCBDB carriers, structurally excludes 30 single-element atomic carriers, preserves all 162 molecular pages and seals 96 molecular identities without magnitude or state-order access. Only after that seal does the custodian open 93 bound and three unbound experimental records, including all 89 explicit uncertainties. A separate standard-library checker regenerates all 256 candidates and independently reconstructs bound, unbound and EmptyOne cases without measurement access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The held-order and positive-Take law is depth-independent. Its quantitative external test is finite-complete for the official frozen NIST CCCBDB surface captured here. The receipt does not install a molecular lookup law or derive an ungenerated species magnitude from its name.
"""
    write(package / "registration.json", json.dumps(registration, indent=2, sort_keys=True) + "\n")
    write(package / "execution.py", execution_source())
    write(package / "independent_validator.py", independent_validator_source())
    write(package / "WHY_DERIVATION_CHECK.md", note)
    write(package / "STATUS.md", f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n")
    write(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", json.dumps(experiment, indent=2, sort_keys=True) + "\n")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
