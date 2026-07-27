#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-016."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.molecular_diffusion_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, MOLECULAR_DIFFUSION_SPEC, PRIMARY_HASH, SOURCE_FILES, SPEC_HASH, TARGET_HASH,
)
from sft.chemistry.molecular_diffusion_validation_v1 import experiment_registration_record, prediction_program_document  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    spec = MOLECULAR_DIFFUSION_SPEC
    package = ROOT / "claims" / spec.claim_id
    registration = {
        "$schema": "../../governance/claim.schema.json", "claim_id": spec.claim_id, "title": spec.title,
        "branch": "chemistry", "status": "registered", "statement": spec.statement,
        "dependencies": list(spec.dependencies), "provenance_classes": ["forward_forcing"],
        "candidate_grammar": {
            "generator": spec.generation_rule, "boundary": spec.grammar_boundary, "expected_cardinality": 256,
            "completeness_certificate": sha256_identity(completeness_record(spec)),
        },
        "excluded_inputs": list(spec.exclusions),
        "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
        "empirical_protocol": "experiments/chemistry/" + spec.experiment_id + "/registration.json",
        "intended_certificate": "Complete 256-form census, one survivor, independent deterministic adjacency/conservation/resource reconstruction, depth-independent successor and complete post-seal 164-record NIST diffusion vector.",
        "registered_by": "Maria Smith", "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json", **experiment_registration_record(ROOT),
        "evidence_mode": "forward_forcing",
        "external_measurement_sources": [
            {"source_id": "NIST-TRC-THERMOML-JCED-2011-56-4840-4848", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 113-row aqueous binary-diffusion surface"},
            {"source_id": "NIST-TRC-THERMOML-FPE-2017-437-34-42", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete self/tracer source: 4 self and 22 tracer rows; every companion dataset retained"},
            {"source_id": "NIST-TRC-THERMOML-FPE-2008-271-43-52", "measurement_body": "National Institute of Standards and Technology ThermoML Archive", "role": "complete 25-row ionic-liquid binary-diffusion surface; density/conductivity companions retained"},
        ],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH, "normalized_primary_records": PRIMARY_HASH,
            "identity_registry": IDENTITY_HASH, "withheld_measurements": TARGET_HASH,
            "complete_raw_and_landing_sources": dict(SOURCE_FILES),
        },
        "prediction_protocol": {"program_hash": sha256_identity(prediction_program_document(ROOT)), "measured_values_present": False, "target_content_inaccessible": True, "complete_trace_required": True},
        "registered_by": "Maria Smith", "registration_date": "2026-07-26", "status": "registered",
    }
    write_json(package / "registration.json", registration)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-016`

## WHY

Molecular diffusion cannot begin with a Fick equation, Brownian continuum, random-walk probability, Stokes-Einstein relation, fitted activation term or transport coefficient. The Fold-native carrier is a counted transition of a retained molecular identity between adjacent generated cells, inside a complete constituent, phase, condition, time and space record. Apparent uncertainty or ensemble dispersion does not install ontological randomness in a superdeterministic process; it records distinctions closed by observation.

## DERIVATION

The complete eight-axis grammar generates 256 forms. Exactly one preserves the molecular carrier, component identities, adjacency, complete constituent conservation, exact resources, unsigned positive magnitude boundary, value-free target identities and depth-independent successor:

`{survivor_id(spec)}`

Binary, self and tracer diffusion are three retained observation classes of the same adjacent-transition relation. Opposed cell directions are held labels, never signed displacements. Counted transitions divided by counted ticks form exact positive internal support. Common transition/tick replication preserves that support; finite record append preserves every earlier identity and condition.

## CHECK

All 164 target identities seal before species, medium, phase, composition, temperature, pressure, method, coefficient, uncertainty or target hashes open. After sealing, all 138 binary, four self and 22 tracer rows open from three complete NIST ThermoML sources. Every one of 30 source datasets and 373 source points remains byte-preserved; non-diffusion companion datasets remain explicit provenance and never become diffusion measurements. Twenty-six external absent condition glyphs translate to structural `EmptyOne`.

The NIST source-declared unit labels and literal value inscriptions are preserved exactly, including any source-level scale presentation; no post-hoc scale correction is invented. An implementation-distinct checker regenerates all 256 candidates, the unique survivor, three diffusion classes, adjacency, held direction, exact resource density, constituent conservation, deterministic replication and adverse controls without target access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The adjacent-transition, conservation and common-replication relations are depth-independent. The empirical result is finite-complete for the three byte-sealed sources. It does not infer unmeasured molecular systems by interpolation or import a continuum transport equation.
""", encoding="utf-8")
    (package / "STATUS.md").write_text(f"# {spec.claim_id}\n\nStatus: `registered_forward_forcing`\n", encoding="utf-8")
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
