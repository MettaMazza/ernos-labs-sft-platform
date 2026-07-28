#!/usr/bin/env python3
"""Register then capture one alternate transport for the failed GVP source."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "experiments/external_sources/earth_environment"
ADDENDUM = OUTPUT / "source_transport_addendum_v1.json"


def digest(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    manifest = json.loads((OUTPUT / "capture_manifest.json").read_text(encoding="utf-8"))
    failed = next(row for row in manifest["captures"] if row["source_id"] == "SMITHSONIAN-GVP-VOTW-001")
    if failed["transport_status"] != "failed" or failed["http_status"] != 403:
        raise ValueError("the preserved Smithsonian transport does not have the registered failure")

    registration = {
        "schema": "sft-v3-earth-environment-source-transport-addendum/1",
        "registered_at_utc": datetime.now(timezone.utc).isoformat(),
        "logical_source_id": "SMITHSONIAN-GVP-VOTW-001",
        "transport_id": "SMITHSONIAN-GVP-VOTW-WFS-CAPABILITIES-001",
        "custodian": "Smithsonian Institution Global Volcanism Program",
        "locator": "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/wfs?request=GetCapabilities",
        "source_kind": "authoritative_volcano_database_wfs_capabilities",
        "registered_features": ["database service identity", "versioned feature types", "volcano and eruption data access", "machine-readable service capabilities"],
        "prior_failed_transport_preserved": True,
        "prior_failed_transport_hash": digest(failed),
        "outcome_opened_before_registration": False,
        "replacement_of_prior_evidence": False,
    }
    registration["registration_hash"] = digest(registration)
    ADDENDUM.parent.mkdir(parents=True, exist_ok=True)
    ADDENDUM.write_text(json.dumps({"registration": registration, "capture": None}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    request = urllib.request.Request(registration["locator"], headers={"User-Agent": "Ernos-Labs-SFT-Earth-Evidence-Capture/1.0"})
    started = datetime.now(timezone.utc).isoformat()
    data = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read()
            snapshot = OUTPUT / "snapshots/SMITHSONIAN-GVP-VOTW-WFS-CAPABILITIES-001.xml"
            snapshot.write_bytes(data)
            capture = {
                "attempted_at_utc": started,
                "transport_status": "captured",
                "http_status": getattr(response, "status", None),
                "resolved_locator": response.geturl(),
                "content_type": response.headers.get_content_type(),
                "byte_count": len(data),
                "snapshot_path": str(snapshot.relative_to(ROOT)),
                "snapshot_hash": "sha256:" + hashlib.sha256(data).hexdigest(),
                "error_class": None,
                "error_message": None,
            }
    except Exception as error:
        capture = {
            "attempted_at_utc": started,
            "transport_status": "failed",
            "http_status": error.code if isinstance(error, urllib.error.HTTPError) else None,
            "resolved_locator": None,
            "content_type": None,
            "byte_count": None,
            "snapshot_path": None,
            "snapshot_hash": None,
            "error_class": type(error).__name__,
            "error_message": str(error)[:500],
        }
    payload = {"registration": registration, "capture": capture}
    payload["addendum_hash"] = digest(payload)
    ADDENDUM.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "source_transport_addendum": str(ADDENDUM.relative_to(ROOT)),
        "source_transport_addendum_hash": payload["addendum_hash"],
        "additional_captured_source_count": 1 if capture["transport_status"] == "captured" else 0,
        "additional_failed_source_transport_count": 1 if capture["transport_status"] == "failed" else 0,
        "next_exact_operation": "audit_registered_source_features_and_build_claim_specific_external_targets",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Earth source addendum: {capture['transport_status']} {payload['addendum_hash']}")


if __name__ == "__main__":
    main()
