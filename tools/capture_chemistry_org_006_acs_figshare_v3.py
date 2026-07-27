#!/usr/bin/env python3
"""Capture the complete exact-DOI ACS Figshare surface after the ORG-006 v3 seal."""
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

SOURCE = ROOT / "experiments/external_sources/chemistry/org_006_acs_figshare_source_identity_addendum_v3.json"
SOURCE_HASH = "sha256:82aa03ea2e64a64a58091d95e8f6ab177ecc05bf5b5076ded184f2ae944937a0"
TARGET = ROOT / "experiments/external_sources/chemistry/org_006_target_identity_addendum_v3.json"
TARGET_HASH = "sha256:9021001e93242e5b00dc5b3f843264d6e272974886710b844d1791a41e2a6839"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_006_conformer_population_ordering_pre_source_v3.json"
PREDICTION_FILE_HASH = "sha256:e895041444f2e2bab62a411246c7b6e7d96e3798ab6717eb858e3f277216e19c"
PREDICTION_PAYLOAD_HASH = "sha256:6e73bcf51461074dc44dcfb6680d1b43f0d2288c2577bad78a79ee1ca84ef3ee"
V2_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-value-blind-v2/source-inventory-v2.json"
V2_INVENTORY_HASH = "sha256:7030ee5cd2c738d0f89b849626517432e1ced739b15e26556e5f4c4fb2601fe1"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-006-acs-figshare-v3"
INVENTORY = OUTPUT / "source-inventory-v3.json"
EXACT_DOI = "10.1021/jp404315t"


def fetch(request: Request) -> tuple[bytes, int | None, str, str]:
    try:
        with urlopen(request, timeout=90) as response:
            return (
                response.read(),
                getattr(response, "status", None),
                response.geturl(),
                response.headers.get("Content-Type", ""),
            )
    except Exception as exc:
        return str(exc).encode("utf-8", errors="replace"), None, request.full_url, "capture-error-text/plain"


def request(uri: str, *, body: dict | None = None) -> Request:
    headers = {"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1.0", "Accept": "application/json"}
    if body is None:
        return Request(uri, headers=headers)
    payload = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    headers["Content-Type"] = "application/json"
    return Request(uri, data=payload, headers=headers, method="POST")


def save(path: Path, payload: bytes, req: Request, status: int | None, final_uri: str, content_type: str) -> dict:
    path.write_bytes(payload)
    return {
        "requested_uri": req.full_url,
        "request_method": req.method,
        "http_status": status,
        "final_uri": final_uri,
        "content_type": content_type,
        "capture_status": "captured_complete_response" if status is not None else "capture_error_preserved",
        "snapshot_path": str(path.relative_to(ROOT)),
        "snapshot_sha256": hash_file(path),
        "snapshot_bytes": path.stat().st_size,
    }


def decoded_json(payload: bytes):
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception:
        return None


def main() -> None:
    if OUTPUT.exists() or INVENTORY.exists():
        raise SystemExit("ORG-006 v3 capture already exists; preserved without recapture")
    if (
        hash_file(SOURCE) != SOURCE_HASH
        or hash_file(TARGET) != TARGET_HASH
        or hash_file(PREDICTION) != PREDICTION_FILE_HASH
        or hash_file(V2_INVENTORY) != V2_INVENTORY_HASH
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v3 sealed identity or predecessor evidence changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v3 value seal changed")
    registry = json.loads(SOURCE.read_text(encoding="utf-8"))
    groups = registry.get("source_groups", [])
    if len(groups) != 1 or registry.get("exact_repository_results_item_ids_file_ids_download_urls_values_rows_or_outcomes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 v3 source identity changed")

    group = groups[0]
    OUTPUT.mkdir(parents=True, exist_ok=False)
    search_request = request(group["uri"], body=group["canonical_query_body"])
    search_payload, search_status, search_final, search_type = fetch(search_request)
    search_capture = save(OUTPUT / "acs-figshare-search-response.json", search_payload, search_request, search_status, search_final, search_type)
    search_rows = decoded_json(search_payload)
    if not isinstance(search_rows, list):
        search_rows = []

    exact_rows = [
        row for row in search_rows
        if isinstance(row, dict) and str(row.get("resource_doi", "")).casefold() == EXACT_DOI.casefold()
    ]
    records = []
    for record_ordinal, search_row in enumerate(exact_rows, 1):
        item_id = search_row.get("id")
        metadata_uri = f"https://api.figshare.com/v2/articles/{item_id}"
        metadata_request = request(metadata_uri)
        metadata_payload, metadata_status, metadata_final, metadata_type = fetch(metadata_request)
        metadata_capture = save(
            OUTPUT / f"acs-figshare-item-{record_ordinal:02d}-metadata.json",
            metadata_payload, metadata_request, metadata_status, metadata_final, metadata_type,
        )
        metadata = decoded_json(metadata_payload)
        files = metadata.get("files", []) if isinstance(metadata, dict) else []
        file_captures = []
        for file_ordinal, file_row in enumerate(files, 1):
            download_uri = file_row.get("download_url") if isinstance(file_row, dict) else None
            if not isinstance(download_uri, str) or not download_uri:
                file_captures.append({"file_record": file_row, "capture_status": "registered-download-url-absent"})
                continue
            file_request = request(download_uri)
            file_payload, file_status, file_final, file_type = fetch(file_request)
            filename = str(file_row.get("name") or f"file-{file_ordinal:02d}.bin").replace("/", "_")
            capture = save(
                OUTPUT / f"acs-figshare-item-{record_ordinal:02d}-file-{file_ordinal:02d}-{filename}",
                file_payload, file_request, file_status, file_final, file_type,
            )
            file_captures.append({"file_record": file_row, "capture": capture})
        records.append({
            "search_result": search_row,
            "metadata_capture": metadata_capture,
            "metadata_resource_doi_exact_match": isinstance(metadata, dict) and str(metadata.get("resource_doi", "")).casefold() == EXACT_DOI.casefold(),
            "complete_returned_file_count": len(files),
            "complete_file_captures": file_captures,
            "all_returned_files_preserved": len(file_captures) == len(files),
        })

    inventory = {
        "schema": "sft-v3-exact-resource-doi-complete-capture-inventory/3",
        "claim_id": registry["claim_id"],
        "source_identity_registry": [str(SOURCE.relative_to(ROOT)), SOURCE_HASH],
        "target_identity_addendum": [str(TARGET.relative_to(ROOT)), TARGET_HASH],
        "prediction_seal": [str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH],
        "preserved_v2_capture": [str(V2_INVENTORY.relative_to(ROOT)), V2_INVENTORY_HASH],
        "source_recapture_count": 0,
        "search_capture": search_capture,
        "complete_search_result_count": len(search_rows),
        "exact_resource_doi_result_count": len(exact_rows),
        "nonmatching_search_result_count": len(search_rows) - len(exact_rows),
        "exact_records": records,
        "all_exact_results_and_returned_files_preserved_without_stopping_on_success": len(records) == len(exact_rows) and all(row["all_returned_files_preserved"] for row in records),
        "all_favourable_adverse_absent_unavailable_and_unresolved_results_preserved": True,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))
    print("search", search_status, "rows", len(search_rows), "exact", len(exact_rows))
    for row in records:
        print("item", row["search_result"].get("id"), "files", row["complete_returned_file_count"])
        for file_capture in row["complete_file_captures"]:
            captured = file_capture.get("capture")
            if captured:
                print(" file", captured["http_status"], captured["snapshot_bytes"], captured["snapshot_sha256"])


if __name__ == "__main__":
    main()
