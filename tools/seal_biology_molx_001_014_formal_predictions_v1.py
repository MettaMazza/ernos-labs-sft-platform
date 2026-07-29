#!/usr/bin/env python3
"""Seal the complete formal MOLX family before external outcome access."""

from __future__ import annotations

from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.biology.molx_001_014_laws_v1 import ORDER, SPECS


OUT = ROOT / "census/biology_molx_001_014_formal_prediction_seal_v1.json"
REGISTRY_ID = "sha256:ae8d5c4e9d47270d7dd795a4ac34e1bc916a712622d90ed6ccfaaa1bd33b5733"


def canonical(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("refusing to overwrite Biology MOLX formal prediction seal")
    registry = json.loads((ROOT / "census/biology_molx_001_014_target_registry_v1.json").read_text())
    if registry["registry_identity"] != REGISTRY_ID or any(
        registry[key] is not False
        for key in ("target_content_present", "measured_value_present", "outcome_present", "survivor_identity_present")
    ):
        raise SystemExit("Biology MOLX target registry is not value-free")
    predictions = []
    for claim_id in ORDER:
        spec = SPECS[claim_id]
        generated = tuple("__".join(row) for row in product(*(tuple(choice.name for choice in axis.choices) for axis in spec.axes)))
        survivor = "__".join(axis.survivor.name for axis in spec.axes)
        if len(generated) != len(set(generated)) or generated.count(survivor) != 1:
            raise SystemExit("MOLX formal candidate enumeration does not contain one survivor")
        predictions.append(
            {
                "claim_id": claim_id,
                "obligation_id": spec.obligation_id,
                "statement": spec.statement,
                "exact_result": spec.exact_result,
                "candidate_count": len(generated),
                "survivor_identity": survivor,
                "survivor_identity_hash": canonical(survivor),
                "dependency_ids": list(spec.dependencies),
                "axioms": [],
                "free_parameters": [],
                "external_outcome_opened": False,
            }
        )
    payload = {
        "schema": "sft-v3-biology-molx-formal-prediction-seal/1",
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "family": "living_biochemistry_and_molecular_processes",
        "target_registry_identity": REGISTRY_ID,
        "law_source_hash": file_hash(ROOT / "sft/biology/molx_001_014_laws_v1.py"),
        "independent_validator_hash": file_hash(ROOT / "generated/biology/molx_001_014_validator_v1.py"),
        "focused_test_hash": file_hash(ROOT / "tests/test_biology_molx_001_014_v1.py"),
        "claim_count": len(predictions),
        "candidate_count_per_claim": 256,
        "total_candidate_count": sum(row["candidate_count"] for row in predictions),
        "unique_survivor_count": len(predictions),
        "external_target_content_opened": False,
        "predictions": predictions,
    }
    payload["formal_prediction_seal_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "claim_count": payload["claim_count"],
                "total_candidate_count": payload["total_candidate_count"],
                "formal_prediction_seal_identity": payload["formal_prediction_seal_identity"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
