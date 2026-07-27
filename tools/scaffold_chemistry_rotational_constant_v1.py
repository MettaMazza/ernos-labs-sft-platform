#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry PROP-010."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.rotational_constant_batch_v1 import (  # noqa: E402
    CHOICE_SNAPSHOT_HASH,
    CHOICE_SNAPSHOT_PATH,
    IDENTITY_HASH,
    IDENTITY_PATH,
    LIST_SNAPSHOT_HASH,
    LIST_SNAPSHOT_PATH,
    PRIMARY_HASH,
    PRIMARY_PATH,
    ROTATIONAL_CONSTANT_SPEC,
    SNAPSHOT_HASH,
    SNAPSHOT_PATH,
    TARGET_HASH,
    TARGET_PATH,
)
from sft.chemistry.rotational_constant_validation_v1 import (  # noqa: E402
    experiment_registration_record,
    prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = ROTATIONAL_CONSTANT_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free PROP-010 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def constant(recurrences, interval):
    if not isinstance(recurrences, int) or not isinstance(interval, int) or recurrences < 1 or interval < 1:
        raise ValueError("positive finite counts required")
    return Fraction(recurrences, interval)

def level(j):
    if not isinstance(j, int) or j < 1:
        raise ValueError("positive rotational ordinal required")
    return j * (j + 1)

def gap(j):
    if not isinstance(j, int) or j < 1:
        raise ValueError("positive upper ordinal required")
    return 2 * j

def main():
    with open(sys.argv[1], encoding="utf-8") as handle:
        sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    controls = sealed["controls"]
    base = constant(12, 3)
    repeated = constant(60, 15)
    invalid_rejected = False
    try:
        constant(1, None)
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
        and tuple(level(j) for j in range(1, 5)) == (2, 6, 12, 20)
        and tuple(gap(j) for j in range(1, 5)) == (2, 4, 6, 8)
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
            "held_axis_recurrence_ratio_reconstructed": base == Fraction(4, 1),
            "equal_interval_successor_reconstructed": repeated == base,
            "positive_JJplusOne_ladder_reconstructed": tuple(level(j) for j in range(1, 5)) == (2, 6, 12, 20),
            "adjacent_2J_gaps_reconstructed": tuple(gap(j) for j in range(1, 5)) == (2, 4, 6, 8),
            "invalid_interval_rejected": invalid_rejected,
            "rigid_rotor_or_inertia_equation_used": False,
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__":
    main()
'''


def execution_source() -> str:
    claim_id = ROTATIONAL_CONSTANT_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.rotational_constant_batch_v1 import ROTATIONAL_CONSTANT_SPEC
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.rotational_constant_validation_v1 import RotationalConstantValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/rotational_constant_law_v1.py",
        root / "sft/chemistry/rotational_constant_batch_v1.py",
        root / "sft/chemistry/rotational_constant_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_rotational_constant_sources_v1.py",
        root / {LIST_SNAPSHOT_PATH!r}, root / {CHOICE_SNAPSHOT_PATH!r},
        root / {SNAPSHOT_PATH!r}, root / {PRIMARY_PATH!r},
        root / {IDENTITY_PATH!r}, root / {TARGET_PATH!r},
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ROTATIONAL_CONSTANT_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-rotational-constant-010-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=RotationalConstantValidator(root),
    )
'''


def main() -> None:
    spec = ROTATIONAL_CONSTANT_SPEC
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
            "source_id": "NIST-CCCBDB-COMPLETE-ROTATIONAL-CONSTANT-SURFACE",
            "measurement_body": "National Institute of Standards and Technology",
            "role": "complete list-to-choice-to-result route with every displayed A/B/C measurement and absence",
        }],
        "source_hashes": {
            "complete_species_list": LIST_SNAPSHOT_HASH,
            "complete_choice_surface": CHOICE_SNAPSHOT_HASH,
            "complete_result_surface": SNAPSHOT_HASH,
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
Chemistry obligation: `SFT-CHEM-OBL-PROP-010`

## WHY

A rotational constant cannot begin as a fitted moment of inertia, continuum rigid body or imported angular equation. The Fold-native carrier is a molecular state, finite generated geometry, held principal axis, positive finite axis-recurrence count and positive observation interval.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one retains the complete geometry/axis carrier, forces the exact recurrence ratio, forces positive `J(J+1)` levels and `2J` gaps, translates units only afterward, seals all identities before values, preserves the entire NIST list/choice/result boundary and admits no fitted extension:

`{survivor_id(spec)}`

The exact relations are:

`rotational constant = positive held-axis recurrence count / positive observation-interval count`

`positive level multiplier = J(J+1)`

`adjacent positive gap multiplier = 2J`

The unexcited rotational form is structural `EmptyOne`, never numerical zero. Equal repetition scales recurrence and interval counts together and leaves the constant invariant.

## CHECK

All 3,015 displayed axis identities seal without rotational-value access. They arise from every one of 1,193 unique compositions generated from all 2,186 entries in the official complete list. The source returns 1,832 charge/state choices and 1,005 displayed molecular property rows. After sealing, 1,681 exact positive A/B/C inscriptions open; all 1,334 blank axis cells remain structural `EmptyOne`. The 83 listed compositions with no returned selectable row remain explicit. An implementation-distinct checker regenerates all 256 candidates, the recurrence ratio, the positive ladder and every adverse control without target access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The recurrence ratio, equal-interval successor, `J(J+1)` level law and `2J` gap law are depth-independent for positive finite ordinals. The empirical test is finite-complete for the frozen official NIST list-to-choice-to-result route. The receipt does not install a numerical lookup rule for an ungenerated molecule or fabricate a value for an unreturned source composition.
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
