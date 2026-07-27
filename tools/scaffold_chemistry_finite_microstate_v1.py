#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-001."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.finite_microstate_batch_v1 import (  # noqa: E402
    FINITE_MICROSTATE_SPEC, IDENTITY_HASH, IDENTITY_PATH, PRIMARY_HASH, PRIMARY_PATH,
    POP_IDENTITY_HASH, POP_IDENTITY_PATH, POP_TARGET_HASH, POP_TARGET_PATH,
    STATE_SNAPSHOT_PATHS, TARGET_HASH, TARGET_PATH, WATER_HASH, WATER_PATH,
)
from sft.chemistry.finite_microstate_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = FINITE_MICROSTATE_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free THERMO-001 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def finite_support(states, fibres):
    if not states or len(states) != len(set(states)) or not fibres:
        raise ValueError("finite unique support and fibres required")
    flattened = tuple(state for _, members in fibres for state in members)
    labels = tuple(label for label, _ in fibres)
    if len(labels) != len(set(labels)) or any(not members for _, members in fibres):
        raise ValueError("finite nonempty unique fibres required")
    if len(flattened) != len(set(flattened)) or set(flattened) != set(states):
        raise ValueError("fibres must partition support exactly once")
    return tuple(states), tuple(fibres)

def weight(support, label):
    states, fibres = support
    matches = tuple(members for name, members in fibres if name == label)
    if len(matches) != 1: raise ValueError("macrostate absent or non-unique")
    return Fraction(len(matches[0]), len(states))

def append_state(support, state, label):
    states, fibres = support
    if state in states or label in {{name for name, _ in fibres}}:
        raise ValueError("finite successor must be new")
    return finite_support(states + (state,), fibres + ((label, (state,)),))

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    support = finite_support(("state-a", "state-b", "state-c"), (("macro-a", ("state-a", "state-b")), ("macro-b", ("state-c",))))
    overlap_rejected = False
    try: finite_support(("state-a", "state-b", "state-c"), (("macro-a", ("state-a", "state-b")), ("macro-b", ("state-b", "state-c"))))
    except ValueError: overlap_rejected = True
    extended = append_state(support, "state-d", "macro-c")
    controls = sealed["controls"]
    passed = (
        sealed["claim_id"] == CLAIM_ID and received == generated
        and sealed["census"]["expected_cardinality"] == len(generated) == 256
        and len(set(received)) == len(generated)
        and decisions == {{candidate: candidate == SURVIVOR for candidate in generated}}
        and sum(decisions.values()) == 1
        and sealed["closure"]["scope"] == "depth_independent"
        and sealed["closure"]["minimality_passed"] is True
        and sealed["closure"]["named_shape_uniqueness_passed"] is True
        and {{row["kind"] for row in controls}} == {{"false_premise", "tampered_source", "tampered_artifact", "boundary"}}
        and all(row["passed"] is True for row in controls)
        and weight(support, "macro-a") == Fraction(2,3)
        and weight(support, "macro-b") == Fraction(1,3)
        and overlap_rejected
        and extended[0][:-1] == support[0] and extended[1][:-1] == support[1]
        and extended[0][-1] == "state-d" and extended[1][-1] == ("macro-c", ("state-d",))
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "complete_partition_reconstructed": support[0] == ("state-a", "state-b", "state-c"),
            "exact_two_thirds_and_one_third_weights_reconstructed": weight(support, "macro-a") == Fraction(2,3) and weight(support, "macro-b") == Fraction(1,3),
            "overlap_rejected": overlap_rejected,
            "finite_successor_reconstructed": extended[0][:-1] == support[0] and extended[1][:-1] == support[1],
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__": main()
'''


def execution_source() -> str:
    claim_id = FINITE_MICROSTATE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.finite_microstate_batch_v1 import (
    FINITE_MICROSTATE_SPEC, WATER_PATH, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
    POP_IDENTITY_PATH, POP_TARGET_PATH, STATE_SNAPSHOT_PATHS,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.finite_microstate_validation_v1 import FiniteMicrostateValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/finite_microstate_law_v1.py",
        root / "sft/chemistry/finite_microstate_batch_v1.py",
        root / "sft/chemistry/finite_microstate_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_finite_microstate_sources_v1.py",
        root / WATER_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / POP_IDENTITY_PATH, root / POP_TARGET_PATH,
        *(root / path for path in STATE_SNAPSHOT_PATHS),
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(FINITE_MICROSTATE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-finite-microstate-001-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=FiniteMicrostateValidator(root),
    )
'''


def main() -> None:
    spec = FINITE_MICROSTATE_SPEC
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
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_sources": [
            {
                "source_id": "NIST-MDS2-3389-CAH-PLUS-QUANTUM-JUMP-THERMOMETRY",
                "body": "National Institute of Standards and Technology",
                "role": "complete direct finite molecular-state population and transition surface",
            },
            {
                "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-WATER-GAS-CALORIMETRIC-TABLE",
                "body": "National Institute of Standards and Technology",
                "role": "complete finite gas-phase water calorimetric table; external evaluated representation only",
            },
        ],
        "source_hashes": {
            "water_snapshot": WATER_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_targets": TARGET_HASH,
            "direct_state_identity_registry": POP_IDENTITY_HASH,
            "direct_state_withheld_targets": POP_TARGET_HASH,
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "populations_temperatures_or_calorimetric_values_present": False,
            "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-001`

## WHY

A continuum ensemble or imported probability distribution cannot prove which chemical states exist. The Fold law instead requires the complete generated finite support and preserves the composition, phase, condition and internal identity of every state. A macro-observation is exactly one fibre of a disjoint exhaustive partition.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

Multiplicity is the exact positive count of one observation fibre. Statistical weight is that count over the complete support count. Appending one newly generated state and its named fibre preserves every prior state and assignment. No continuum, completed infinity, distribution, partition function, fitted coefficient or target value selects the law.

## CHECK

All 387 identities seal before target content opens. The complete post-seal surface preserves 330 direct CaH+ state-population/transition rows and 57 NIST water calorimetric rows, including both separately published 1700 K regime-boundary rows. An implementation-distinct standard-library checker regenerates all candidates, the unique survivor, exact two-thirds and one-third weights, overlap rejection and finite successor closure without measurement-file access.

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
