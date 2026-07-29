#!/usr/bin/env python3
"""Capture the registered post-seal C3H8O linked records without selection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/external_sources/chemistry/comp_004_formula_linked_source_identity_addendum_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1"
OUTPUT = ROOT / "experiments/external_sources/chemistry/comp_004_formula_linked_transport_addendum_v1.json"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def fetch(url: str):
    try:
        with urlopen(Request(url, headers={"User-Agent": "Ernos-Labs-SFT-V3-open-science-capture/1.0 (Maria.Smith.Sftoe@gmail.com)"}), timeout=90) as response:
            return response.status, response.read(), None, response.geturl()
    except HTTPError as error:
        return error.code, error.read(), f"HTTPError:{error.code}", error.geturl()
    except (URLError, OSError, TimeoutError) as error:
        return None, b"", f"{type(error).__name__}:{error}", url


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("linked transport addendum already exists")
    rows = []
    for record in json.loads(REGISTRY.read_text())["records"]:
        for route in ("json_url", "sdf_url"):
            status, data, error, final_url = fetch(record[route])
            extension = ".json" if route == "json_url" else ".sdf"
            path = SNAPSHOT / f"pubchem-c3h8o-linked-cid-{record['cid']}-{route.removesuffix('_url')}{extension}"
            if data:
                path.write_bytes(data)
            rows.append({
                "source_id": record["source_id"], "cid": record["cid"], "route": route,
                "url": record[route], "final_url": final_url, "status": status, "transport_error": error,
                "path": str(path.relative_to(ROOT)) if data else None, "bytes": len(data), "sha256": digest(data),
            })
    payload = {
        "schema": "sft-v3-postseal-linked-source-transport-addendum/1",
        "identity_addendum_path": str(REGISTRY.relative_to(ROOT)),
        "identity_addendum_hash": digest(REGISTRY.read_bytes()),
        "records": rows,
        "all_records_retained_including_failures": True,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"routes": len(rows), "artifacts": sum(bool(row["path"]) for row in rows), "failures": sum(bool(row["transport_error"]) for row in rows)}, indent=2))


if __name__ == "__main__":
    main()
