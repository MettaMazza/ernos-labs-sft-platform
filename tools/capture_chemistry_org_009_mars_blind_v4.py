#!/usr/bin/env python3
"""Capture the three preregistered MARS USPTO50K splits once after the V4 seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capture_chemistry_org_009_blind_sources_v1 import fetch

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v4.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v4.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-mars-blind-v4"
EXPECTED_IDENTITY = "sha256:6b84bb8fced57a4e65031936932fe314d08d7097bf3f5ba6cea36460e11806c7"
EXPECTED_PRESEAL = "sha256:5c050e976756117ce29b6ee6b9c99030f16ad28df5394af8cf4f790e9259d6b2"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY or digest(PRESEAL.read_bytes()) != EXPECTED_PRESEAL:
        raise SystemExit("ORG-009 V4 identity or prediction seal changed before capture")
    identity = json.loads(IDENTITY.read_text())
    if identity.get("external_values_products_reaction_rows_or_outcomes_present") is not False:
        raise SystemExit("ORG-009 V4 identity is not outcome-free")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    names = {
        "SFT-CHEM-ORG-009-MARS-TRAIN": "mars_uspto50k_train.csv",
        "SFT-CHEM-ORG-009-MARS-VALID": "mars_uspto50k_valid.csv",
        "SFT-CHEM-ORG-009-MARS-TEST": "mars_uspto50k_test.csv",
    }
    rows = []
    for source in identity["outcome_unopened_rows"]:
        path = OUTPUT / names[source["target_id"]]
        if path.exists():
            raise SystemExit(f"ORG-009 MARS source already exists; recapture prohibited: {path}")
        payload, status, headers = fetch(source["uri"])
        registered = source["registered_http_head"]
        if status != 200 or len(payload) != registered["content_length"] or headers.get("etag", "").strip('"') != registered["etag"]:
            raise SystemExit(f"ORG-009 MARS registered response changed: {source['target_id']}")
        path.write_bytes(payload)
        rows.append({**source, "capture_status": "captured_once_after_v4_claim_specific_seal", "http_status": status, "opened_snapshot_path": path.relative_to(ROOT).as_posix(), "opened_snapshot_bytes": len(payload), "opened_snapshot_sha256": digest(payload), "response_etag": headers.get("etag"), "response_content_type": headers.get("content-type")})
    inventory = {"schema": "sft-v3-chemistry-org-009-mars-capture-inventory/4", "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009", "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(), "prediction_seal_sha256": EXPECTED_PRESEAL, "all_v1_v2_v3_results_preserved": True, "source_recapture_count": 0, "all_payloads_opened_only_after_v4_seal": True, "rows": rows}
    inventory_path = OUTPUT / "source-inventory-v4.json"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
