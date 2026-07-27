#!/usr/bin/env python3
"""Capture registered Biology source fallbacks while preserving failures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
REGISTRATION = ROOT / "experiments/registrations/biology_foundation_authority_source_transport_addendum_v1.json"
DESTINATION = ROOT / "experiments/external_sources/biology/snapshots"
MANIFEST = ROOT / "experiments/external_sources/biology/biology_foundation_source_transport_addendum_v1.json"


def main() -> None:
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    rows = []
    for position, source in enumerate(registration["sources"], 1):
        suffix = ".obo" if source["uri"].endswith(".obo") else ".html"
        path = DESTINATION / (source["source_id"].lower() + suffix)
        process = subprocess.run(("curl", "--location", "--fail", "--silent", "--show-error", "--max-time", "90", "--user-agent", "Ernos-Labs-SFT/3 biology-foundation reproducibility capture", "--output", str(path), source["uri"]), check=False, capture_output=True, text=True)
        if process.returncode:
            rows.append({"position": position, "source_id": source["source_id"], "registered_uri": source["uri"], "replaces_failed_transport_source_id": source["replaces_failed_transport_source_id"], "capture_status": "transport_failed_preserved", "transport_error": process.stderr.strip(), "snapshot_path": None, "snapshot_sha256": None, "byte_count": None})
            continue
        content = path.read_bytes()
        rows.append({"position": position, "source_id": source["source_id"], "registered_uri": source["uri"], "replaces_failed_transport_source_id": source["replaces_failed_transport_source_id"], "capture_status": "captured_after_prediction_seal_and_transport_addendum", "snapshot_path": str(path.relative_to(ROOT)), "snapshot_sha256": "sha256:" + hashlib.sha256(content).hexdigest(), "byte_count": len(content)})
    manifest = {"schema": "sft-v3-biology-authority-source-transport-addendum-manifest/1", "registration_path": str(REGISTRATION.relative_to(ROOT)), "pre_source_prediction_seal": registration["pre_source_prediction_seal"], "all_fallbacks_captured": all(row["capture_status"].startswith("captured") for row in rows), "sources": rows}
    manifest["manifest_hash"] = "sha256:" + hashlib.sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Biology source transport addendum: captured={sum(row['capture_status'].startswith('captured') for row in rows)}/{len(rows)}")
    for row in rows:
        print(row["source_id"], row["capture_status"], row["snapshot_sha256"])


if __name__ == "__main__":
    main()
