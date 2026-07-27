#!/usr/bin/env python3
"""Register Medicine and write its frozen foundational inventory."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.medicine.generated_law import MEDICINE_BLUEPRINTS  # noqa: E402
from sft.medicine.obligations import FAMILY_ORDER, MEDICINE_OBLIGATIONS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def register_branch() -> None:
    path = ROOT / "census/branches.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    rows = doc["branches"]
    if any(row["branch_id"] == "medicine" for row in rows):
        return
    insert_at = next(index for index, row in enumerate(rows) if row["branch_id"] == "consciousness_cognitive_science")
    rows.insert(insert_at, {
        "branch_id": "medicine",
        "inventory_status": "foundation_frozen_0_of_72_registered_not_admitted",
        "paper_status": "not_ready",
    })
    write_json(path, doc)


def main() -> None:
    register_branch()
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    specs = {row.claim_id: row for row in MEDICINE_BLUEPRINTS}
    rows = []
    for position, obligation in enumerate(MEDICINE_OBLIGATIONS, 1):
        values = asdict(obligation)
        values["position"] = position
        values["candidate_count"] = 256
        values["unique_survivor"] = specs[obligation.claim_id].exact_result
        values["status"] = "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"
        rows.append(values)
    counts = Counter(row.family for row in MEDICINE_OBLIGATIONS)
    payload = {
        "schema": "sft-v3-medicine-foundation-inventory/1",
        "branch_id": "medicine",
        "categorical_claim_prefix": "SFT-MED-",
        "inventory_frozen": True,
        "inventory_date": "2026-07-27",
        "scope": "Foundational reconstruction of patient and population health observation, disease and injury boundaries, diagnosis, causal clinical inference, prognosis, intervention, exposure, benefit-harm, study designs, care pathways, individual-population inference, consent, privacy and uncertainty.",
        "exclusions": [
            "living mechanism already owned by Biology is cited rather than rederived",
            "molecular identity and reaction law already owned by Chemistry are cited rather than rederived",
            "device and biomaterial law already owned by Materials is cited rather than rederived",
            "specialty-by-specialty complete-field reconstruction belongs to later Medicine versions",
            "institutional policy is not treated as a biological or clinical law",
            "future medical discoveries remain lawful extensions after independent admission",
        ],
        "family_order": list(FAMILY_ORDER),
        "family_counts": {name: counts[name] for name in FAMILY_ORDER},
        "required_claim_count": len(MEDICINE_OBLIGATIONS),
        "required_claim_ids": [row.claim_id for row in MEDICINE_OBLIGATIONS],
        "candidate_count": len(MEDICINE_OBLIGATIONS) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in MEDICINE_OBLIGATIONS),
        "pre_source_complete_branch_seal": "experiments/sealed_predictions/medicine_foundation_complete_pre_source.json",
        "atomic_prior_audit": "audits/medicine_v1_v2_atomic_ownership.json",
        "authority_source_count": 0,
        "authority_source_set_hash": None,
        "unclassified_obligations": [],
        "frontier_obligations": [],
        "obligations": rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    write_json(ROOT / "publications/inventories/medicine.json", payload)
    print(f"frozen Medicine foundation inventory: {len(rows)} obligations; {payload['candidate_count']} candidates; {payload['admitted_claim_count_at_freeze']} admitted")


if __name__ == "__main__":
    main()

