#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-018."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.thermal_conductivity_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, PRIMARY_HASH, SOURCE_FILES, SPEC_HASH, TARGET_HASH, THERMAL_CONDUCTIVITY_SPEC,
)
from sft.chemistry.thermal_conductivity_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    spec = THERMAL_CONDUCTIVITY_SPEC
    package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json",
        "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry", "status": "registered",
        "statement": spec.statement, "dependencies": list(spec.dependencies), "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary,
            "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent composition/phase/energy-transfer reconstruction, depth-independent successor and complete post-seal 655-record NIST thermal-conductivity vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    })
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "forward_forcing",
        "external_measurement_sources": [
            {"source_id": "NIST-TRC-THERMOML-JCED-2013-58-663-670", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete pure/binary/ternary liquid thermal-conductivity surface"},
            {"source_id": "NIST-TRC-THERMOML-JCT-2019-133-135-142", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete pure/binary gas-and-liquid thermal-conductivity surface"},
            {"source_id": "NIST-TRC-THERMOML-FPE-2018-477-78-86", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete pure liquid-and-crystalline thermal-conductivity surface"},
        ],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "prediction_protocol": {
            "program_hash": sha256_identity(prediction_program_document(ROOT)),
            "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True,
        },
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-018`

## WHY

Chemical thermal conductivity cannot begin with Fourier's continuum equation, a temperature gradient, a kinetic-theory formula, a fitted mixing or temperature relation, a logarithm or a selected material curve. Physics supplies admitted energy and thermal-order carriers. Chemistry must retain every component, phase and condition while deriving conductivity as counted energy-packet transfer between adjacent generated cells.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the full composition/phase/energy carrier, distinct identities, adjacent transfer, held thermal orientation, exact resources, post-seal magnitude, value-free identities and depth-independent successor:

`{survivor_id(spec)}`

Pure, binary and ternary systems and gas, liquid and crystalline phases remain distinct retained carriers of the same transfer relation. Opposed thermal directions are held labels, never signed flux. Packet-transfer response is the exact positive ratio of energy-packet transfers to ticks, boundary support and thermal-order separation. Common transfer/tick replication preserves that ratio; complete component, phase, condition, transfer and record append preserves every prior distinction without refitting.

## CHECK

All 655 identities seal before substance, composition, phase, temperature, pressure, method, conductivity, uncertainty or target hashes open. After sealing, all 123 pure, 273 binary and 259 ternary records open from three complete NIST ThermoML sources: 51 gas, 571 liquid and 33 crystalline measurements across three methods. All 61 source datasets and all 679 source points remain preserved; non-conductivity companions remain explicit provenance and never become conductivity measurements.

An implementation-distinct checker regenerates all candidates, the sole survivor, the three composition carriers, opposed held thermal orientations, exact packet/transfer/tick/boundary/order response, replication invariance and adverse controls without target access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The composition-bound adjacent transfer and common-replication relations are depth-independent. The empirical result is finite-complete for the three byte-sealed sources and does not infer unmeasured systems through continuum interpolation.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_forward_forcing`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
