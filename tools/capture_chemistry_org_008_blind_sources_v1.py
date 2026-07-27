#!/usr/bin/env python3
"""Capture the complete fixed ORG-008 Nature article and supplementary surface."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_008_target_identities_v1.json"
IDENTITY_HASH = "sha256:d718044a43d35b2c2a01a419359cb1316053e6ec684d3dd10d4685565082b453"
SEAL = ROOT / "experiments/sealed_predictions/chemistry_org_008_electrophilic_substitution_pre_source_v1.json"
SEAL_PAYLOAD_HASH = "sha256:6ee04e4bdf6f4446c43e7ddcf867db70108626b3a15a9fcea6d36dff07ee43c3"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-008-nature-blind-v1"


def _boundary() -> dict:
    if hash_file(IDENTITY) != IDENTITY_HASH:
        raise SystemExit("ORG-008 identity changed: VOID_INVALID_HALTED")
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != SEAL_PAYLOAD_HASH or sha256_identity(seal) != SEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-008 prediction changed: VOID_INVALID_HALTED")
    return json.loads(IDENTITY.read_text(encoding="utf-8"))


def main() -> int:
    identities = _boundary()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    selected = [row for row in identities["rows"] if row["target_id"] in {"SFT-CHEM-ORG-008-003", "SFT-CHEM-ORG-008-004"}]
    rows = []
    for identity in selected:
        request = Request(identity["uri"], headers={"User-Agent": "Ernos-Labs-SFT-Open-Science/3 ORG-008 fixed-source-capture"})
        payload = b""; status = "unresolved"; content_type = ""; error_class = ""
        try:
            with urlopen(request, timeout=120) as response:
                payload = response.read(); status = f"http-{response.status}"; content_type = response.headers.get("Content-Type", "")
        except HTTPError as exc:
            payload = exc.read(); status = f"http-{exc.code}"; content_type = exc.headers.get("Content-Type", "") if exc.headers else ""; error_class = type(exc).__name__
        except URLError as exc:
            payload = json.dumps({"source_id": identity["source_id"], "error": type(exc).__name__, "reason": str(exc.reason)}, sort_keys=True).encode()
            status = "transport-failure"; content_type = "application/json"; error_class = type(exc).__name__
        suffix = ".pdf" if "pdf" in identity["uri"].casefold() else ".html"
        path = OUTPUT / (identity["source_id"].casefold() + suffix)
        path.write_bytes(payload)
        rows.append({
            "target_id": identity["target_id"], "source_id": identity["source_id"], "uri": identity["uri"],
            "response_status": status, "content_type": content_type, "error_class": error_class,
            "snapshot_path": str(path.relative_to(ROOT)), "snapshot_sha256": hash_file(path), "byte_count": len(payload),
        })
    inventory = {
        "schema": "sft-v3-complete-post-seal-source-inventory/1", "claim_id": identities["claim_id"],
        "identity_path": str(IDENTITY.relative_to(ROOT)), "identity_hash": IDENTITY_HASH,
        "prediction_path": str(SEAL.relative_to(ROOT)), "prediction_payload_hash": SEAL_PAYLOAD_HASH,
        "captured_at": datetime.now(timezone.utc).isoformat(), "registered_capture_count": 2,
        "captured_response_count": len(rows), "all_registered_capture_targets_retained": len(rows) == 2, "rows": rows,
    }
    (OUTPUT / "source-inventory-v1.json").write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"captured": len(rows), "inventory": str((OUTPUT / "source-inventory-v1.json").relative_to(ROOT))}))
    return 0 if len(rows) == 2 else 1


if __name__ == "__main__":
    raise SystemExit(main())
