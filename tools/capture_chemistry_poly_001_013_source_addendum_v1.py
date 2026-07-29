#!/usr/bin/env python3
"""Capture the registered Polymer quantitative addendum without substitution."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import ssl
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/external_sources/chemistry/poly_001_013_quantitative_source_addendum_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-quantitative-addendum-v1"


def sha(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return "sha256:" + digest


def main() -> None:
    if SNAPSHOT.exists():
        raise SystemExit("Polymer quantitative addendum snapshot already exists")
    registry = json.loads(REGISTRY.read_text())
    if registry.get("registered_before_addendum_capture") is not True:
        raise SystemExit("Polymer quantitative addendum ordering is invalid")
    SNAPSHOT.mkdir(parents=True)
    context = ssl.create_default_context(); rows = []
    for index, source in enumerate(registry["sources"], 1):
        route = source["capture_url"]
        suffix = ".pdf" if ".pdf" in route.casefold() or "get_pdf" in route.casefold() else ".html"
        path = SNAPSHOT / f"{index:02d}_{source['source_id'].casefold().replace('-', '_')}{suffix}"
        request = urllib.request.Request(route, headers={"User-Agent": "Ernos-Labs-SFT-V3-Polymer-Evidence/1 (+https://github.com/MettaMazza)"})
        try:
            with urllib.request.urlopen(request, timeout=120, context=context) as response, path.open("wb") as handle:
                shutil.copyfileobj(response, handle)
                rows.append({"source_id": source["source_id"], "route": route, "final_url": response.geturl(), "http_status": int(getattr(response, "status", 200)), "content_type": response.headers.get("Content-Type", ""), "status": "captured", "path": str(path.relative_to(ROOT)), "sha256": sha(path), "bytes": path.stat().st_size})
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ssl.SSLError) as error:
            if path.exists(): path.unlink()
            rows.append({"source_id": source["source_id"], "route": route, "status": "registered_transport_failure_preserved", "error_type": type(error).__name__, "error": str(error)})
    inventory = {"schema": "sft-v3-polymer-quantitative-addendum-source-inventory/1", "captured_at": datetime.now(timezone.utc).isoformat(), "registered_addendum_path": str(REGISTRY.relative_to(ROOT)), "registered_addendum_hash": sha(REGISTRY), "source_count": len(rows), "captured_count": sum(row["status"] == "captured" for row in rows), "transport_failure_count": sum(row["status"] != "captured" for row in rows), "complete_source_manifest": rows}
    (SNAPSHOT / "source-inventory-v1.json").write_text(json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({key: inventory[key] for key in ("source_count", "captured_count", "transport_failure_count")}, sort_keys=True))


if __name__ == "__main__":
    main()
