#!/usr/bin/env python3
"""Seal the complete Medicine inventory and target-blind prediction set."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.medicine.generated_law import MEDICINE_BLUEPRINTS, candidate_forms, unique_survivor  # noqa: E402


OUTPUT = ROOT / "experiments/sealed_predictions/medicine_foundation_complete_pre_source.json"


def hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    inventory_path = ROOT / "publications/inventories/medicine.json"
    obligations_path = ROOT / "sft/medicine/obligations.py"
    generated_law_path = ROOT / "sft/medicine/generated_law.py"
    structural_counts_path = ROOT / "sft/medicine/structural_counts.py"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    if inventory["required_claim_ids"] != [row.claim_id for row in MEDICINE_BLUEPRINTS]:
        raise RuntimeError("Medicine inventory and generated blueprint order differ")
    predictions = []
    for row in MEDICINE_BLUEPRINTS:
        forms = candidate_forms(row)
        survivor = unique_survivor(row)
        predictions.append({
            "claim_id": row.claim_id,
            "experiment_id": row.experiment_id,
            "candidate_count": len(forms),
            "candidate_census_hash": sha256_identity(forms),
            "unique_survivor": row.exact_result,
            "unique_survivor_hash": sha256_identity(survivor),
            "predicted_observation_label": row.predicted_observation_label,
            "falsification_condition": row.falsification_condition,
        })
    payload = {
        "schema": "sft-v3-medicine-foundation-complete-pre-source-seal/1",
        "branch": "medicine",
        "sealed_before_external_source_identity_selection": True,
        "sealed_before_external_content_access": True,
        "external_source_identities_selected": False,
        "external_outcomes_opened": False,
        "prior_answers_used_as_premises": False,
        "target_values_used_to_select_survivors": False,
        "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "inventory_path": str(inventory_path.relative_to(ROOT)),
        "inventory_file_hash": hash_file(inventory_path),
        "inventory_identity": inventory["inventory_hash"],
        "obligations_path": str(obligations_path.relative_to(ROOT)),
        "obligations_hash": hash_file(obligations_path),
        "generated_law_path": str(generated_law_path.relative_to(ROOT)),
        "generated_law_hash": hash_file(generated_law_path),
        "structural_counts_path": str(structural_counts_path.relative_to(ROOT)),
        "structural_counts_hash": hash_file(structural_counts_path),
        "required_claim_count": len(predictions),
        "candidate_count": sum(row["candidate_count"] for row in predictions),
        "claim_prediction_set_hash": sha256_identity(tuple((row["claim_id"], row["unique_survivor"], row["predicted_observation_label"]) for row in predictions)),
        "predictions": predictions,
    }
    payload["complete_branch_pre_source_seal_hash"] = sha256_identity(payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sealed Medicine foundation before source selection: {payload['required_claim_count']} claims; {payload['candidate_count']} candidates")
    print(payload["complete_branch_pre_source_seal_hash"])


if __name__ == "__main__":
    main()

