#!/usr/bin/env python3
"""Capture the value-free-sealed INORG-004 target-identity correction once."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/inorg_004_geometry_identity_correction_v1.json"
SPEC_HASH = "sha256:250c45d33906ecc5f02a318e458b30ba34e81f3fc5cae5da04d841d30dc7e4eb"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"


def main() -> None:
    if hash_file(SPEC) != SPEC_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-004 correction identity changed")
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("target_values_or_outcomes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: correction identity is not value-free")
    if INVENTORY.exists():
        raise SystemExit("INORG-004 correction already captured; preserved without replay")
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for ordinal, source in enumerate(spec["sources"], start=1):
        suffix = ".html"
        name = re.sub(r"[^A-Za-z0-9._-]+", "-", source["source_id"]).lower() + suffix
        path = SNAPSHOT / name
        row = dict(source)
        row.update({"source_ordinal": ordinal, "snapshot_path": str(path.relative_to(ROOT))})
        try:
            request = Request(source["uri"], headers={"User-Agent": "Ernos-Labs-SFT-v3-inorg-004-correction-capture/1"})
            with urlopen(request, timeout=60) as response:
                payload = response.read()
                row["http_status"] = getattr(response, "status", 200)
            path.write_bytes(payload)
            row.update({"capture_status": "captured_complete_response", "snapshot_bytes": len(payload), "snapshot_sha256": hash_file(path)})
        except HTTPError as exc:
            payload = exc.read()
            if payload:
                path.write_bytes(payload)
                row.update({"snapshot_bytes": len(payload), "snapshot_sha256": hash_file(path)})
            row.update({"capture_status": "adverse_http_response_preserved", "http_status": exc.code, "error_class": type(exc).__name__})
        except (URLError, TimeoutError, OSError) as exc:
            row.update({"capture_status": "unresolved_transport_failure_preserved", "error_class": type(exc).__name__, "error_text": str(exc)})
        rows.append(row)
    counts = {}
    for row in rows:
        counts[row["capture_status"]] = counts.get(row["capture_status"], 0) + 1
    payload = {
        "schema": "sft-v3-chemistry-inorg-004-geometry-correction-source-inventory/1",
        "identity_correction_sha256": SPEC_HASH,
        "complete_registered_source_count": len(spec["sources"]),
        "all_registered_rows_preserved": len(rows) == len(spec["sources"]),
        "capture_status_counts": counts,
        "rows": rows,
    }
    INVENTORY.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "statuses": counts}, sort_keys=True))
    print(f"{INVENTORY.relative_to(ROOT)} {hash_file(INVENTORY)}")


if __name__ == "__main__":
    main()
