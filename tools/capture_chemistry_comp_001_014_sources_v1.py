#!/usr/bin/env python3
"""Capture every pre-registered COMP-001--014 official source route."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/external_sources/chemistry/comp_001_014_whole_subfield_source_identity_registry_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/comp-001-014-whole-subfield-v1"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def suffix(url: str, content_type: str) -> str:
    lowered = content_type.casefold()
    if "json" in lowered or url.rstrip("/").endswith("JSON") or "/JSON?" in url:
        return ".json"
    if "sdf" in lowered or url.rstrip("/").endswith("SDF") or "/SDF?" in url:
        return ".sdf"
    if "html" in lowered:
        return ".html"
    if "plain" in lowered or url.endswith((".tsv", ".csv", ".txt")):
        return ".txt"
    return ".bin"


def fetch(url: str) -> tuple[int | None, str, bytes, str | None, str]:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-V3-open-science-capture/1.0 (Maria.Smith.Sftoe@gmail.com)", "Accept": "*/*"})
    try:
        with urlopen(request, timeout=90) as response:
            data = response.read()
            return response.status, response.headers.get("Content-Type", ""), data, None, response.geturl()
    except HTTPError as error:
        data = error.read()
        return error.code, error.headers.get("Content-Type", "") if error.headers else "", data, f"HTTPError:{error.code}", error.geturl()
    except (URLError, TimeoutError, OSError) as error:
        return None, "", b"", f"{type(error).__name__}:{error}", url


def main() -> None:
    if SNAPSHOT.exists():
        raise SystemExit("snapshot already exists; capture is immutable")
    registry = json.loads(REGISTRY.read_text())
    SNAPSHOT.mkdir(parents=True)
    rows = []
    for source in registry["sources"]:
        if str(source.get("capture_url", "")).startswith("repository:"):
            relative = str(source["capture_url"]).removeprefix("repository:")
            target = ROOT / relative
            data = target.read_bytes()
            rows.append({
                "source_id": source["source_id"], "route": "capture_url", "url": source["capture_url"],
                "final_url": source["capture_url"], "status": "repository-existing", "content_type": "repository-artifact",
                "path": relative, "bytes": len(data), "sha256": digest(data), "transport_error": None,
                "previously_exposed": True,
            })
            continue
        routes = []
        for key in ("capture_url", "sdf_url", "property_url", "structure_url"):
            value = source.get(key)
            if value and value not in tuple(url for _, url in routes):
                routes.append((key, value))
        for route, url in routes:
            status, content_type, data, error, final_url = fetch(url)
            stem = re.sub(r"[^a-z0-9]+", "-", source["source_id"].casefold()).strip("-") + "-" + route.replace("_", "-")
            path = None
            if data:
                destination = SNAPSHOT / (stem + suffix(url, content_type))
                destination.write_bytes(data)
                path = str(destination.relative_to(ROOT))
            rows.append({
                "source_id": source["source_id"], "route": route, "url": url, "final_url": final_url,
                "status": status, "content_type": content_type, "path": path, "bytes": len(data),
                "sha256": digest(data), "transport_error": error, "previously_exposed": False,
            })
            time.sleep(0.25)
    inventory = {
        "schema": "sft-v3-comp-001-014-source-inventory/1",
        "family": registry["family"],
        "registered_source_count": len(registry["sources"]),
        "captured_route_count": len(rows),
        "captured_artifact_count": sum(bool(row["path"]) for row in rows),
        "captured_byte_count": sum(row["bytes"] for row in rows),
        "transport_failure_count": sum(bool(row["transport_error"]) for row in rows),
        "all_routes_retained_including_failures": True,
        "records": rows,
    }
    inventory_path = SNAPSHOT / "source-inventory-v1.json"
    inventory_path.write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({key: inventory[key] for key in ("captured_route_count", "captured_artifact_count", "captured_byte_count", "transport_failure_count")}, indent=2))


if __name__ == "__main__":
    main()
