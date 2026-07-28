#!/usr/bin/env python3
"""Seal all Earth foundation derivations before external-source selection."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.earth_environment.generated_law import EARTH_BLUEPRINTS  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


PATHS = (
    "publications/inventories/earth_environment.json",
    "sft/earth_environment/obligations.py",
    "sft/earth_environment/structural_model.py",
    "sft/earth_environment/generated_law.py",
    "audits/earth_environment_v1_v2_initial_atomic_ownership.json",
)


def main() -> None:
    inventory = json.loads((ROOT / PATHS[0]).read_text(encoding="utf-8"))
    prediction_set = tuple((row.claim_id, row.exact_result, row.predicted_observation_label, row.falsification_condition) for row in EARTH_BLUEPRINTS)
    payload = {
        "schema": "sft-v3-earth-environment-complete-pre-source-seal/1",
        "seal_date": "2026-07-28",
        "required_claim_count": len(EARTH_BLUEPRINTS),
        "candidate_count": len(EARTH_BLUEPRINTS) * 256,
        "inventory_hash": inventory["inventory_hash"],
        "claim_prediction_set_hash": sha256_identity(prediction_set),
        "sealed_files": {path: hash_file(ROOT / path) for path in PATHS},
        "external_source_identities_selected": False,
        "external_source_content_opened": False,
        "external_outcomes_opened": False,
        "prior_answers_present_in_derivation_runtime": False,
        "conventional_earth_models_present_in_derivation_runtime": False,
        "dimensional_observations_used_to_select_law": False,
        "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
    }
    payload["complete_branch_pre_source_seal_hash"] = sha256_identity(payload)
    path = ROOT / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "complete_foundation_derivations_sealed_before_external_sources",
        "pre_source_seal_path": str(path.relative_to(ROOT)),
        "pre_source_seal_hash": payload["complete_branch_pre_source_seal_hash"],
        "next_exact_operation": "preregister_authoritative_external_source_identities_for_all_earth_families",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sealed {len(EARTH_BLUEPRINTS)} Earth predictions before source selection: {payload['complete_branch_pre_source_seal_hash']}")


if __name__ == "__main__":
    main()
