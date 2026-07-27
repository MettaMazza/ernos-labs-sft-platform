#!/usr/bin/env python3
"""Open the preregistered Rhea Diels-Alder query once after the V7 seal."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capture_chemistry_org_009_blind_sources_v1 import fetch


ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v7.json"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_query_v7.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-rhea-diels-alder-query-v7"
EXPECTED_IDENTITY = "sha256:1b0dd39446a4480ea0479ad1d08412e729054331ccb116b8c0ca17c3b599abde"
EXPECTED_PREDICTION = "sha256:b5a4d052b6b9c8dc1f768c9cbffb4f7e9da3dae7e1753d50844578ae7c33d8ee"
EXPECTED_PAYLOAD_SEAL = "sha256:c651ebedf854ad0d12dc03e9af5a740a46a51cedbf2a68643c9acb4779c5a662"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY or digest(PREDICTION.read_bytes()) != EXPECTED_PREDICTION:
        raise SystemExit("ORG-009 V7 identity or prediction changed before query")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    canonical = digest(json.dumps(prediction, sort_keys=True, separators=(",", ":")).encode())
    if claimed != EXPECTED_PAYLOAD_SEAL or canonical != claimed:
        raise SystemExit("ORG-009 V7 canonical prediction seal is invalid")
    if identity.get("query_outcome_open_count_before_v7_seal") != 0:
        raise SystemExit("ORG-009 V7 query was not outcome-unopened")
    target = identity["outcome_unopened_label_query"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    snapshot = OUTPUT / "rhea-diels-alder-query.tsv"
    inventory_path = OUTPUT / "source-inventory-v7.json"
    if snapshot.exists() or inventory_path.exists():
        raise SystemExit("ORG-009 V7 query already exists; recapture prohibited")
    payload, status, headers = fetch(target["uri"])
    if status != 200 or not payload:
        raise SystemExit(f"ORG-009 V7 query failed with HTTP status {status}")
    snapshot.write_bytes(payload)
    row = {
        **target,
        "capture_status": "captured_once_after_v7_query_seal",
        "http_status": status,
        "opened_snapshot_path": snapshot.relative_to(ROOT).as_posix(),
        "opened_snapshot_bytes": len(payload),
        "opened_snapshot_sha256": digest(payload),
        "response_content_type": headers.get("content-type"),
        "response_last_modified": headers.get("last-modified"),
        "response_etag": headers.get("etag"),
    }
    inventory = {
        "schema": "sft-v3-chemistry-org-009-rhea-diels-alder-query-inventory/7",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PREDICTION.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PREDICTION,
        "query_recapture_count": 0,
        "query_opened_only_after_v7_seal": True,
        "rows": [row],
    }
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "row": row}, indent=2))


if __name__ == "__main__":
    main()
