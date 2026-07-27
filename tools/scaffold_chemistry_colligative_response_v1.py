#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-014."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.colligative_response_batch_v1 import (  # noqa: E402
    COLLIGATIVE_RESPONSE_SPEC, IDENTITY_HASH, PRIMARY_HASH, SOURCE_FILES, SPEC_HASH, TARGET_HASH,
)
from sft.chemistry.colligative_response_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    spec = COLLIGATIVE_RESPONSE_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["observational_derivation"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent response-orientation/separation reconstruction, depth-independent replication and complete post-seal 276-record NIST vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [
            {"source_id": "NIST-TRC-THERMOML-FPE-2013-337-60-66", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 16-dataset 144-row direct boiling response surface"},
            {"source_id": "NIST-TRC-THERMOML-FPE-2016-420-14-19", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete six-dataset 37-row direct solid-liquid response surface"},
            {"source_id": "NIST-TRC-THERMOML-JCT-2009-41-1439-1445", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete six-dataset 95-row direct osmotic response surface"},
        ],
        "source_hashes": {"prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH, "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH, "complete_raw_and_landing_sources": dict(SOURCE_FILES)},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    write_json(package / "registration.json", registration)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-014`

## WHY

A colligative response cannot begin with a memorized linear equation, fitted boiling/freezing constant, osmotic equation, van't Hoff factor or dissociation parameter. The Fold-native carrier retains distinct solvent and solute particle identities, exact composition, the boundary that transmits solvent exchange while retaining the solute distinction, and the resulting held response orientation.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the complete particle carrier, distinct identities, exact boundary, unsigned orientation, exact positive response separation, structural pure-solvent absence, value-free identities and depth-independent successor:

`{survivor_id(spec)}`

Solute retention forces three boundary-specific relations: expanded temperature support until liquid-gas balance, reduced temperature support until liquid-crystal balance, and pressure support directed toward the solute-holding solution. These are held orientations, never signed proof magnitudes. A pure-solvent composition is structural `EmptyOne`. Numerical magnitudes enter only after the relation seals and remain exact external fractions.

## CHECK

All 276 source identities seal before compounds or values open. After sealing, all 144 direct boiling rows, 37 direct freezing rows and 95 direct osmotic rows open from three complete NIST ThermoML records—28 datasets and 276 points with every method, phase, uncertainty and source record retained. The sole absent composition coordinate becomes `EmptyOne`. An implementation-distinct checker regenerates all 256 candidates, all three orientations, exact positive separation, replication invariance and adverse controls without measurement access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The particle distinction, response orientation and common-replication laws are depth-independent. The empirical result is finite-complete for the three byte-sealed sources. It does not install a conventional colligative equation or predict an ungenerated system by interpolation.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
