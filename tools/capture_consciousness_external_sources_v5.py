#!/usr/bin/env python3
"""Preserve and inspect a publisher response whose HTTP status is adverse.

ScienceDirect returns the registered article body together with HTTP 403 to
this non-browser custodian.  The status must remain adverse; the returned bytes
are preserved separately and may be used only after their article identity is
verified.  No earlier manifest is rewritten.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
ADDENDUM = ROOT / "experiments/consciousness/source_transport_addendum_v3.json"
SNAPSHOTS = ROOT / "experiments/external_sources/consciousness/snapshots_v5"
MANIFEST = ROOT / "experiments/external_sources/consciousness/capture_manifest_v5.json"
SOURCE_ID = "CONSC-SYNESTHETIC-COLOUR-MATCH-2008"
REQUIRED_IDENTITY_MARKERS = (
    "Early visual mechanisms do not contribute to synesthetic color experience",
    "10.1016/j.visres.2008.01.024",
    "Hong",
    "Blake",
)


def hash_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    route = next(row for row in addendum["routes"] if row["source_id"] == SOURCE_ID)
    request = urllib.request.Request(
        route["transport_uri"],
        headers={
            "User-Agent": "Mozilla/5.0 Ernos-Labs-SFT-V3-source-custodian/1",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-GB,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            content = response.read()
            http_status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "unreported")
    except urllib.error.HTTPError as error:
        content = error.read()
        http_status = error.code
        content_type = error.headers.get("Content-Type", "unreported")

    text = content.decode("utf-8", errors="ignore")
    markers = {marker: marker.casefold() in text.casefold() for marker in REQUIRED_IDENTITY_MARKERS}
    identity_verified = len(content) > 100_000 and all(markers.values())
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS / "consc-synesthetic-colour-match-2008.html"
    path.write_bytes(content)
    payload = {
        "schema": "sft-v3-consciousness-external-capture-manifest/5",
        "capture_date": "2026-07-27",
        "transport_addendum_hash": addendum["addendum_hash"],
        "preserved_v4_capture_manifest_hash": json.loads(
            (ROOT / "experiments/external_sources/consciousness/capture_manifest_v4.json").read_text(encoding="utf-8")
        )["capture_manifest_hash"],
        "source_id": SOURCE_ID,
        "source_identity_uri": route["source_identity_uri"],
        "transport_uri": route["transport_uri"],
        "capture_status": "content_preserved_with_adverse_http_status",
        "http_status": http_status,
        "http_status_passed": False,
        "content_type": content_type,
        "snapshot_path": str(path.relative_to(ROOT)),
        "snapshot_size": len(content),
        "snapshot_hash": hash_bytes(content),
        "article_identity_markers": markers,
        "article_identity_verified": identity_verified,
        "earlier_transport_failure_remains_preserved": True,
    }
    payload["capture_manifest_hash"] = identity(payload)
    MANIFEST.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not identity_verified:
        raise ValueError("adverse publisher response does not identify the registered article")

    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update(
        {
            "status": "external_source_content_complete_with_adverse_transport_history_preserved",
            "source_capture_manifest_v5": str(MANIFEST.relative_to(ROOT)),
            "source_capture_manifest_v5_hash": payload["capture_manifest_hash"],
            "next_exact_operation": "verify_registered_features_and_build_claim_specific_postseal_targets",
        }
    )
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"preserved verified article content with HTTP {http_status}: {payload['capture_manifest_hash']}")


if __name__ == "__main__":
    main()
