"""Freeze the complete Materials obligation and admission inventory."""

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
from sft.materials.generated_law import MATERIALS_SPECS, PRE_SOURCE_SEAL_PATH  # noqa: E402
from sft.materials.obligations import MATERIALS_OBLIGATIONS, SUBBRANCH_ORDER  # noqa: E402
from sft.materials.sources import MATERIALS_AUTHORITY_SOURCES, validate_sources  # noqa: E402


def main() -> None:
    validate_sources(ROOT)
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    specs = {row.claim_id: row for row in MATERIALS_SPECS}
    rows = []
    for position, obligation in enumerate(MATERIALS_OBLIGATIONS, 1):
        values = asdict(obligation)
        values["position"] = position
        values["candidate_count"] = 256
        values["unique_survivor"] = specs[obligation.claim_id].exact_result
        values["status"] = (
            "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"
        )
        rows.append(values)
    counts = Counter(row.subbranch for row in MATERIALS_OBLIGATIONS)
    payload = {
        "schema": "sft-v3-materials-branch-inventory/1",
        "branch_id": "materials",
        "inventory_frozen": True,
        "inventory_date": "2026-07-24",
        "scope": "Complete Materials reconstruction through identity and traceability; crystals and quasicrystals; defects and microstructure; electronic and semiconductor organization; superconducting, superfluid and topological material response; mechanical, thermal, magnetic and optical response; bulk material classes; processing and degradation; and advanced functional and lifecycle organization.",
        "exclusions": [
            "specimen- and method-dependent magnitudes are conditional records, not universal constants",
            "biological function beyond the material interface belongs to Biology",
            "clinical outcomes belong to Medicine and Health Sciences",
            "industrial application performance cannot select a Materials law",
            "unregistered materials and future observations remain new empirical targets",
        ],
        "subbranch_order": list(SUBBRANCH_ORDER),
        "subbranch_counts": {name: counts[name] for name in SUBBRANCH_ORDER},
        "required_claim_count": len(MATERIALS_OBLIGATIONS),
        "required_claim_ids": [row.claim_id for row in MATERIALS_OBLIGATIONS],
        "candidate_count": len(MATERIALS_OBLIGATIONS) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in MATERIALS_OBLIGATIONS),
        "pre_source_complete_branch_seal": PRE_SOURCE_SEAL_PATH,
        "authority_source_count": len(MATERIALS_AUTHORITY_SOURCES),
        "authority_source_set_hash": sha256_identity(tuple(asdict(row) for row in MATERIALS_AUTHORITY_SOURCES)),
        "unclassified_obligations": [],
        "frontier_obligations": [],
        "obligations": rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    destination = ROOT / "publications/inventories/materials.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"frozen Materials inventory: {len(MATERIALS_OBLIGATIONS)} obligations; "
        f"{payload['admitted_claim_count_at_freeze']} admitted"
    )


if __name__ == "__main__":
    main()
