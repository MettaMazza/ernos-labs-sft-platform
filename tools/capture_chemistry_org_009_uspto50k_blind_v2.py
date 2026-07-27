#!/usr/bin/env python3
"""Capture the preregistered USPTO-50K ORG-009 payload once after the V2 seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capture_chemistry_org_009_blind_sources_v1 import fetch

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v2.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v2.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-uspto50k-blind-v2"
EXPECTED_IDENTITY = "sha256:c78fa69c33b1109dc75b7893ce80a07885721dd5d628e285b0566f7b6487aa94"
EXPECTED_PRESEAL = "sha256:538be5c575534831557e1ada725a6a4b52a200b278f2459a69ce2d59106ea67a"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY:
        raise SystemExit("ORG-009 V2 target identity changed before capture")
    if digest(PRESEAL.read_bytes()) != EXPECTED_PRESEAL:
        raise SystemExit("ORG-009 V2 prediction seal changed before capture")
    identity = json.loads(IDENTITY.read_text())
    if identity.get("external_values_products_reaction_rows_or_outcomes_present") is not False:
        raise SystemExit("ORG-009 V2 identity is not outcome-free")
    source = identity["outcome_unopened_rows"][0]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / "USPTO_50K.csv"
    if path.exists():
        raise SystemExit("ORG-009 USPTO-50K source already exists; recapture prohibited")
    payload, status, headers = fetch(source["uri"])
    registered = source["registered_http_head"]
    if status != 200 or len(payload) != registered["content_length"]:
        raise SystemExit("ORG-009 USPTO-50K registered response changed")
    if headers.get("etag", "").strip('"') != registered["etag"]:
        raise SystemExit("ORG-009 USPTO-50K registered ETag changed")
    path.write_bytes(payload)
    row = {
        **source,
        "capture_status": "captured_once_after_v2_claim_specific_seal",
        "http_status": status,
        "opened_snapshot_path": path.relative_to(ROOT).as_posix(),
        "opened_snapshot_bytes": len(payload),
        "opened_snapshot_sha256": digest(payload),
        "response_last_modified": headers.get("last-modified"),
        "response_etag": headers.get("etag"),
        "response_content_type": headers.get("content-type"),
    }
    inventory = {
        "schema": "sft-v3-chemistry-org-009-uspto50k-capture-inventory/2",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PRESEAL,
        "v1_blind_adverse_surface_preserved": True,
        "source_recapture_count": 0,
        "payload_opened_only_after_v2_seal": True,
        "rows": [row],
    }
    inventory_path = OUTPUT / "source-inventory-v2.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "row": row}, indent=2))


if __name__ == "__main__":
    main()
