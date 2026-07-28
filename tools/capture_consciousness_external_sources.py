#!/usr/bin/env python3
"""Capture every preregistered Consciousness source without changing scope."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "experiments/consciousness/source_registry.json"
SNAPSHOT_DIR = ROOT / "experiments/external_sources/consciousness/snapshots"
MANIFEST_PATH = ROOT / "experiments/external_sources/consciousness/capture_manifest.json"


def sha256_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def main() -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for source in registry["sources"]:
        request = urllib.request.Request(
            source["source_uri"],
            headers={"User-Agent": "Ernos-Labs-SFT-V3-source-custodian/1 (+https://github.com/MettaMazza/ernos-labs-sft-platform)"},
        )
        path = SNAPSHOT_DIR / source["snapshot_name"]
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                content = response.read()
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "unreported")
            path.write_bytes(content)
            row = {
                "source_id": source["source_id"], "source_uri": source["source_uri"],
                "capture_status": "captured", "http_status": status, "content_type": content_type,
                "snapshot_path": str(path.relative_to(ROOT)), "snapshot_size": len(content),
                "snapshot_hash": sha256_bytes(content), "transport_error": None,
            }
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as error:
            row = {
                "source_id": source["source_id"], "source_uri": source["source_uri"],
                "capture_status": "transport_failed_preserved", "http_status": getattr(error, "code", None),
                "content_type": None, "snapshot_path": None, "snapshot_size": None,
                "snapshot_hash": None, "transport_error": f"{type(error).__name__}: {error}",
            }
        rows.append(row)
        print(f"{source['source_id']}: {row['capture_status']}", flush=True)
    manifest = {
        "schema": "sft-v3-consciousness-external-capture-manifest/1",
        "capture_date": "2026-07-27", "source_registry_hash": registry["registry_hash"],
        "source_count": len(rows), "captured_count": sum(row["capture_status"] == "captured" for row in rows),
        "transport_failure_count": sum(row["capture_status"] != "captured" for row in rows),
        "all_transport_failures_preserved": True, "rows": rows,
    }
    manifest["capture_manifest_hash"] = "sha256:" + hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "external_source_capture_complete_with_failures_preserved",
        "source_capture_manifest": str(MANIFEST_PATH.relative_to(ROOT)),
        "source_capture_manifest_hash": manifest["capture_manifest_hash"],
        "captured_source_count": manifest["captured_count"],
        "failed_source_transport_count": manifest["transport_failure_count"],
        "next_exact_operation": "build_claim_specific_external_bindings_and_postseal_targets",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"capture manifest: {manifest['capture_manifest_hash']} captured={manifest['captured_count']} failed={manifest['transport_failure_count']}")


if __name__ == "__main__":
    main()
