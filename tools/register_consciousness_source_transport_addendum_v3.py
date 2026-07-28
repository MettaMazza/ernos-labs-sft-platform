#!/usr/bin/env python3
"""Register exact-work author/publisher transports for two older source records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def main() -> None:
    registry = json.loads((ROOT / "experiments/consciousness/source_registry.json").read_text(encoding="utf-8"))
    prior = json.loads((ROOT / "experiments/external_sources/consciousness/capture_manifest_v3.json").read_text(encoding="utf-8"))
    rows = {row["source_id"]: row for row in registry["sources"]}
    definitions = (
        (
            "CONSC-SYNESTHESIA-BATTERY-2007",
            "https://synesthete.org/files/EaglemanetalSynesthesiaBattery2006.pdf",
            "author research site",
            "application/pdf",
        ),
        (
            "CONSC-SYNESTHETIC-COLOUR-MATCH-2008",
            "https://www.sciencedirect.com/science/article/pii/S0042698908000503",
            "journal publisher",
            "text/html",
        ),
    )
    routes = [
        {
            "source_id": source_id,
            "source_identity_uri": rows[source_id]["source_uri"],
            "transport_uri": uri,
            "transport_authority": authority,
            "expected_content_type": content_type,
            "scientific_work_identity": "same title, authors and DOI as the registered PMC record",
            "reason": "The official metadata transport contains only the abstract; this route exposes the same registered scientific work.",
        }
        for source_id, uri, authority, content_type in definitions
    ]
    payload = {
        "schema": "sft-v3-consciousness-source-transport-addendum/3",
        "registration_date": "2026-07-27",
        "source_registry_hash": registry["registry_hash"],
        "preserved_v3_capture_manifest_hash": prior["capture_manifest_hash"],
        "scientific_source_identities_changed": False,
        "registered_features_changed": False,
        "scientific_outcomes_used_to_select_transport": False,
        "routes": routes,
    }
    payload["addendum_hash"] = identity(payload)
    path = ROOT / "experiments/consciousness/source_transport_addendum_v3.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered {len(routes)} exact-work transports: {payload['addendum_hash']}")


if __name__ == "__main__":
    main()
