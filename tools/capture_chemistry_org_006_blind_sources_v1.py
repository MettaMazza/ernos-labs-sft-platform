#!/usr/bin/env python3
"""Capture each ORG-006 value-blind source identity exactly once after sealing."""
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

ADDENDUM = ROOT / "experiments/external_sources/chemistry/org_006_blind_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:72fa75a828a84c2a3eab4c21f5dd4e11bb230ed8d7d1a13ac888540d39b435b6"
IDENTITY = ROOT / "experiments/external_sources/chemistry/org_006_target_identities_v1.json"
IDENTITY_HASH = "sha256:36643ce7da55fd4a59881b2af84ae5e750efc9e37583334617f34ac688fb2d4a"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source.json"
PREDICTION_FILE_HASH = "sha256:a0122d6afcfb87fcb6e553e46ddf2d51939018ddd862fd6848147bc494b283f0"
PREDICTION_PAYLOAD_HASH = "sha256:ac6d9d47c2299a2ad4f0e9cde6d3d82f1b2cad208ff271e685a1db15ad46f413"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-blind-v1"
INVENTORY = OUTPUT / "source-inventory-v1.json"
FILENAMES = {
    "NIST-CCCBDB-109660-INTERNAL-ROTATION-1": "nist-cccbdb-109660-internal-rotation-1.html",
    "OSTI-22415852-PRIMARY-RECORD": "osti-22415852-primary-record.html",
    "OSTI-22415852-PUBLIC-FULLTEXT-ENDPOINT": "osti-22415852-public-fulltext-payload.bin",
}


def main() -> None:
    if INVENTORY.exists() or OUTPUT.exists():
        raise SystemExit("ORG-006 blind capture already exists; preserved without recapture")
    if hash_file(ADDENDUM) != ADDENDUM_HASH or hash_file(IDENTITY) != IDENTITY_HASH or hash_file(PREDICTION) != PREDICTION_FILE_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 sealed identity surface changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 prediction seal changed")
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    sources = addendum.get("sources", [])
    if len(sources) != 3 or addendum.get("exact_values_tables_figures_attachment_outcomes_or_payload_hashes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 blind source registry changed")
    OUTPUT.mkdir(parents=True, exist_ok=False)
    captured = []
    for source in sources:
        path = OUTPUT / FILENAMES[source["source_id"]]
        request = Request(source["uri"], headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1.0"})
        try:
            with urlopen(request, timeout=60) as response:
                payload = response.read()
                status = getattr(response, "status", None)
                final_uri = response.geturl()
                content_type = response.headers.get("Content-Type", "")
        except Exception as exc:
            payload = str(exc).encode("utf-8", errors="replace")
            status = None
            final_uri = source["uri"]
            content_type = "capture-error-text/plain"
        path.write_bytes(payload)
        captured.append({
            **source,
            "capture_status": "captured_complete_response" if status is not None else "capture_error_preserved",
            "http_status": status,
            "final_uri": final_uri,
            "content_type": content_type,
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_sha256": hash_file(path),
            "snapshot_bytes": path.stat().st_size,
        })
    inventory = {
        "schema": "sft-v3-complete-source-capture-inventory/1",
        "claim_id": addendum["claim_id"],
        "source_identity_registry": (str(ADDENDUM.relative_to(ROOT)), ADDENDUM_HASH),
        "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "source_recapture_count": 0,
        "all_favourable_adverse_absent_unavailable_and_unresolved_results_preserved": True,
        "rows": captured,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))
    for row in captured:
        print(row["source_id"], row["http_status"], row["content_type"], row["snapshot_bytes"], row["snapshot_sha256"])


if __name__ == "__main__":
    main()
