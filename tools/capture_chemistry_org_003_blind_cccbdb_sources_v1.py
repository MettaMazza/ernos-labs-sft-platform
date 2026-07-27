#!/usr/bin/env python3
"""Capture the three outcome-unopened ORG-003 CCCBDB pages after sealing."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import ssl
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_003_target_identities_v1.json"
IDENTITY_HASH = "sha256:c4ad884ce29b88a63362ac2c32aac3f267f1b3c66626460f5572f851c7057cf7"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_003_aromatic_recurrence_stability_pre_source.json"
PREDICTION_FILE_HASH = "sha256:f8d7938126d337d60fd3c2a2e56889552c74c88b7daf136772b7c94a7ed26085"
PREDICTION_PAYLOAD_HASH = "sha256:eb06a1bd1cf7b4555eb08dc6c7c81dd27c5795fe035a24a53d5b282a4fef9038"
INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-003-blind-cccbdb-v1/source-inventory-v1.json"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if INVENTORY.exists():
        raise SystemExit("ORG-003 blind source inventory already exists; preserved without recapture")
    if hash_file(IDENTITY) != IDENTITY_HASH or hash_file(PREDICTION) != PREDICTION_FILE_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 identity or prediction seal changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 prediction payload changed")
    if prediction.get("blind_target_content_fetched_or_opened") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind target was not sealed unopened")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    rows = tuple(row for row in identity["rows"] if row["custody_class"].startswith("identity-only-outcome-unopened"))
    if len(rows) != 3 or identity.get("outcome_unopened_blind_target_count") != 3:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind identity census changed")
    for row in rows:
        path = ROOT / row["intended_snapshot_path"]
        if path.exists():
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-003 blind snapshot already exists: {path}")
    context = ssl.create_default_context()
    captured = []
    for row in rows:
        request = Request(
            row["source_uri"],
            headers={
                "User-Agent": "Ernos-Labs-SFT-v3-independent-empirical-capture/1 (+https://github.com/MettaMazza)"
            },
        )
        with urlopen(request, timeout=60, context=context) as response:
            payload = response.read()
            status = response.status
            final_uri = response.geturl()
            content_type = response.headers.get("Content-Type", "")
        path = ROOT / row["intended_snapshot_path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        captured.append(
            {
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "registered_source_uri": row["source_uri"],
                "final_source_uri": final_uri,
                "snapshot_path": row["intended_snapshot_path"],
                "snapshot_sha256": hash_file(path),
                "byte_count": len(payload),
                "http_status": status,
                "content_type": content_type,
                "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
    write_json(
        INVENTORY,
        {
            "schema": "sft-v3-postseal-external-source-inventory/1",
            "claim_id": identity["claim_id"],
            "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
            "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
            "source_count": len(captured),
            "source_recapture_count": 0,
            "all_registered_sources_captured_once": len(captured) == 3,
            "rows": captured,
        },
    )
    print(f"{INVENTORY.relative_to(ROOT)} {hash_file(INVENTORY)}")
    for row in captured:
        print(row["source_id"], row["snapshot_sha256"], row["byte_count"], row["http_status"])


if __name__ == "__main__":
    main()
