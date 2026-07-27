#!/usr/bin/env python3
"""Capture the value-free-sealed INORG-005 linkage authority once."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/inorg_005_linkage_source_identity_addendum_v1.json"
SPEC_HASH = "sha256:980b2752e4617f217b145a491a786baa035d18170db88dbdd6c75783b068a6ba"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1"
DOCUMENT = SNAPSHOT / "iupac-red-book-2005-complete.pdf"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"


def main() -> None:
    if hash_file(SPEC) != SPEC_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 linkage identity addendum changed")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if (
        spec.get("target_values_or_outcomes_present") is not False
        or spec.get("linkage_definition_example_class_formula_page_section_or_payload_present") is not False
    ):
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 linkage identity addendum is not value-free")
    if INVENTORY.exists() or DOCUMENT.exists():
        raise SystemExit("INORG-005 linkage authority already captured; preserved without replay")

    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    source = spec["source"]
    row = {
        "source_ordinal": 1,
        "source_id": source["source_id"],
        "authority": source["authority"],
        "identity": source["identity"],
        "registered_source_role": source["registered_source_role"],
        "custody_status_at_registration": source["custody_status"],
        "uri": source["uri"],
        "snapshot_path": str(DOCUMENT.relative_to(ROOT)),
    }
    try:
        request = Request(
            source["uri"],
            headers={"User-Agent": "Ernos-Labs-SFT-v3-inorg-005-linkage-capture/1"},
        )
        with urlopen(request, timeout=60) as response:
            payload = response.read()
            row["http_status"] = getattr(response, "status", 200)
            row["response_content_type"] = response.headers.get("Content-Type", "")
        DOCUMENT.write_bytes(payload)
        row.update(
            {
                "capture_status": "captured_complete_response",
                "snapshot_bytes": len(payload),
                "snapshot_sha256": hash_file(DOCUMENT),
            }
        )
    except HTTPError as exc:
        payload = exc.read()
        if payload:
            DOCUMENT.write_bytes(payload)
            row.update({"snapshot_bytes": len(payload), "snapshot_sha256": hash_file(DOCUMENT)})
        row.update(
            {
                "capture_status": "adverse_http_response_preserved",
                "http_status": exc.code,
                "error_class": type(exc).__name__,
            }
        )
    except (URLError, TimeoutError, OSError) as exc:
        row.update(
            {
                "capture_status": "unresolved_transport_failure_preserved",
                "error_class": type(exc).__name__,
                "error_text": str(exc),
            }
        )

    inventory = {
        "schema": "sft-v3-chemistry-inorg-005-linkage-source-inventory/1",
        "identity_addendum_sha256": SPEC_HASH,
        "complete_registered_source_count": 1,
        "all_registered_rows_preserved": True,
        "capture_status_counts": {row["capture_status"]: 1},
        "rows": [row],
    }
    INVENTORY.write_text(
        json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"rows": 1, "status": row["capture_status"]}, sort_keys=True))
    print(f"{INVENTORY.relative_to(ROOT)} {hash_file(INVENTORY)}")


if __name__ == "__main__":
    main()
