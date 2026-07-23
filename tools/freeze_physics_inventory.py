"""Materialize the frozen Physics obligation inventory without admitting claims."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.physics.obligations import OBLIGATIONS, SUBBRANCH_ORDER  # noqa: E402


def main() -> None:
    external_path = ROOT / "experiments/external_sources/physics/authoritative_sources.json"
    external = json.loads(external_path.read_text(encoding="utf-8"))
    external_ids = {row["source_id"] for row in external["sources"]}
    missing = sorted({source for row in OBLIGATIONS for source in row.external_source_ids} - external_ids)
    if missing:
        raise SystemExit("unregistered Physics external sources: " + ", ".join(missing))
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    obligation_rows = []
    for position, row in enumerate(OBLIGATIONS, 1):
        values = asdict(row)
        values["position"] = position
        values["status"] = "model_admitted" if row.claim_id in admitted else "registered_not_admitted"
        obligation_rows.append(values)
    counts = Counter(row.subbranch for row in OBLIGATIONS)
    payload = {
        "schema": "sft-v3-physics-branch-inventory/1",
        "branch_id": "physics",
        "inventory_frozen": True,
        "inventory_date": "2026-07-23",
        "scope": "Categorical reconstruction of measurement and metrology; mechanics; interactions and fields; waves; thermodynamics and statistical physics; quantum physical correspondence; matter, particles and nuclei; spacetime and gravitation; fluids, plasmas and condensed collective matter; and only the physical relations required at the later Astronomy/Cosmology boundary.",
        "exclusions": [
            "astronomical object census and cosmological history belong to the later Astronomy/Cosmology branch",
            "chemical species and materials-property reconstruction belong to Chemistry and Materials",
            "Protein, Chess, Go and Unison application experiments remain excluded",
            "engineering implementations do not select physical laws",
            "conventional equations, constants and measurements may test only after a Fold relation is sealed"
        ],
        "subbranch_order": list(SUBBRANCH_ORDER),
        "subbranch_counts": {key: counts[key] for key in SUBBRANCH_ORDER},
        "required_claim_count": len(OBLIGATIONS),
        "required_claim_ids": [row.claim_id for row in OBLIGATIONS],
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in OBLIGATIONS),
        "unclassified_obligations": [],
        "external_source_registry_path": "experiments/external_sources/physics/authoritative_sources.json",
        "external_source_registry_hash": sha256_identity(external),
        "obligations": obligation_rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    destination = ROOT / "publications/inventories/physics.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"frozen Physics inventory: {len(OBLIGATIONS)} obligations; {payload['admitted_claim_count_at_freeze']} admitted")


if __name__ == "__main__":
    main()
