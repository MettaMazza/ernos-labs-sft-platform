#!/usr/bin/env python3
"""Capture the three preregistered atom-mapped Schneider-50K splits once."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from capture_chemistry_org_009_blind_sources_v1 import fetch

ROOT = Path(__file__).resolve().parents[1]
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_009_target_identities_v3.json"
PRESEAL = ROOT / "experiments/sealed_predictions/chemistry_org_009_addition_reaction_pre_source_v3.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-009-schneider50k-blind-v3"
EXPECTED_IDENTITY = "sha256:010287086572655861bf4f1a686fbecc13612e350dea511f579d2179a4ab3816"
EXPECTED_PRESEAL = "sha256:4a6f9fa9bed47259f3f50e02e396a187e10a0b53f9844c88f5115b4a5e0f56ad"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if digest(IDENTITY.read_bytes()) != EXPECTED_IDENTITY:
        raise SystemExit("ORG-009 V3 target identity changed before capture")
    if digest(PRESEAL.read_bytes()) != EXPECTED_PRESEAL:
        raise SystemExit("ORG-009 V3 prediction seal changed before capture")
    identity = json.loads(IDENTITY.read_text())
    if identity.get("external_values_products_reaction_rows_or_outcomes_present") is not False:
        raise SystemExit("ORG-009 V3 identity is not outcome-free")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    names = {
        "SFT-CHEM-ORG-009-SCHNEIDER50K-TRAIN": "schneider50k_train.csv",
        "SFT-CHEM-ORG-009-SCHNEIDER50K-VALID": "schneider50k_valid.csv",
        "SFT-CHEM-ORG-009-SCHNEIDER50K-TEST": "schneider50k_test.csv",
    }
    rows = []
    for source in identity["outcome_unopened_rows"]:
        path = OUTPUT / names[source["target_id"]]
        if path.exists():
            raise SystemExit(f"ORG-009 Schneider-50K source already exists; recapture prohibited: {path}")
        payload, status, headers = fetch(source["uri"])
        registered = source["registered_http_head"]
        if status != 200 or len(payload) != registered["content_length"]:
            raise SystemExit(f"ORG-009 Schneider-50K registered response changed: {source['target_id']}")
        if headers.get("etag", "").strip('"') != registered["etag"]:
            raise SystemExit(f"ORG-009 Schneider-50K registered ETag changed: {source['target_id']}")
        path.write_bytes(payload)
        rows.append(
            {
                **source,
                "capture_status": "captured_once_after_v3_claim_specific_seal",
                "http_status": status,
                "opened_snapshot_path": path.relative_to(ROOT).as_posix(),
                "opened_snapshot_bytes": len(payload),
                "opened_snapshot_sha256": digest(payload),
                "response_etag": headers.get("etag"),
                "response_content_type": headers.get("content-type"),
            }
        )
    inventory = {
        "schema": "sft-v3-chemistry-org-009-schneider50k-capture-inventory/3",
        "claim_id": "SFT-CHEM-ADDITION-REACTION-FAMILY-009",
        "prediction_seal_path": PRESEAL.relative_to(ROOT).as_posix(),
        "prediction_seal_sha256": EXPECTED_PRESEAL,
        "v1_and_v2_adverse_surfaces_preserved": True,
        "source_recapture_count": 0,
        "all_payloads_opened_only_after_v3_seal": True,
        "rows": rows,
    }
    inventory_path = OUTPUT / "source-inventory-v3.json"
    inventory_path.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"inventory": inventory_path.relative_to(ROOT).as_posix(), "rows": rows}, indent=2))


if __name__ == "__main__":
    main()
