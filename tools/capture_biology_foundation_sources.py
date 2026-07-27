#!/usr/bin/env python3
"""Capture the post-seal Biology authority sources byte-for-byte."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "experiments/registrations/biology_foundation_authority_source_selection.json"
DESTINATION = ROOT / "experiments/external_sources/biology/snapshots"
MANIFEST = ROOT / "experiments/external_sources/biology/biology_foundation_source_manifest.json"


def main() -> None:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration["pre_source_prediction_seal"] != "sha256:4b3e1ba191d363a1b67e1a02853f071cdf2c9d3d86081fced05ab3c5d079e639":
        raise ValueError("Biology source selection is not bound to the frozen prediction set")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    rows = []
    for position, source in enumerate(registration["sources"], 1):
        suffix = ".cif" if source["uri"].endswith(".cif") else ".html"
        path = DESTINATION / (source["source_id"].lower() + suffix)
        process = subprocess.run(
            (
                "curl", "--location", "--fail", "--silent", "--show-error",
                "--max-time", "90", "--user-agent",
                "Ernos-Labs-SFT/3 biology-foundation reproducibility capture",
                "--output", str(path), source["uri"],
            ),
            check=False,
            capture_output=True,
            text=True,
        )
        if process.returncode:
            rows.append({
                "position": position,
                "source_id": source["source_id"],
                "registered_uri": source["uri"],
                "resolved_uri": source["uri"],
                "purpose": source["purpose"],
                "snapshot_path": None,
                "snapshot_sha256": None,
                "byte_count": None,
                "content_type": None,
                "capture_status": "transport_failed_preserved",
                "transport_error": process.stderr.strip(),
            })
            continue
        content = path.read_bytes()
        final_uri = source["uri"]
        content_type = "chemical/x-mmcif" if suffix == ".cif" else "text/html"
        rows.append({
            "position": position,
            "source_id": source["source_id"],
            "registered_uri": source["uri"],
            "resolved_uri": final_uri,
            "purpose": source["purpose"],
            "snapshot_path": str(path.relative_to(ROOT)),
            "snapshot_sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
            "byte_count": len(content),
            "content_type": content_type,
            "capture_status": "captured_after_complete_prediction_seal",
        })
    manifest = {
        "schema": "sft-v3-biology-authority-source-manifest/1",
        "branch": "biology",
        "registration_path": str(REGISTRATION.relative_to(ROOT)),
        "pre_source_prediction_seal": registration["pre_source_prediction_seal"],
        "source_count": len(rows),
        "all_sources_preserved": all(row["capture_status"] == "captured_after_complete_prediction_seal" for row in rows),
        "sources": rows,
    }
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["manifest_hash"] = "sha256:" + hashlib.sha256(encoded).hexdigest()
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"captured Biology authority sources: {len(rows)}")
    for row in rows:
        print(row["source_id"], row["byte_count"], row["snapshot_sha256"])


if __name__ == "__main__":
    main()
