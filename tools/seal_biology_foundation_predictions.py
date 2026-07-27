#!/usr/bin/env python3
"""Seal every foundational Biology derivation before source selection."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.biology.derivation import BIOLOGY_BLUEPRINTS, candidate_forms  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


DESTINATION = ROOT / "experiments/sealed_predictions/biology_foundation_complete_pre_source.json"


def main() -> None:
    prediction_set = tuple((row.claim_id, row.exact_result, row.predicted_observation_label) for row in BIOLOGY_BLUEPRINTS)
    payload = {
        "schema": "sft-v3-target-blind-derivation-seal/1",
        "batch": "complete_biology_foundation",
        "branch": "biology",
        "sealed_date": "2026-07-27",
        "external_source_identities_selected": False,
        "external_target_content_opened": False,
        "inventory_path": "sft/biology/obligations.py",
        "inventory_hash": hash_file(ROOT / "sft/biology/obligations.py"),
        "structural_counts_path": "sft/biology/structural_counts.py",
        "structural_counts_hash": hash_file(ROOT / "sft/biology/structural_counts.py"),
        "derivation_path": "sft/biology/derivation.py",
        "derivation_hash": hash_file(ROOT / "sft/biology/derivation.py"),
        "required_claim_count": len(BIOLOGY_BLUEPRINTS),
        "candidate_count": sum(len(candidate_forms(row)) for row in BIOLOGY_BLUEPRINTS),
        "claim_prediction_set_hash": sha256_identity(prediction_set),
    }
    payload["sealed_payload_hash"] = sha256_identity(payload)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"sealed Biology foundation: claims={len(BIOLOGY_BLUEPRINTS)} candidates={payload['candidate_count']}")
    print(payload["sealed_payload_hash"])


if __name__ == "__main__":
    main()
