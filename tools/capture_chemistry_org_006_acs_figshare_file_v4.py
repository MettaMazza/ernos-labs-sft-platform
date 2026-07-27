#!/usr/bin/env python3
"""Capture the one complete ACS Figshare file registered under the ORG-006 v4 seal."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402

SOURCE = ROOT / "experiments/external_sources/chemistry/org_006_acs_figshare_file_source_identity_addendum_v4.json"
SOURCE_HASH = "sha256:9dee56a8a1b51858bb82c8349441dc86bd4a7fba88bddcb8c682bb53fb529a1f"
TARGET = ROOT / "experiments/external_sources/chemistry/org_006_target_identity_addendum_v4.json"
TARGET_HASH = "sha256:a395cfb5428b665fd430e08dc7351f66f14f0b62d083eb9faad02f74989aadb2"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v4.json"
PREDICTION_FILE_HASH = "sha256:ea751c4f872e72e40d865eb9a96797ecaaf3ac8e39cdb6dc384ea8d777a467da"
PREDICTION_PAYLOAD_HASH = "sha256:6b42c72492573c737c924fe48578814641addc296cb641bc8f3b2e529c9224e7"
FAILURE = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-v3/failure-inventory-v3.json"
FAILURE_HASH = "sha256:08d5cfe81d3fc9b6180103316ece4c0780137b40782578fc12258a4b8b10b853"
METADATA = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-v3/acs-figshare-item-01-metadata.json"
METADATA_HASH = "sha256:b0872bc80803a5978934812e1ed3295e6b19765846ddf6d96a6be3796dbd2020"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-file-v4"
INVENTORY = OUTPUT / "source-inventory-v4.json"


def main() -> None:
    if OUTPUT.exists() or INVENTORY.exists():
        raise SystemExit("ORG-006 v4 capture already exists; preserved without recapture")
    if any((
        hash_file(SOURCE) != SOURCE_HASH,
        hash_file(TARGET) != TARGET_HASH,
        hash_file(PREDICTION) != PREDICTION_FILE_HASH,
        hash_file(FAILURE) != FAILURE_HASH,
        hash_file(METADATA) != METADATA_HASH,
    )):
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v4 sealed identity or predecessor evidence changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v4 value seal changed")
    registry = json.loads(SOURCE.read_text(encoding="utf-8"))
    sources = registry.get("sources", [])
    if len(sources) != 1 or registry.get("exact_file_payload_values_rows_or_download_outcome_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v4 file identity changed")
    source = sources[0]
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    files = metadata.get("files", [])
    if len(files) != 1 or files[0].get("download_url") != source["uri"] or files[0].get("name") != "jp404315t_si_001.txt":
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 returned-file identity mismatch")

    OUTPUT.mkdir(parents=True, exist_ok=False)
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
    path = OUTPUT / "jp404315t_si_001.txt"
    path.write_bytes(payload)
    observed_md5 = hashlib.md5(payload).hexdigest()
    capture = {
        "requested_uri": source["uri"],
        "request_method": "GET",
        "http_status": status,
        "final_uri": final_uri,
        "content_type": content_type,
        "capture_status": "captured_complete_response" if status is not None else "capture_error_preserved",
        "snapshot_path": str(path.relative_to(ROOT)),
        "snapshot_sha256": hash_file(path),
        "snapshot_bytes": path.stat().st_size,
        "snapshot_md5": observed_md5,
        "declared_size_match": path.stat().st_size == source["declared_size_bytes"],
        "declared_md5_match": observed_md5 == source["declared_md5"],
    }
    inventory = {
        "schema": "sft-v3-complete-returned-file-capture-inventory/4",
        "claim_id": registry["claim_id"],
        "source_identity_registry": [str(SOURCE.relative_to(ROOT)), SOURCE_HASH],
        "target_identity_addendum": [str(TARGET.relative_to(ROOT)), TARGET_HASH],
        "prediction_seal": [str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH],
        "preserved_v3_failure": [str(FAILURE.relative_to(ROOT)), FAILURE_HASH],
        "source_recapture_count": 0,
        "complete_registered_file_count": 1,
        "file_capture": capture,
        "all_favourable_adverse_absent_unavailable_and_unresolved_results_preserved": True,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))
    print(status, content_type, path.stat().st_size, hash_file(path), observed_md5)


if __name__ == "__main__":
    main()
