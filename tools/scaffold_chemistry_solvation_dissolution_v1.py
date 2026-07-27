#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-015."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.solvation_dissolution_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, PRIMARY_HASH, SOLVATION_DISSOLUTION_SPEC, SOURCE_FILES, SPEC_HASH, TARGET_HASH,
)
from sft.chemistry.solvation_dissolution_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    spec = SOLVATION_DISSOLUTION_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent state/order/capacity reconstruction, depth-independent successor and complete post-seal 799-record FreeSolv/NIST vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [
            {
                "source_id": "FREESOLV-0.52-COMMIT-6C7D19B",
                "measurement_body": "MobleyLab FreeSolv curated experimental hydration free-energy database",
                "role": "complete 642-row experimental hydration free-energy and uncertainty surface; calculated companions preserved but excluded",
            },
            {
                "source_id": "NIST-TRC-THERMOML-JCED-2016-61-1470-1476",
                "measurement_body": "National Institute of Standards and Technology ThermoML Archive",
                "role": "complete seven-dataset 157-row direct binary and mixed-solvent solubility surface",
            },
        ],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)), "measured_values_present": False,
            "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    write_json(package / "registration.json", registration)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-015`

## WHY

Solvation and dissolution cannot begin with a force field, continuum-solvent model, partition/activity fit, solubility-product equation, logarithm or correlation. The Fold-native carrier must retain the solute, every solvent, the distinct source and destination states, and the exact condition. Direction must be held as a state relation rather than represented by a negative SFT number.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the complete carrier, distinct component and state identities, exact condition, unsigned held order, structural absence, value-free identities and depth-independent successor:

`{survivor_id(spec)}`

An external signed free-energy inscription is translated only after sealing: its sign becomes a held source/destination orientation and its magnitude becomes an exact positive fraction. An exact external zero glyph becomes structural `EmptyOne` and coincident support. Solubility is an exact positive, condition-bound composition capacity. Complete record append and common support replication preserve the relation without refitting.

## CHECK

All 799 row identities seal before compound, solvent, state, condition, measurement, uncertainty, reference or target hashes open. After sealing, every one of 642 FreeSolv experimental records and every one of 157 direct NIST ThermoML solubility records opens. Both favorable and opposed solvation orientations, two coincident/`EmptyOne` rows, all seven dissolution datasets, all 93 mixed-solvent records and all ten absent solvent-composition coordinates are retained. Calculated FreeSolv and correlated paper companions remain in provenance but never become measurements.

An implementation-distinct checker regenerates all 256 candidates, the unique survivor, held orientations, exact positive magnitude/capacity, structural absence, replication invariance and all adverse controls without measurement-file access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The carrier, held-order and finite-successor relations are depth-independent. The empirical result is finite-complete for the two byte-sealed complete sources. Initial source-family research is disclosed; the executable candidate and prediction package remained value-inaccessible. No unmeasured solvent system is inferred by interpolation.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
