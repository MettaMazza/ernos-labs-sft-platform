#!/usr/bin/env python3
"""Capture the complete preregistered ORG-007 outcome-unopened source surface."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity
from sft.engine.source import hash_file


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_007_target_identities_v1.json"
IDENTITY_HASH = "sha256:5dcb77e93b457fc4c02e93c3b8aac171d0813ecee72c8046e2cef36a2c585bff"
SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_007_nucleophilic_substitution_pre_source_v1.json"
SEAL_PAYLOAD_HASH = "sha256:70f38b8bb83b54b5613c9ea8f3639f15dc0382dd80afed58247b5e7a4add287e"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-007-blind-v1"


def _verify_boundary() -> dict:
    if hash_file(IDENTITY) != IDENTITY_HASH:
        raise SystemExit("ORG-007 identity boundary changed: VOID_INVALID_HALTED")
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != SEAL_PAYLOAD_HASH or sha256_identity(seal) != SEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-007 prediction boundary changed: VOID_INVALID_HALTED")
    return json.loads(IDENTITY.read_text(encoding="utf-8"))


def _filename(source_id: str) -> str:
    return source_id.lower().replace("_", "-") + ".json"


def main() -> int:
    identities = _verify_boundary()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for identity in identities["rows"]:
        if "exact-payload-unopened" not in identity["custody_class"] and "structure-payload-unopened" not in identity["custody_class"]:
            continue
        request = Request(
            identity["uri"],
            headers={"User-Agent": "Ernos-Labs-SFT-Open-Science/3 ORG-007 fixed-source-capture"},
        )
        payload = b""
        status = "unresolved"
        content_type = ""
        error_class = ""
        try:
            with urlopen(request, timeout=60) as response:
                payload = response.read()
                status = f"http-{response.status}"
                content_type = response.headers.get("Content-Type", "")
        except HTTPError as exc:
            payload = exc.read()
            status = f"http-{exc.code}"
            content_type = exc.headers.get("Content-Type", "") if exc.headers else ""
            error_class = type(exc).__name__
        except URLError as exc:
            payload = json.dumps(
                {"source_id": identity["source_id"], "error": type(exc).__name__, "reason": str(exc.reason)},
                sort_keys=True,
            ).encode("utf-8")
            status = "transport-failure"
            content_type = "application/json"
            error_class = type(exc).__name__
        path = OUTPUT / _filename(identity["source_id"])
        path.write_bytes(payload)
        rows.append(
            {
                "target_id": identity["target_id"],
                "source_id": identity["source_id"],
                "uri": identity["uri"],
                "response_status": status,
                "content_type": content_type,
                "error_class": error_class,
                "snapshot_path": str(path.relative_to(ROOT)),
                "snapshot_sha256": hash_file(path),
                "byte_count": len(payload),
            }
        )
    inventory = {
        "schema": "sft-v3-complete-post-seal-source-inventory/1",
        "claim_id": identities["claim_id"],
        "identity_path": str(IDENTITY.relative_to(ROOT)),
        "identity_hash": IDENTITY_HASH,
        "prediction_path": str(SEAL.relative_to(ROOT)),
        "prediction_payload_hash": SEAL_PAYLOAD_HASH,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "registered_new_target_count": 7,
        "captured_response_count": len(rows),
        "all_registered_new_targets_retained": len(rows) == 7,
        "rows": rows,
    }
    (OUTPUT / "source-inventory-v1.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"captured": len(rows), "inventory": str((OUTPUT / "source-inventory-v1.json").relative_to(ROOT))}))
    return 0 if len(rows) == 7 else 1


if __name__ == "__main__":
    raise SystemExit(main())
