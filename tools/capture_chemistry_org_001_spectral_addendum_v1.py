#!/usr/bin/env python3
"""Capture the value-free ORG-001 UV-visible payload identity exactly once."""

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


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_001_spectral_source_identity_addendum_v1.json"
IDENTITY_HASH = "sha256:d4839729d56d75088a5f0c09c3bb8e37070f183ebe8899e6ae579a7b659332c8"
OUTPUT = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-spectral-addendum-v1/nist-c106990-uvvis-index-0.jdx"
INVENTORY = OUTPUT.parent / "source-inventory-v1.json"


def main() -> None:
    if hash_file(IDENTITY) != IDENTITY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 spectral identity changed")
    document = json.loads(IDENTITY.read_text(encoding="utf-8"))
    if document.get("target_values_peaks_intensities_or_outcomes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: ORG-001 spectral identity is not value-free")
    if len(document.get("sources", ())) != 1 or INVENTORY.exists():
        raise SystemExit("ORG-001 spectral capture boundary invalid or already executed")
    source = document["sources"][0]
    request = Request(
        source["uri"],
        headers={"User-Agent": "Ernos-Labs-SFT-v3-organic-spectral-capture/1"},
    )
    row = {key: source[key] for key in ("source_id", "authority", "uri", "identity", "custody_status")}
    row["snapshot_path"] = str(OUTPUT.relative_to(ROOT))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(request, timeout=60) as response:
            payload = response.read()
            row["http_status"] = getattr(response, "status", 200)
        OUTPUT.write_bytes(payload)
        row.update(
            capture_status="captured_complete_response",
            snapshot_bytes=len(payload),
            snapshot_sha256=hash_file(OUTPUT),
        )
    except HTTPError as exc:
        payload = exc.read()
        if payload:
            OUTPUT.write_bytes(payload)
            row.update(snapshot_bytes=len(payload), snapshot_sha256=hash_file(OUTPUT))
        row.update(capture_status="adverse_http_response_preserved", http_status=exc.code)
    except (URLError, TimeoutError, OSError) as exc:
        row.update(capture_status="unresolved_transport_failure_preserved", error_text=str(exc))
    inventory = {
        "schema": "sft-v3-chemistry-org-001-spectral-source-inventory/1",
        "identity_addendum_sha256": IDENTITY_HASH,
        "complete_registered_source_count": 1,
        "all_registered_rows_preserved": True,
        "rows": [row],
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(row, sort_keys=True))
    print(f"{INVENTORY.relative_to(ROOT)} {hash_file(INVENTORY)}")


if __name__ == "__main__":
    main()
