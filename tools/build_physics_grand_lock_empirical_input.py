#!/usr/bin/env python3
"""Build the post-formal-seal Physics empirical reconciliation vector."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMAL_ID = "SFT-PHYS-GRAND-LOCK-TERMINAL-075"
FORMAL_HASH = "sha256:ae18f67371c8e7054430935d6b5e5f3162f24cf9cba073769384bf7ba467d817"
SOURCE = ROOT / "experiments/external_sources/physics/snapshots/physics-grand-lock-empirical-reconciliation-record.json"


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    frozen_path = ROOT / "census/physics_grand_lock_input_v1.json"
    frozen = load(frozen_path)
    census = {row["claim_id"]: row for row in load(ROOT / "census/claims.json")["claims"]}
    if FORMAL_ID not in census or census[FORMAL_ID]["receipt_hash"] != FORMAL_HASH:
        raise SystemExit("formal Grand Lock receipt is absent or changed")
    formal_receipt = ROOT / census[FORMAL_ID]["receipt_path"]
    if load(formal_receipt).get("receipt_hash") != FORMAL_HASH:
        raise SystemExit("formal Grand Lock receipt identity mismatch")

    empirical = tuple(row for row in frozen["physics_claims"] if row["empirical"])
    if len(empirical) != frozen["empirical_claim_count"]:
        raise SystemExit("empirical vector count changed")
    legacy = tuple(row["claim_id"] for row in empirical if not row.get("measurement_receipt_hash"))
    source_ids = tuple(sorted({
        source_id
        for row in empirical
        for source_id in row.get("external_data_source_ids", ())
    }))
    payload = {
        "schema": "sft-v3-physics-grand-lock-empirical-reconciliation/1",
        "formal_grand_lock": {
            "claim_id": FORMAL_ID,
            "receipt_hash": FORMAL_HASH,
            "receipt_path": census[FORMAL_ID]["receipt_path"],
            "receipt_file_sha256": sha256(formal_receipt),
        },
        "prelock_input_path": frozen_path.relative_to(ROOT).as_posix(),
        "prelock_input_sha256": sha256(frozen_path),
        "physics_claim_count": frozen["physics_claim_count"],
        "physics_claim_ids": frozen["physics_claim_ids"],
        "empirical_claim_count": len(empirical),
        "unique_external_source_id_count": len(source_ids),
        "unique_external_source_ids": source_ids,
        "unfavorable_or_scope_boundary_ids": frozen["unfavorable_or_scope_boundary_ids"],
        "legacy_empirical_materialization_without_separate_measurement_receipt": legacy,
        "empirical_claims": empirical,
        "methodological_boundary": {
            "observation_is_empirical_evidence": True,
            "formal_survivor_sealed_before_this_aggregate_reconciliation": True,
            "prior_observations_not_relabelled_as_unseen_predictions": True,
            "every_empirical_validation_hash_retained": True,
            "every_external_validation_hash_retained": True,
            "every_available_measurement_receipt_hash_retained": True,
            "legacy_receipt_shape_explicit": True,
            "every_unfavorable_result_and_scope_boundary_retained": True,
            "measurements_select_formal_survivor": False,
            "current_evidence_closed_lawful_extensions_open": True,
        },
    }
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    SOURCE.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "sha256": sha256(SOURCE),
        "empirical_claims": len(empirical),
        "external_source_ids": len(source_ids),
        "retained_adverse_or_scope_boundaries": len(frozen["unfavorable_or_scope_boundary_ids"]),
        "legacy_receipt_shapes": len(legacy),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
