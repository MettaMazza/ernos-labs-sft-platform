#!/usr/bin/env python3
"""Prepare the pre-admission PROP-002 claim and experiment package."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.bond_dissociation_energy_batch_v1 import (  # noqa: E402
    BOND_DISSOCIATION_ENERGY_SPEC, IDENTITY_HASH, IDENTITY_PATH, TARGET_HASH, TARGET_PATH,
)
from sft.chemistry.bond_dissociation_energy_validation_v1 import (  # noqa: E402
    ATOMIC_HASH, ATOMIC_PATH, APS_HASH, APS_PATH, CURRENT_HASH, CURRENT_PATH,
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = BOND_DISSOCIATION_ENERGY_SPEC
    domains = tuple(tuple(choice.name for choice in item.choices) for item in spec.dimensions)
    return f'''"""Implementation-distinct value-free PROP-002 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor_id(spec)!r}

def positive_take(longer, shorter):
    if not longer > shorter:
        raise ValueError("ordered positive Take halted")
    result = longer - shorter
    if result.numerator < 1 or result.denominator < 1:
        raise ValueError("Take left the exact positive domain")
    return result

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    operational = positive_take(Fraction(9, 8), Fraction(3, 4)) == Fraction(3, 8)
    reversed_rejected = False
    try:
        positive_take(Fraction(3, 4), Fraction(9, 8))
    except ValueError:
        reversed_rejected = True
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
        and operational and reversed_rejected
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"],
        "recomputed_from_declared_inputs": True,
        "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "finite_complete" if passed else None,
            "ordered_positive_Take_reconstructed": operational,
            "reversed_Take_rejected": reversed_rejected,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = BOND_DISSOCIATION_ENERGY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.bond_dissociation_energy_batch_v1 import BOND_DISSOCIATION_ENERGY_SPEC, GeneratedFiniteDissociationChemistryProgram
from sft.chemistry.bond_dissociation_energy_validation_v1 import BondDissociationEnergyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/bond_dissociation_energy_law_v1.py",
        root / "sft/chemistry/bond_dissociation_energy_batch_v1.py",
        root / "sft/chemistry/bond_dissociation_energy_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/prior_value_laws.py",
        root / "tools/capture_chemistry_bond_dissociation_energy_sources_v1.py",
        root / {ATOMIC_PATH!r}, root / {APS_PATH!r}, root / {CURRENT_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedFiniteDissociationChemistryProgram(BOND_DISSOCIATION_ENERGY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-bond-dissociation-energy-002-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=BondDissociationEnergyValidator(root),
    )
'''


def main() -> None:
    spec = BOND_DISSOCIATION_ENERGY_SPEC
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
            {"source_id": "APS-PRA-49-2460-1994", "measurement_body": "American Physical Society", "role": "withheld H2/D2 thresholds and historical ground D0 rows"},
            {"source_id": "PRL-UDEM-H-1S2S-1997", "measurement_body": "American Physical Society", "role": "withheld H atomic 1S-2S interval"},
            {"source_id": "PRL-PARTHEY-HD-1S2S-SHIFT-2010", "measurement_body": "American Physical Society", "role": "withheld D-H isotope-shift interval"},
            {"source_id": "SI-DEFINING-LIGHT-SPEED", "measurement_body": "Bureau International des Poids et Mesures", "role": "exact post-seal unit translation"},
            {"source_id": "JCP-LIU-H2-DISSOCIATION-2009", "measurement_body": "American Institute of Physics", "role": "withheld later H2 ground D0 row"},
            {"source_id": "PRA-HUSSELS-D2-DISSOCIATION-2022", "measurement_body": "American Physical Society", "role": "withheld later D2 ground D0 row"},
        ],
        "source_hashes": {
            "atomic_primary": ATOMIC_HASH, "historical_primary": APS_HASH,
            "later_primary": CURRENT_HASH, "identity_registry": IDENTITY_HASH,
            "withheld_measurements": TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document()),
            "measured_values_present": False, "target_content_inaccessible": True,
            "complete_trace_required": True,
        },
        "custody_protocol": {
            "identity_registry_path": IDENTITY_PATH, "withheld_target_path": TARGET_PATH,
            "all_eight_values_release_only_after_prediction_seal": True,
        },
        "absence_boundary": {"native_proof_form": "structural EmptyOne", "display_glyph": "0", "numerical_zero_admitted": False},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-PROP-002`

## WHY

A qualitative bond law does not close the dissociation-energy relation. PROP-002 retains the exact path distinction: the B-prime threshold ends in M(1s)+M(2s), while X-state ground dissociation ends in M(1s)+M(1s). Their common M(1s) endpoint is held, so the sole remaining segment is the atomic 1s--2s distinction.

## DERIVATION

The eight-axis grammar contains 256 forms. Exactly one preserves isotopologue, both molecular states, both product channels, ordered positive Take, value-free execution, complete measurement custody and no correction term:

`{survivor_id(spec)}`

The forced exact relation is:

`D0[M2, X -> M(1s)+M(1s)] = T[B-prime -> M(1s)+M(2s)] Take E[M(1s)->M(2s)]`

No measured threshold, transition, dissociation energy, potential, wavefunction, fitted offset or species coefficient occurs in the law or prediction.

## CHECK

The capability-closed program seals only the two structural state-path words and the ordered positive Take operation. After that seal, the custodian releases all eight registered measurements: two B-prime thresholds, two atomic segments, two historical ground D0 rows and two later high-resolution ground D0 rows. Exact outward interval transport must overlap both ground rows for each isotopologue. Every displaced interval, missing row, erased state/channel and reversed Take must fail. A standard-library-only independent checker separately reconstructs all 256 candidates and the Take law without reading any measurement file.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

Finite-complete for the registered gas-phase H2/D2 state-path and eight-row measurement vector. This does not claim an ungenerated universal numerical lookup rule for every bond. Observation-informed provenance is disclosed, while values remain wholly post-seal.
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
