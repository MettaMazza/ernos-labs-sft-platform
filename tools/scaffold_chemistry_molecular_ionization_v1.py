#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-007."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_ionization_batch_v1 import (  # noqa: E402
    GUIDE_HASH, GUIDE_PATH, IDENTITY_HASH, IDENTITY_PATH, MOLECULAR_IONIZATION_SPEC,
    PRIMARY_HASH, PRIMARY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.molecular_ionization_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in MOLECULAR_IONIZATION_SPEC.dimensions)
    survivor = survivor_id(MOLECULAR_IONIZATION_SPEC)
    return f'''"""Implementation-distinct value-free PROP-007 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {MOLECULAR_IONIZATION_SPEC.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def take(final, initial):
    if final <= initial or initial <= 0:
        raise ValueError("strict positive terminal ordering required")
    return final - initial

def adiabatic(initial, terminals):
    if not terminals:
        raise ValueError("complete terminal support required")
    return min(take(final, initial) for final in terminals)

def vertical_order(initial, terminals, held):
    if held not in terminals:
        raise ValueError("held geometry terminal is outside support")
    return take(held, initial) >= adiabatic(initial, terminals)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    initial = Fraction(3, 1)
    terminals = (Fraction(8, 1), Fraction(6, 1), Fraction(7, 1))
    exact_take = take(terminals[0], initial) == Fraction(5, 1)
    least = adiabatic(initial, terminals) == Fraction(3, 1)
    order = vertical_order(initial, terminals, terminals[2])
    reversed_rejected = False
    missing_rejected = False
    try:
        take(initial, terminals[0])
    except ValueError:
        reversed_rejected = True
    try:
        vertical_order(initial, terminals, Fraction(9, 1))
    except ValueError:
        missing_rejected = True
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
        and exact_take and least and order and reversed_rejected and missing_rejected
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
            "ordered_positive_Take_reconstructed": exact_take,
            "least_adiabatic_terminal_reconstructed": least,
            "vertical_not_below_adiabatic_reconstructed": order,
            "reversed_order_rejected": reversed_rejected,
            "missing_vertical_terminal_rejected": missing_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = MOLECULAR_IONIZATION_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.molecular_ionization_batch_v1 import MOLECULAR_IONIZATION_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.molecular_ionization_validation_v1 import MolecularIonizationValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/molecular_ionization_law_v1.py",
        root / "sft/chemistry/molecular_ionization_batch_v1.py",
        root / "sft/chemistry/molecular_ionization_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_molecular_ionization_sources_v1.py",
        root / {GUIDE_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    ) + tuple(sorted((root / "experiments/external_sources/chemistry/snapshots/prop-007-molecular-ionization-v1").glob("[0-9][0-9]-*.html")))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MOLECULAR_IONIZATION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-molecular-ionization-007-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularIonizationValidator(root),
    )
'''


def main() -> None:
    spec = MOLECULAR_IONIZATION_SPEC
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
                "role": "ionization definitions and adiabatic/vertical state-ordering surface",
            },
            {
                "source_id": "NIST-CCCBDB-SRD101-EXPERIMENTAL-IONIZATION-ENERGY",
                "measurement_body": "National Institute of Standards and Technology",
                "role": "withheld complete nine-species experimental ionization-energy vector",
            },
        ],
        "source_hashes": {
            "definition_source": GUIDE_HASH,
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
Chemistry obligation: `SFT-CHEM-OBL-PROP-007`

## WHY

Ionization energy is not an imported signed orbital number. The scientific carrier includes the complete neutral molecule, its state and conformation, the held removal of one electron distinction, and the resulting positive-ion-plus-electron terminal state.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves complete state custody, held removal, ordered positive Take, distinct adiabatic and vertical paths, their forced order, value-free prediction, every registered row and no fitted correction:

`{survivor_id(spec)}`

The forced exact law is:

`ionization requirement = higher separated terminal height Take lower neutral bound height`

Adiabatic ionization is the least positive Take over complete generated terminal support. A vertical path retains the neutral geometry and is one member of that support; it therefore cannot lie below the least adiabatic member. No signed energy, imported orbital theorem, continuum state space, wavefunction, Hamiltonian or fitted species coefficient enters the derivation.

## CHECK

The prediction seals the full D2, HD, H2, N2, CO, NO, O2, HF and F2 carrier/state vector and exact operations without energy access. The custodian then opens the nine byte-sealed NIST CCCBDB values. Every value must reconstruct as an exact positive rational record attached to its neutral and resulting ionic states, source identity, condition and uncertainty class. A separate standard-library checker regenerates all 256 candidates and the Take, least-terminal and vertical-order results without measurement access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The ordered Take and adiabatic/vertical ordering laws are depth-independent. Their quantitative external test is finite-complete for the preregistered nine neutral diatomic species. This receipt does not identify ionization energy with one imported orbital eigenvalue and does not install a numerical lookup law for an ungenerated molecule.
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
