#!/usr/bin/env python3
"""Capture the complete pre-registered KIN-012 source surface."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "experiments/external_sources/chemistry/kinetic_isotope_effect_capture_spec_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-012-kinetic-isotope-effect-v1"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    specification = json.loads(SPEC.read_text())
    if specification.get("target_values_or_hashes_present") is not False:
        raise SystemExit("KIN-012 prefetch specification is not value-free")
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    records = []
    for row in specification["sources"]:
        request = Request(row["url"], headers={"User-Agent": "Ernos-Labs-SFT-source-custody/1"})
        with urlopen(request, timeout=120) as response:
            payload = response.read()
        path = SNAPSHOT / row["source_document_identity"]
        path.write_bytes(payload)
        records.append({
            **row,
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_hash": hash_file(path),
            "byte_count": len(payload),
        })
    inventory = {
        "schema": "sft-v3-kinetic-isotope-effect-source-inventory/1",
        "article_doi": "10.1038/s41467-024-44753-x",
        "complete_source_file_count": len(records),
        "complete_source_files": records,
        "all_complete_files_retained_without_value_selection": True,
        "prefetch_spec_hash": hash_file(SPEC),
    }
    write_json(SNAPSHOT / "source-inventory-v1.json", inventory)
    print(json.dumps({"files": len(records), "bytes": sum(row["byte_count"] for row in records)}, sort_keys=True))


if __name__ == "__main__":
    main()
