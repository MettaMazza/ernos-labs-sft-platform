#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-019."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.chemistry.coupled_transport_batch_v1 import COUPLED_TRANSPORT_SPEC, IDENTITY_HASH, PRIMARY_HASH, SOURCE_FILES, SPEC_HASH, TARGET_HASH  # noqa: E402
from sft.chemistry.coupled_transport_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    spec = COUPLED_TRANSPORT_SPEC; package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry",
        "status": "registered", "statement": spec.statement, "dependencies": list(spec.dependencies), "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent mass/heat/charge triad and pairwise-projection reconstruction, depth-independent successor and complete post-seal 232-record NIST coupled vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    })
    experiment = {"$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT), "evidence_mode": "forward_forcing",
        "external_measurement_sources": [
            {"source_id": "NIST-TRC-THERMOML-JCED-2015-60-3621-3630", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete thermally forced binary-diffusion mass-heat surface"},
            {"source_id": "NIST-TRC-THERMOML-JCED-2006-51-680-685", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete electrical-conductivity/tracer-diffusion mass-charge surface"},
            {"source_id": "NIST-TRC-THERMOML-JCED-2014-59-757-763", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete thermal/electrical-conductivity heat-charge surface"},
        ],
        "source_hashes": {"prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH, "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH, "complete_raw_and_landing_sources": dict(SOURCE_FILES)},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered"}
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-019`

## WHY

Coupled transport cannot begin with an Onsager matrix, continuum gradients and fluxes, phenomenological cross coefficients or fitted relations. Physics supplies mass, energy and charge carriers. Chemistry must retain component, phase and condition while asking when distinct carrier packets occupy the same generated transition event.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the complete mass/heat/charge triad, all three pairwise projections, counted shared adjacent transition, held per-carrier directions, exact resources, post-seal pairwise responses, value-free identities and depth-independent successor:

`{survivor_id(spec)}`

Coupling is therefore shared transition provenance, not a fitted coefficient. Each mass, heat and charge packet remains distinct; all occupy one exact event ledger. Opposed directions are held labels, never signed magnitudes. Common event/tick replication preserves every exact response and every pairwise projection without refitting.

## CHECK

All 232 identities seal before substance, carrier-pair property, composition, phase, condition, method, response, uncertainty or target hashes open. After sealing, three complete NIST ThermoML sources open: 22 thermally forced mass-diffusion records, 146 mass-charge records and 64 heat-charge records. The surface contains 137 binary and 95 ternary rows, four response-property families and five methods. All 23 source datasets and 375 source points remain preserved; every companion property remains explicit provenance and never becomes a coupled measurement. Six external absence glyphs translate to structural `EmptyOne`.

The NIST source inscriptions and source-declared units are preserved literally. No unregistered exponent or scale correction is introduced for tracer-diffusion inscriptions.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The shared-event triad and common-replication law are depth-independent. The empirical result is finite-complete for the three byte-sealed pairwise sources; it does not claim an imported reciprocal matrix or infer unmeasured cross coefficients.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_forward_forcing`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__": main()
