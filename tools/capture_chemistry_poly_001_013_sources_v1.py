#!/usr/bin/env python3
"""Capture the complete registered POLY-001--013 source surface post-seal."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import ssl
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments/external_sources/chemistry/poly_001_013_whole_subfield_source_identity_registry_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/poly-001-013-whole-subfield-v1"


def sha(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    if SNAPSHOT.exists():
        raise SystemExit("Polymer snapshot already exists; refusing to recapture")
    registry = json.loads(REGISTRY.read_text())
    seals = [ROOT / f"experiments/sealed_predictions/chemistry_poly_{value:03d}_pre_source_v1.json" for value in range(1, 14)]
    if not all(path.is_file() for path in seals):
        raise SystemExit("all thirteen Polymer derivation seals must exist before capture")
    if any(json.loads(path.read_text()).get("complete_postseal_source_capture_had_occurred_before_this_seal") is not False for path in seals):
        raise SystemExit("Polymer source ordering assertion failed")
    SNAPSHOT.mkdir(parents=True)
    rows = []
    context = ssl.create_default_context()
    for index, source in enumerate(registry["sources"], 1):
        source_id = source["source_id"]
        route = source["capture_url"]
        safe = source_id.casefold().replace("-", "_")
        if route.startswith("repository:"):
            relative = route.removeprefix("repository:")
            path = ROOT / relative
            if path.is_file():
                rows.append({
                    "source_id": source_id, "route": route, "status": "preserved_existing_immutable_artifact",
                    "path": relative, "sha256": sha(path), "bytes": path.stat().st_size,
                    "prior_exposure_disclosed": True,
                })
            else:
                rows.append({"source_id": source_id, "route": route, "status": "registered_repository_artifact_absent", "error": "path absent"})
            continue
        suffix = ".pdf" if ".pdf" in route.casefold() or "get_pdf" in route.casefold() else ".html"
        destination = SNAPSHOT / f"{index:02d}_{safe}{suffix}"
        request = urllib.request.Request(route, headers={"User-Agent": "Ernos-Labs-SFT-V3-Polymer-Evidence/1 (+https://github.com/MettaMazza)"})
        try:
            with urllib.request.urlopen(request, timeout=120, context=context) as response, destination.open("wb") as output:
                shutil.copyfileobj(response, output)
                status = int(getattr(response, "status", 200))
                content_type = response.headers.get("Content-Type", "")
                final_url = response.geturl()
            rows.append({
                "source_id": source_id, "route": route, "final_url": final_url, "status": "captured",
                "http_status": status, "content_type": content_type,
                "path": str(destination.relative_to(ROOT)), "sha256": sha(destination), "bytes": destination.stat().st_size,
                "prior_exposure_disclosed": True,
            })
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ssl.SSLError) as error:
            if destination.exists():
                destination.unlink()
            rows.append({
                "source_id": source_id, "route": route, "status": "registered_transport_failure_preserved",
                "error_type": type(error).__name__, "error": str(error), "prior_exposure_disclosed": True,
            })
    inventory = {
        "schema": "sft-v3-polymer-whole-subfield-source-inventory/1",
        "family": registry["family"], "captured_at": datetime.now(timezone.utc).isoformat(),
        "capture_started_after_all_thirteen_derivation_seals": True,
        "discovery_exposure_never_relabelled_blind": True,
        "source_count": len(rows), "captured_count": sum(row["status"] == "captured" for row in rows),
        "preserved_existing_count": sum(row["status"] == "preserved_existing_immutable_artifact" for row in rows),
        "transport_failure_count": sum(row["status"] == "registered_transport_failure_preserved" for row in rows),
        "absent_repository_count": sum(row["status"] == "registered_repository_artifact_absent" for row in rows),
        "complete_source_manifest": rows,
    }
    write_json(SNAPSHOT / "source-inventory-v1.json", inventory)
    print(json.dumps({key: inventory[key] for key in ("source_count", "captured_count", "preserved_existing_count", "transport_failure_count", "absent_repository_count")}, sort_keys=True))


if __name__ == "__main__":
    main()
