#!/usr/bin/env python3
"""Capture the exact-work transports registered by addendum v3."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "experiments/consciousness/source_transport_addendum_v3.json"
SNAPSHOTS = ROOT / "experiments/external_sources/consciousness/snapshots_v4"
MANIFEST = ROOT / "experiments/external_sources/consciousness/capture_manifest_v4.json"


def hash_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for route in addendum["routes"]:
        request = urllib.request.Request(route["transport_uri"], headers={"User-Agent": "Mozilla/5.0 Ernos-Labs-SFT-V3-source-custodian/1"})
        suffix = ".pdf" if route["expected_content_type"] == "application/pdf" else ".html"
        path = SNAPSHOTS / (route["source_id"].lower() + suffix)
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                content = response.read()
                status = getattr(response, "status", 200)
                content_type = response.headers.get("Content-Type", "unreported")
            if suffix == ".pdf" and not content.startswith(b"%PDF"):
                raise ValueError("registered PDF transport did not return a PDF")
            if suffix == ".html" and len(content) < 100_000:
                raise ValueError("publisher transport returned an incomplete HTML response")
            path.write_bytes(content)
            row = {
                "source_id": route["source_id"],
                "source_identity_uri": route["source_identity_uri"],
                "transport_uri": route["transport_uri"],
                "capture_status": "captured_exact_work",
                "http_status": status,
                "content_type": content_type,
                "snapshot_path": str(path.relative_to(ROOT)),
                "snapshot_size": len(content),
                "snapshot_hash": hash_bytes(content),
                "transport_error": None,
            }
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            row = {
                "source_id": route["source_id"],
                "source_identity_uri": route["source_identity_uri"],
                "transport_uri": route["transport_uri"],
                "capture_status": "transport_failed_preserved",
                "http_status": getattr(error, "code", None),
                "content_type": None,
                "snapshot_path": None,
                "snapshot_size": None,
                "snapshot_hash": None,
                "transport_error": f"{type(error).__name__}: {error}",
            }
        rows.append(row)
        print(f"{route['source_id']}: {row['capture_status']}", flush=True)

    payload = {
        "schema": "sft-v3-consciousness-external-capture-manifest/4",
        "capture_date": "2026-07-27",
        "transport_addendum_hash": addendum["addendum_hash"],
        "preserved_v3_capture_manifest_hash": addendum["preserved_v3_capture_manifest_hash"],
        "route_count": len(rows),
        "captured_count": sum(row["capture_status"] == "captured_exact_work" for row in rows),
        "transport_failure_count": sum(row["capture_status"] != "captured_exact_work" for row in rows),
        "earlier_transport_failures_remain_preserved": True,
        "rows": rows,
    }
    payload["capture_manifest_hash"] = identity(payload)
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update(
        {
            "status": "external_source_capture_complete_all_historical_failures_preserved",
            "source_transport_addendum_v3": str(ADDENDUM.relative_to(ROOT)),
            "source_transport_addendum_v3_hash": addendum["addendum_hash"],
            "source_capture_manifest_v4": str(MANIFEST.relative_to(ROOT)),
            "source_capture_manifest_v4_hash": payload["capture_manifest_hash"],
            "additional_v4_captured_source_count": payload["captured_count"],
            "additional_v4_failed_source_transport_count": payload["transport_failure_count"],
            "next_exact_operation": "verify_registered_features_and_build_claim_specific_postseal_targets",
        }
    )
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"capture v4: {payload['capture_manifest_hash']} captured={payload['captured_count']} failed={payload['transport_failure_count']}")


if __name__ == "__main__":
    main()
