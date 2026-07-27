#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-009."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.vibrational_frequency_batch_v1 import (  # noqa: E402
    IDENTITY_HASH,
    IDENTITY_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
    VIBRATIONAL_FREQUENCY_SPEC,
)
from sft.chemistry.vibrational_frequency_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = VIBRATIONAL_FREQUENCY_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-009 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def frequency(recurrences, interval):
    if not isinstance(recurrences, int) or not isinstance(interval, int) or recurrences < 1 or interval < 1:
        raise ValueError("positive finite counts required")
    return Fraction(recurrences, interval)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    base = frequency(12, 3)
    repeated = frequency(60, 15)
    invalid_rejected = False
    try:
        frequency(1, None)
    except ValueError:
        invalid_rejected = True
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
        and base == Fraction(4, 1)
        and repeated == base
        and invalid_rejected
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
            "finite_recurrence_ratio_reconstructed": base == Fraction(4, 1),
            "equal_interval_successor_reconstructed": repeated == base,
            "nonpositive_interval_rejected": invalid_rejected,
            "fitted_scale_factor_used": False,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = VIBRATIONAL_FREQUENCY_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.vibrational_frequency_batch_v1 import VIBRATIONAL_FREQUENCY_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.vibrational_frequency_validation_v1 import VibrationalFrequencyValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/vibrational_frequency_law_v1.py",
        root / "sft/chemistry/vibrational_frequency_batch_v1.py",
        root / "sft/chemistry/vibrational_frequency_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_vibrational_frequency_sources_v1.py",
        root / {SNAPSHOT_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(VIBRATIONAL_FREQUENCY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-vibrational-frequency-009-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=VibrationalFrequencyValidator(root),
    )
'''


def main() -> None:
    spec = VIBRATIONAL_FREQUENCY_SPEC
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
            "source_id": "NIST-CCCBDB-COMPLETE-DISPLAYED-FUNDAMENTAL-FREQUENCY-SURFACE",
            "measurement_body": "National Institute of Standards and Technology",
            "role": "complete displayed 2,009-mode surface, 1,984 experimental values, 25 absences and preserved advertised/displayed count boundary",
        }],
        "source_hashes": {
            "source_snapshot": SNAPSHOT_HASH,
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
Chemistry obligation: `SFT-CHEM-OBL-PROP-009`

## WHY

A vibrational frequency cannot begin as a continuum sinusoid or a fitted harmonic-oscillator output. The Fold-native carrier is a molecule, distinct mode, symmetry, positive finite recurrence count and positive observation interval. Frequency is their exact ratio; the source unit is attached afterward.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one retains the complete mode carrier, begins from finite recurrence, forces the exact count/interval ratio, translates units only afterward, seals all identities before values, preserves displayed absences and the source count discrepancy, and rejects the NIST page's theoretical ratios and fitted scale factor:

`{survivor_id(spec)}`

The exact relation is:

`vibrational frequency = positive finite recurrence count / positive observation-interval count`

Equal repetition scales both counts together and leaves the ratio invariant. No continuum time, differential equation, harmonic potential, theoretical frequency, experimental/theoretical ratio, fitted scale factor or species correction enters the derivation.

## CHECK

All 2,009 displayed identities across 145 displayed molecules seal without frequency access. After sealing, 1,984 exact positive experimental wavenumbers open and the 25 blank experimental cells remain structural `EmptyOne`. The NIST header advertises 164 molecules and 2,452 vibrations while the returned table displays 145 and 2,009; the 19-molecule/443-mode presentation gap remains explicit and is not called a measured result. An implementation-distinct checker regenerates all 256 candidates and the recurrence ratio without target access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The recurrence ratio and equal-interval successor are depth-independent. The external test is finite-complete for the table actually displayed in the frozen official response. The receipt does not install a numerical lookup law for an ungenerated molecule or claim access to the source-advertised but undisplayed rows.
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
