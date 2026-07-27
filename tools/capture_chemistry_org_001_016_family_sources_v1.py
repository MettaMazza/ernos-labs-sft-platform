#!/usr/bin/env python3
"""Capture the frozen ORG-001–016 authority family exactly once.

The value-free identity registry is immutable input. Successful, adverse,
absent and unresolved responses are preserved without scientific parsing or
survivor selection.
"""

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


REGISTRY = ROOT / "experiments/external_sources/chemistry/org_001_016_family_source_identity_registry_v1.json"
REGISTRY_HASH = "sha256:12c6822a695eb7135081ef8d044a3136c2fee2b0d486c9164b1f1166ef087381"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1"
INVENTORY = SNAPSHOT_ROOT / "source-inventory-v1.json"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def filename(source_id: str, uri: str) -> str:
    suffix = ".json" if uri.endswith("/json") else ".html"
    return re.sub(r"[^A-Za-z0-9._-]+", "-", source_id).lower() + suffix


def main() -> None:
    if hash_file(REGISTRY) != REGISTRY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: Organic family identity registry changed")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    rows = registry.get("sources", [])
    if registry.get("target_values_or_outcomes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: Organic family identity registry is not value-free")
    if len(rows) != 46 or len({row["source_id"] for row in rows}) != 46:
        raise SystemExit("VOID_INVALID_HALTED: Organic family source identity census changed")
    if INVENTORY.exists():
        raise SystemExit("Organic family source inventory already exists; preserved without replay")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    captured = []
    for ordinal, source in enumerate(rows, start=1):
        name = filename(source["source_id"], source["uri"])
        path = SNAPSHOT_ROOT / name
        result = {
            "source_ordinal": ordinal,
            "source_id": source["source_id"],
            "authority": source["authority"],
            "identity": source["identity"],
            "obligations": source["obligations"],
            "custody_status_at_registration": source["custody_status"],
            "uri": source["uri"],
            "snapshot_path": str(path.relative_to(ROOT)),
        }
        request = Request(
            source["uri"],
            headers={"User-Agent": "Ernos-Labs-SFT-v3-organic-family-source-capture/1"},
        )
        try:
            with urlopen(request, timeout=60) as response:
                payload = response.read()
                result["http_status"] = getattr(response, "status", 200)
            path.write_bytes(payload)
            result.update(
                {
                    "capture_status": "captured_complete_response",
                    "snapshot_bytes": len(payload),
                    "snapshot_sha256": hash_file(path),
                }
            )
        except HTTPError as exc:
            payload = exc.read()
            if payload:
                path.write_bytes(payload)
                result["snapshot_bytes"] = len(payload)
                result["snapshot_sha256"] = hash_file(path)
            result.update(
                {
                    "capture_status": "adverse_http_response_preserved",
                    "http_status": exc.code,
                    "error_class": type(exc).__name__,
                }
            )
        except (URLError, TimeoutError, OSError) as exc:
            result.update(
                {
                    "capture_status": "unresolved_transport_failure_preserved",
                    "error_class": type(exc).__name__,
                    "error_text": str(exc),
                }
            )
        captured.append(result)

    counts: dict[str, int] = {}
    for row in captured:
        counts[row["capture_status"]] = counts.get(row["capture_status"], 0) + 1
    inventory = {
        "schema": "sft-v3-chemistry-org-001-016-family-source-inventory/1",
        "family_id": registry["family_id"],
        "identity_registry_sha256": REGISTRY_HASH,
        "complete_registered_source_count": len(rows),
        "all_registered_rows_preserved": len(captured) == len(rows),
        "capture_status_counts": counts,
        "rows": captured,
    }
    write_json(INVENTORY, inventory)
    print(json.dumps({"rows": len(captured), "statuses": counts}, sort_keys=True))
    print(f"{INVENTORY.relative_to(ROOT)} {hash_file(INVENTORY)}")


if __name__ == "__main__":
    main()
