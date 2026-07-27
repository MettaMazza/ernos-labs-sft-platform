#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-017."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.chemistry.viscous_transport_batch_v1 import IDENTITY_HASH, PRIMARY_HASH, SOURCE_FILES, SPEC_HASH, TARGET_HASH, VISCOUS_TRANSPORT_SPEC  # noqa: E402
from sft.chemistry.viscous_transport_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    spec = VISCOUS_TRANSPORT_SPEC; package = ROOT / "claims" / spec.claim_id
    write_json(package / "registration.json", {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title, "branch": "chemistry",
        "status": "registered", "statement": spec.statement, "dependencies": list(spec.dependencies), "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {"generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256, "completeness_certificate": sha256_identity(completeness_record(spec))},
        "excluded_inputs": list(spec.exclusions), "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent composition/momentum-exchange reconstruction, depth-independent successor and complete post-seal 425-record NIST viscosity vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    })
    experiment = {"$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT), "evidence_mode": "forward_forcing",
        "external_measurement_sources": [
            {"source_id": "NIST-TRC-THERMOML-FPE-2018-474-6-13", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 50-row ternary viscosity surface"},
            {"source_id": "NIST-TRC-THERMOML-JCED-2005-50-1038-1042", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 159-row pure/binary viscosity surface"},
            {"source_id": "NIST-TRC-THERMOML-FPE-2017-453-13-23", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 216-row three-binary-mixture viscosity surface"},
        ],
        "source_hashes": {"prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH, "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH, "complete_raw_and_landing_sources": dict(SOURCE_FILES)},
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered"}
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-017`

## WHY

Chemical viscosity cannot begin with a Newtonian constitutive equation, continuum velocity gradient, Arrhenius/WLF/VFT form, logarithm or fitted coefficient. Physics supplies the admitted momentum carrier; Chemistry must retain every component, phase and condition while deriving viscosity as counted momentum-packet exchange across adjacent generated layers.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the full composition/momentum carrier, distinct identities, adjacent exchange, held orientation, exact resources, post-seal magnitude, value-free identities and depth-independent successor:

`{survivor_id(spec)}`

Pure, binary and ternary systems are distinct retained carriers of the same exchange relation. Opposed layer directions are held labels, never signed shear. Common exchange/tick replication preserves exact packet-transfer density; complete component, exchange and record append preserves every prior distinction without refitting.

## CHECK

All 425 identities seal before substance, composition, phase, temperature, pressure, method, viscosity, uncertainty or target hashes open. After sealing, all 11 pure, 364 binary and 50 ternary viscosity records open from three complete NIST ThermoML sources. All 17 source datasets and 900 source points remain preserved; density, interfacial-tension and other companions remain explicit provenance and never become viscosity measurements. Thirty-eight external absent condition glyphs translate to structural `EmptyOne`.

An implementation-distinct checker regenerates all candidates, the sole survivor, the three composition carriers, adjacent-layer orientations, exact packet/exchange/tick density, replication invariance and adverse controls without target access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The composition-bound exchange and common-replication relations are depth-independent. The empirical result is finite-complete for the three byte-sealed sources and does not infer unmeasured systems by continuum interpolation.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_forward_forcing`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__": main()
