#!/usr/bin/env python3
"""Create the registered claim and experiment package for Chemistry THERMO-013."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.multicomponent_phase_diagram_batch_v1 import (  # noqa: E402
    IDENTITY_HASH, LANDING_HASH, MULTICOMPONENT_PHASE_DIAGRAM_SPEC, PRIMARY_HASH, RAW_HASH,
    SPEC_HASH, TARGET_HASH,
)
from sft.chemistry.multicomponent_phase_diagram_validation_v1 import (  # noqa: E402
    experiment_registration_record, prediction_program_document,
)
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.generated_empirical_law import completeness_record, survivor_id  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    spec = MULTICOMPONENT_PHASE_DIAGRAM_SPEC
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
        "intended_certificate": "Complete 256-form census, one survivor, independent exact-composition/exchange/rank reconstruction, depth-independent append/replication proof and complete post-seal 116-record NIST vector.",
        "registered_by": "Maria Smith",
        "registration_date": "2026-07-26",
    }
    experiment = {
        "$schema": "../../../governance/experiment.schema.json",
        **experiment_registration_record(ROOT),
        "evidence_mode": "observational_derivation",
        "external_measurement_sources": [{
            "source_id": "NIST-TRC-THERMOML-JCT-2012-47-260-266",
            "measurement_body": "National Institute of Standards and Technology ThermoML Archive",
            "role": "complete five-pair binary and complete ternary liquid-gas coexistence surface with companion records",
        }],
        "source_hashes": {
            "prefetch_value_free_specification": SPEC_HASH,
            "complete_raw_thermoml_source": RAW_HASH,
            "source_landing_record": LANDING_HASH,
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
    write_json(package / "registration.json", registration)
    write_json(ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json", experiment)
    (package / "WHY_DERIVATION_CHECK.md").write_text(
        f"""# {spec.title}

Claim: `{spec.claim_id}`  
Chemistry obligation: `SFT-CHEM-OBL-THERMO-013`

## WHY

A multicomponent phase diagram cannot begin as an assumed continuum plane, fitted equation of state, lever rule, tie-line formula, Gibbs triangle or convex-hull construction. The Fold-native object is the exact finite word of measured coexistence records. Each phase is a complete ordered component-coordinate word closing exactly to the One; the two held phases retain the same components while componentwise exchange supports balance.

## DERIVATION

The complete eight-axis grammar generates 256 named forms. Exactly one preserves the complete two-phase carrier, exact phase composition, distinct phase words, componentwise exchange balance, finite phase-rule rank, structural absence, value-free identity boundary and depth-independent successor:

`{survivor_id(spec)}`

For two coexisting phases, the admitted phase-rule cancellation leaves a carrier word whose length is exactly the number of components. A source `0` inscription is retained in provenance but becomes structural `EmptyOne`; it is never consumed as an SFT number. Appending a complete point and commonly replicating paired exchange support preserve the law without redrawing or refitting.

## CHECK

Before compounds, phases, temperatures, pressures, compositions, uncertainties or target hashes open, all 116 source identities are sealed. After sealing, the complete NIST vector opens: five binary dataset pairs containing 65 coexistence records, the complete 51-record ternary surface, 566 exact liquid/gas composition coordinates, all 12 structural-absence boundaries, all six companion pure-component datasets, and the complete 17-dataset 187-point source. An implementation-distinct checker regenerates all 256 candidates, exact binary and ternary normalization, componentwise exchange balance, phase ranks, append/replication invariance and all adverse controls without measurement access.

## FALSIFICATION

{spec.falsification_condition}

## BOUNDARY

The exact phase-word, exchange-balance, phase-rank and finite append/replication laws are depth-independent. The empirical result is finite-complete for the byte-sealed NIST source. It does not interpolate unmeasured points or install an equation for an ungenerated system.
""",
        encoding="utf-8",
    )
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `registered_observational_derivation`\n",
        encoding="utf-8",
    )
    print("scaffolded", spec.claim_id)


if __name__ == "__main__":
    main()
