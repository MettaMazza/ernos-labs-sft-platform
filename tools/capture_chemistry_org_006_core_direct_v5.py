#!/usr/bin/env python3
"""Capture both fixed CORE download routes registered under the ORG-006 v5 seal."""
from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402

SOURCE = ROOT / "experiments/external_sources/chemistry/org_006_core_direct_source_identity_addendum_v5.json"
SOURCE_HASH = "sha256:bcca1b8211fd359b70292b1f7cc07c82a723c56add1d941b56de4fe03b9ab7dc"
TARGET = ROOT / "experiments/external_sources/chemistry/org_006_target_identity_addendum_v5.json"
TARGET_HASH = "sha256:ca55055db1a974973131a5fc18fdafcde47e4e3218f32a2c27e2ee5f9762912d"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v5.json"
PREDICTION_FILE_HASH = "sha256:76b38b99801d4c158eb32d9568202012f671e3834150fa6af3690ab7dd9d6202"
PREDICTION_PAYLOAD_HASH = "sha256:937757ab2e2cb928be4d1e779b0d19ee1c15bf38022acddf971f3c87b3dc1121"
V4_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-file-v4/source-inventory-v4.json"
V4_INVENTORY_HASH = "sha256:0b54ce16024ab5646e8498b9bad65aec864c85ec281a3c85035aead2cfe61d0e"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-core-direct-v5"
INVENTORY = OUTPUT / "source-inventory-v5.json"


def main() -> None:
    if OUTPUT.exists() or INVENTORY.exists():
        raise SystemExit("ORG-006 v5 capture already exists; preserved without recapture")
    if any((hash_file(SOURCE) != SOURCE_HASH, hash_file(TARGET) != TARGET_HASH, hash_file(PREDICTION) != PREDICTION_FILE_HASH, hash_file(V4_INVENTORY) != V4_INVENTORY_HASH)):
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v5 sealed identity or predecessor evidence changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v5 value seal changed")
    registry = json.loads(SOURCE.read_text(encoding="utf-8"))
    sources = registry.get("sources", [])
    if len(sources) != 2 or registry.get("exact_download_outcomes_payloads_values_tables_or_figures_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v5 source identity changed")
    OUTPUT.mkdir(parents=True, exist_ok=False)
    captures = []
    for ordinal, source in enumerate(sources, 1):
        request = Request(source["uri"], headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1.0"})
        try:
            with urlopen(request, timeout=90) as response:
                payload = response.read()
                status = getattr(response, "status", None)
                final_uri = response.geturl()
                content_type = response.headers.get("Content-Type", "")
        except Exception as exc:
            payload = str(exc).encode("utf-8", errors="replace")
            status = None
            final_uri = source["uri"]
            content_type = "capture-error-text/plain"
        extension = ".pdf" if payload.startswith(b"%PDF") else ".txt"
        path = OUTPUT / f"core-43583184-route-{ordinal:02d}{extension}"
        path.write_bytes(payload)
        captures.append({
            **source,
            "http_status": status,
            "final_uri": final_uri,
            "content_type": content_type,
            "capture_status": "captured_complete_response" if status is not None else "capture_error_preserved",
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_sha256": hash_file(path),
            "snapshot_bytes": path.stat().st_size,
            "pdf_signature": payload.startswith(b"%PDF"),
        })
    inventory = {
        "schema": "sft-v3-complete-fixed-provider-download-capture-inventory/5",
        "claim_id": registry["claim_id"],
        "source_identity_registry": [str(SOURCE.relative_to(ROOT)), SOURCE_HASH],
        "target_identity_addendum": [str(TARGET.relative_to(ROOT)), TARGET_HASH],
        "prediction_seal": [str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH],
        "preserved_v4_capture": [str(V4_INVENTORY.relative_to(ROOT)), V4_INVENTORY_HASH],
        "source_recapture_count": 0,
        "complete_registered_source_count": len(sources),
        "captures": captures,
        "all_registered_routes_preserved_without_stopping_on_success": len(captures) == len(sources),
        "all_favourable_adverse_absent_unavailable_and_unresolved_results_preserved": True,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))
    for row in captures:
        print(row["source_id"], row["http_status"], row["content_type"], row["snapshot_bytes"], row["snapshot_sha256"], row["pdf_signature"])


if __name__ == "__main__":
    main()
