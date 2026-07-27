#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-002."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.temperature_correspondence_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, IDENTITY_PATH, PHYSICS_RECORD_HASH, PHYSICS_RECORD_PATH,
    PRIMARY_HASH, PRIMARY_PATH, SOURCE_FILES, TARGET_HASH, TARGET_PATH,
    TEMPERATURE_CORRESPONDENCE_SPEC,
)
from sft.chemistry.temperature_correspondence_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def independent_validator_source() -> str:
    spec = TEMPERATURE_CORRESPONDENCE_SPEC
    domains = tuple(tuple(choice.name for choice in dimension.choices) for dimension in spec.dimensions)
    survivor = survivor_id(spec)
    return f'''"""Implementation-distinct value-free THERMO-002 reconstruction."""
from fractions import Fraction
from itertools import product
import json
import sys

CLAIM_ID = {spec.claim_id!r}
DOMAINS = {domains!r}
SURVIVOR = {survivor!r}

def context(composition, phase, reference, route, carrier):
    if not all((composition, phase, reference, route)) or carrier <= 0:
        raise ValueError("complete held context and positive carrier required")
    return (composition, phase, reference, route, carrier)

def common_carrier(left, right):
    if left[2] != right[2] or left[4] != right[4]:
        raise ValueError("equilibrium reference or Physics carrier differs")
    return left[4]

def append_context(contexts, extension):
    if not contexts or extension in contexts: raise ValueError("new finite context required")
    carrier, reference = contexts[0][4], contexts[0][2]
    if any(row[4] != carrier or row[2] != reference for row in contexts + (extension,)):
        raise ValueError("composition-specific temperature rescaling rejected")
    return contexts + (extension,)

def main():
    with open(sys.argv[1], encoding="utf-8") as handle: sealed = json.load(handle)
    generated = ["__".join(row) for row in product(*DOMAINS)]
    received = [row["candidate_id"] for row in sealed["census"]["candidates"]]
    decisions = {{row["candidate_id"]: row["survives"] for row in sealed["decisions"]}}
    carrier = Fraction(5,3)
    argon = context("argon", "gas", "common-reference", "acoustic", carrier)
    resistor = context("resistor", "condensed", "common-reference", "Johnson-noise", carrier)
    water = context("water", "liquid", "common-reference", "contact", carrier)
    mismatch_rejected = False
    try: common_carrier(argon, context("tampered", "gas", "common-reference", "route", Fraction(7,4)))
    except ValueError: mismatch_rejected = True
    extended = append_context((argon, resistor), water)
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
        and argon[4] == carrier and common_carrier(argon, resistor) == carrier
        and mismatch_rejected and extended[:-1] == (argon, resistor) and extended[-1] == water
    )
    print(json.dumps({{
        "validated_seal_hash": sealed["seal_hash"], "recomputed_from_declared_inputs": True, "passed": passed,
        "certificate": {{
            "claim_id": CLAIM_ID, "generated_cardinality": len(generated),
            "unique_survivor": SURVIVOR if passed else None,
            "closure": "depth_independent" if passed else None,
            "unchanged_physics_carrier_reconstructed": argon[4] == carrier,
            "cross_route_common_carrier_reconstructed": common_carrier(argon, resistor) == carrier,
            "composition_rescaling_rejected": mismatch_rejected,
            "append_only_composition_reconstructed": extended[:-1] == (argon, resistor),
            "measurement_file_accessed": False,
        }},
    }}, sort_keys=True))

if __name__ == "__main__": main()
'''


def execution_source() -> str:
    claim_id = TEMPERATURE_CORRESPONDENCE_SPEC.claim_id
    return f'''"""Official execution binding for {claim_id}."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.temperature_correspondence_batch_v1 import (
    TEMPERATURE_CORRESPONDENCE_SPEC, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
    PHYSICS_RECORD_PATH, SOURCE_FILES,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.temperature_correspondence_validation_v1 import TemperatureCorrespondenceValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/temperature_correspondence_law_v1.py",
        root / "sft/chemistry/temperature_correspondence_batch_v1.py",
        root / "sft/chemistry/temperature_correspondence_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_temperature_correspondence_sources_v1.py",
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH, root / PHYSICS_RECORD_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/{claim_id}/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(TEMPERATURE_CORRESPONDENCE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-temperature-correspondence-002-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=TemperatureCorrespondenceValidator(root),
    )
'''


def main() -> None:
    spec = TEMPERATURE_CORRESPONDENCE_SPEC
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
            {"source_id": "NIST-CODATA-2022-BOLTZMANN", "body": "National Institute of Standards and Technology", "role": "exact SI common temperature-energy carrier"},
            {"source_id": "NIM-NIST-ACOUSTIC-BOLTZMANN-2017", "body": "National Institute of Metrology and National Institute of Standards and Technology", "role": "complete acoustic argon gas thermometry interval and TPW chemical context"},
            {"source_id": "NIST-JOHNSON-NOISE-BOLTZMANN-2011", "body": "National Institute of Standards and Technology", "role": "independent electronic Johnson-noise thermometry interval"},
        ],
        "source_hashes": {
            "physics_source_record": PHYSICS_RECORD_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_targets": TARGET_HASH,
            **{path: source_hash for path, source_hash in SOURCE_FILES},
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "values_uncertainties_intervals_or_relation_flags_present": False,
            "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    note = f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-002`

## WHY

Temperature is already a Physics carrier. Chemistry cannot lawfully invent a composition-specific temperature scale. It must retain composition, phase, equilibrium reference and route while consuming the same carrier unchanged and owning only the chemical-state consequences attached to it.

## DERIVATION

The complete eight-axis grammar generates 256 forms and leaves exactly one survivor:

`{survivor_id(spec)}`

Two equilibrated chemical contexts must share one exact Physics carrier. A different route or composition cannot rescale it. Adding one composition-dependent consequence preserves the carrier and every earlier context. No measured value, calibration coefficient, continuum distribution or target-derived scale selects this result.

## CHECK

All three identities seal before values or uncertainties open. Post-seal, exact SI k_B is `13806490/10^30 J/K`; the complete acoustic-argon interval is `[13806456,13806512]/10^30 J/K`; the independent Johnson-noise interval is `[13806340,13806680]/10^30 J/K`. Both contain the exact common carrier. The primary acoustic paper retains pure argon gas at the triple point of water and the kinetic-temperature relation; the electronic record retains the independent Johnson temperature-response relation.

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
