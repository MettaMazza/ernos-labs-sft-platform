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
from sft.materials.successor_evidence import SOURCES as SUCCESSOR_SOURCES, SPECS as SUCCESSOR_SPECS, validate_pre_source_seal as validate_successor_seal  # noqa: E402
from sft.materials.successor_obligations import MATERIALS_SUCCESSOR_OBLIGATIONS  # noqa: E402


def main() -> None:
    validate_sources(ROOT)
    successor_seal = validate_successor_seal(ROOT)
    admitted = {
        row["claim_id"]
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    all_obligations = MATERIALS_OBLIGATIONS + MATERIALS_SUCCESSOR_OBLIGATIONS
    specs = {row.claim_id: row for row in MATERIALS_SPECS + SUCCESSOR_SPECS}
    rows = []
    for position, obligation in enumerate(all_obligations, 1):
        values = asdict(obligation)
        values["position"] = position
        values["candidate_count"] = 256
        values["unique_survivor"] = specs[obligation.claim_id].exact_result
        values["status"] = (
            "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"
        )
        rows.append(values)
    counts = Counter(row.subbranch for row in all_obligations)
    payload = {
        "schema": "sft-v3-materials-branch-inventory/1",
        "branch_id": "materials",
        "inventory_frozen": True,
        "inventory_date": "2026-07-27",
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
        "required_claim_count": len(all_obligations),
        "required_claim_ids": [row.claim_id for row in all_obligations],
        "candidate_count": len(all_obligations) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in all_obligations),
        "pre_source_complete_branch_seal": PRE_SOURCE_SEAL_PATH,
        "successor_pre_source_complete_branch_seal": {"path": "experiments/sealed_predictions/materials_v1_v2_successor_complete_pre_source.json", "hash": successor_seal},
        "authority_source_count": len(MATERIALS_AUTHORITY_SOURCES) + len(SUCCESSOR_SOURCES),
        "authority_source_set_hash": sha256_identity((tuple(asdict(row) for row in MATERIALS_AUTHORITY_SOURCES), tuple(asdict(row) for row in SUCCESSOR_SOURCES))),
        "unclassified_obligations": [],
        "frontier_obligations": [],
        "obligations": rows,
    }
    payload["inventory_hash"] = sha256_identity(payload)
    destination = ROOT / "publications/inventories/materials.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"frozen Materials inventory: {len(all_obligations)} obligations; "
        f"{payload['admitted_claim_count_at_freeze']} admitted"
    )


if __name__ == "__main__":
    main()
