#!/usr/bin/env python3
"""Write the frozen foundational Biology publication inventory."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.biology.derivation import BIOLOGY_BLUEPRINTS  # noqa: E402
from sft.biology.obligations import BIOLOGY_OBLIGATIONS, SUBBRANCH_ORDER  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


def main() -> None:
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    specs = {row.claim_id: row for row in BIOLOGY_BLUEPRINTS}
    rows = []
    for position, obligation in enumerate(BIOLOGY_OBLIGATIONS, 1):
        values = asdict(obligation)
        values["position"] = position
        values["candidate_count"] = 256
        values["unique_survivor"] = specs[obligation.claim_id].exact_result
        values["status"] = "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"
        rows.append(values)
    counts = Counter(row.subbranch for row in BIOLOGY_OBLIGATIONS)
    payload = {
        "schema": "sft-v3-biology-foundation-inventory/1",
        "branch_id": "biology",
        "inventory_frozen": True,
        "inventory_date": "2026-07-27",
        "scope": "Foundational reconstruction of living organization, compartments, metabolism, inheritance, evolution, gene and genome organization, protein structure and function, cell processes, development, organismal physiology, population ecology, and biological evidence boundaries.",
        "exclusions": [
            "molecular identity already owned by Chemistry is cited rather than rederived",
            "clinical intervention and efficacy belong to Medicine and Health Sciences",
            "consciousness and qualia belong to the Consciousness branch",
            "engineering implementation and Fold Protein remain downstream application work",
            "future biological discoveries remain lawful extensions after independent admission",
        ],
        "subbranch_order": list(SUBBRANCH_ORDER),
        "subbranch_counts": {name: counts[name] for name in SUBBRANCH_ORDER},
        "required_claim_count": len(BIOLOGY_OBLIGATIONS),
        "required_claim_ids": [row.claim_id for row in BIOLOGY_OBLIGATIONS],
        "candidate_count": len(BIOLOGY_OBLIGATIONS) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in BIOLOGY_OBLIGATIONS),
        "pre_source_complete_branch_seal": "experiments/sealed_predictions/biology_foundation_complete_pre_source.json",
        "atomic_prior_audit": "audits/biology_v1_v2_atomic_ownership.json",
        "authority_source_count": 0,
        "authority_source_set_hash": None,
        "unclassified_obligations": [],
        "frontier_obligations": [],
        "obligations": rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    destination = ROOT / "publications/inventories/biology.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"frozen Biology foundation inventory: {len(rows)} obligations; {payload['admitted_claim_count_at_freeze']} admitted")


if __name__ == "__main__":
    main()
