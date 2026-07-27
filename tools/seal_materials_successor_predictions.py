#!/usr/bin/env python3
"""Seal all eight target-blind Materials successor predictions at once."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file
from sft.materials.successor_derivation import MATERIALS_SUCCESSOR_BLUEPRINTS, successor_candidate_ids


OUT = ROOT / "experiments/sealed_predictions/materials_v1_v2_successor_complete_pre_source.json"
SOURCE_PATHS = (
    "sft/materials/successor_obligations.py",
    "sft/materials/successor_structural_counts.py",
    "sft/materials/successor_derivation.py",
)


def main() -> None:
    prediction_set = tuple(
        (row.claim_id, row.exact_result, row.predicted_observation_label)
        for row in MATERIALS_SUCCESSOR_BLUEPRINTS
    )
    payload = {
        "schema": "sft.materials.complete-successor-pre-source-seal.v1",
        "purpose": "Freeze the complete eight-claim Materials V1/V2 reconciliation surface before selecting or opening any new external target.",
        "external_source_identities_selected": False,
        "external_target_content_opened": False,
        "required_claim_count": len(MATERIALS_SUCCESSOR_BLUEPRINTS),
        "candidate_count": sum(len(successor_candidate_ids(row)) for row in MATERIALS_SUCCESSOR_BLUEPRINTS),
        "claim_ids": [row.claim_id for row in MATERIALS_SUCCESSOR_BLUEPRINTS],
        "claim_prediction_set_hash": sha256_identity(prediction_set),
        "source_files": {path: hash_file(ROOT / path) for path in SOURCE_PATHS},
        "root_theorem": "SFT-ROOT-THERE-IS-NO-NOTHING",
        "axioms": [],
        "free_parameters": [],
        "proof_value_boundary": "positive exact whole/part forms and held categorical absence/orientation only",
    }
    payload["sealed_payload_hash"] = sha256_identity(payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(payload["sealed_payload_hash"])


if __name__ == "__main__":
    main()
