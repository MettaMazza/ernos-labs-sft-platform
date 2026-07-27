#!/usr/bin/env python3
"""Capture all 48 sealed non-USPTO ORD parquet payloads once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capture_chemistry_org_009_blind_sources_v1 import fetch


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v9.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_ord_v9.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-ord-holdout-v9"
EXPECTED_IDENTITY = "sha256:763e26e4d60699e7af4ddffb71789b9535df2959259abfed8b29a67e650b7138"
EXPECTED_PREDICTION = "sha256:045b5a0960e729450a6b5d0670fe3d6337c6d066c97ede3e865550b12fdf98cc"
EXPECTED_PAYLOAD_SEAL = "sha256:cdc4cb97a28cf077b377eb9e97bc627882d773fad111a35ea69fd661a55396d3"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY or digest(PREDICTION.read_bytes()) != EXPECTED_PREDICTION:
        raise SystemExit("ORG-009 V9 identity or prediction changed before capture")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    canonical = digest(json.dumps(prediction, sort_keys=True, separators=(",", ":")).encode())
    if claimed != EXPECTED_PAYLOAD_SEAL or canonical != claimed:
        raise SystemExit("ORG-009 V9 canonical prediction seal is invalid")
    if identity.get("parquet_payload_open_count_before_v9_seal") != 0:
        raise SystemExit("ORG-009 V9 parquet payloads were not unopened")
    sources = identity["outcome_unopened_non_uspto_parquet_rows"]
    if len(sources) != 48 or sum(row["registered_bytes"] for row in sources) != 12993815:
        raise SystemExit("ORG-009 V9 registered payload census changed")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    inventory_path = OUTPUT / "source-inventory-v9.json"
    if inventory_path.exists():
        raise SystemExit("ORG-009 V9 capture inventory already exists; recapture prohibited")
    captured = []
    for source in sources:
        filename = source["config"] + ".parquet"
        destination = OUTPUT / filename
        if destination.exists():
            raise SystemExit(f"ORG-009 V9 payload already exists; recapture prohibited: {destination}")
        payload, status, headers = fetch(source["uri"])
        if status != 200 or len(payload) != source["registered_bytes"]:
            raise SystemExit(f"ORG-009 V9 payload changed or failed: {source['config']}")
        destination.write_bytes(payload)
        captured.append({
            **source,
            "capture_status": "captured_once_after_v9_seal",
            "http_status": status,
            "opened_snapshot_path": destination.relative_to(ROOT).as_posix(),
            "opened_snapshot_bytes": len(payload),
            "opened_snapshot_sha256": digest(payload),
            "response_content_type": headers.get("content-type"),
            "response_etag": headers.get("etag"),
        })
    inventory = {
        "schema": "sft-v3-chemistry-org-009-ord-holdout-inventory/9",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PREDICTION.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PREDICTION,
        "source_recapture_count": 0,
        "all_payloads_opened_only_after_v9_seal": True,
        "complete_payload_count": len(captured),
        "complete_payload_bytes": sum(row["opened_snapshot_bytes"] for row in captured),
        "rows": captured,
    }
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "inventory_sha256": digest(inventory_path.read_bytes()), "payload_count": len(captured), "payload_bytes": inventory["complete_payload_bytes"]}, indent=2))


if __name__ == "__main__":
    main()
