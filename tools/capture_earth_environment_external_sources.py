#!/usr/bin/env python3
"""Capture every preregistered Earth source and preserve every transport result."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "experiments/earth_environment/source_registry.json"
OUTPUT = ROOT / "experiments/external_sources/earth_environment"
MANIFEST_PATH = OUTPUT / "capture_manifest.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_hash(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def capture(row: dict[str, object]) -> tuple[dict[str, object], bytes | None]:
    request = urllib.request.Request(
        str(row["locator"]),
        headers={"User-Agent": "Ernos-Labs-SFT-Earth-Evidence-Capture/1.0 (+https://github.com/MettaMazza/ernos-labs-sft-platform)"},
    )
    started = datetime.now(timezone.utc).isoformat()
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            content_type = response.headers.get_content_type()
            suffix = ".json" if "json" in content_type else ".xml" if "xml" in content_type else ".txt" if content_type.startswith("text/plain") else ".html" if "html" in content_type else ".bin"
            relative = f"experiments/external_sources/earth_environment/snapshots/{row['source_id']}{suffix}"
            return ({
                "source_id": row["source_id"],
                "source_identity": row["source_identity"],
                "registered_locator": row["locator"],
                "attempted_at_utc": started,
                "transport_status": "captured",
                "http_status": getattr(response, "status", None),
                "resolved_locator": response.geturl(),
                "content_type": content_type,
                "byte_count": len(data),
                "snapshot_path": relative,
                "snapshot_hash": file_hash(data),
                "error_class": None,
                "error_message": None,
            }, data)
    except Exception as error:  # the exact transport failure is evidence
        status = error.code if isinstance(error, urllib.error.HTTPError) else None
        return ({
            "source_id": row["source_id"],
            "source_identity": row["source_identity"],
            "registered_locator": row["locator"],
            "attempted_at_utc": started,
            "transport_status": "failed",
            "http_status": status,
            "resolved_locator": None,
            "content_type": None,
            "byte_count": None,
            "snapshot_path": None,
            "snapshot_hash": None,
            "error_class": type(error).__name__,
            "error_message": str(error)[:500],
        }, None)


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    claimed = registry.pop("registry_hash")
    if digest(registry) != claimed:
        raise ValueError("Earth source registry identity changed")
    registry["registry_hash"] = claimed
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "snapshots").mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(capture, registry["sources"]))
    rows = []
    for record, data in results:
        rows.append(record)
        if data is not None:
            destination = ROOT / str(record["snapshot_path"])
            destination.write_bytes(data)

    manifest = {
        "schema": "sft-v3-earth-environment-source-capture-manifest/1",
        "registry_path": str(REGISTRY_PATH.relative_to(ROOT)),
        "registry_hash": claimed,
        "attempt_count": len(rows),
        "captured_count": sum(row["transport_status"] == "captured" for row in rows),
        "failed_count": sum(row["transport_status"] == "failed" for row in rows),
        "all_registered_sources_attempted_once": len(rows) == registry["source_count"] and len({row["source_id"] for row in rows}) == len(rows),
        "failed_transports_preserved": True,
        "captures": rows,
    }
    manifest["manifest_hash"] = digest(manifest)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "registered_external_sources_captured_feature_audit_not_yet_executed",
        "source_capture_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_capture_manifest_hash": manifest["manifest_hash"],
        "captured_source_count": manifest["captured_count"],
        "failed_source_transport_count": manifest["failed_count"],
        "next_exact_operation": "audit_registered_source_features_and_build_claim_specific_external_targets",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth source capture: captured={manifest['captured_count']} failed={manifest['failed_count']} manifest={manifest['manifest_hash']}")
    for row in rows:
        print(f"{row['source_id']}: {row['transport_status']}" + (f" ({row['error_class']})" if row["transport_status"] == "failed" else ""))


if __name__ == "__main__":
    main()
