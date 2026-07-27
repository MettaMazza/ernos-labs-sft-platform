#!/usr/bin/env python3
"""Capture the complete predeclared INORG-001 authority surface byte-for-byte."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/coordination_entity_capture_spec_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-001-coordination-entity-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def fetch(uri: str) -> bytes:
    request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
    if len(payload) < 500:
        raise ValueError(f"INORG-001 response unexpectedly short: {uri}")
    return payload


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    if spec.get("target_values_present") is not False:
        raise ValueError("INORG-001 prefetch specification is not value-free")
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for ordinal, source in enumerate(spec["sources"], start=1):
        payload = fetch(source["uri"])
        path = SNAPSHOT / source["document_identity"]
        path.write_bytes(payload)
        rows.append({
            "source_ordinal": ordinal,
            "authority": source["authority"],
            "source_role": source["source_role"],
            "uri": source["uri"],
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_bytes": len(payload),
            "snapshot_sha256": hash_file(path),
        })
    inventory = {
        "schema": "sft-v3-coordination-entity-source-inventory/1",
        "chemistry_obligation": spec["chemistry_obligation"],
        "claim_id": spec["claim_id"],
        "prefetch_spec_sha256": hash_file(SPEC),
        "complete_source_file_count": len(rows),
        "complete_source_bytes": sum(row["snapshot_bytes"] for row in rows),
        "rows": rows,
    }
    write_json(INVENTORY, inventory)
    print(json.dumps({"files": len(rows), "bytes": inventory["complete_source_bytes"]}, sort_keys=True))
    print(INVENTORY.relative_to(ROOT), hash_file(INVENTORY))


if __name__ == "__main__":
    main()
