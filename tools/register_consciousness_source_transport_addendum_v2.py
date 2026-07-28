#!/usr/bin/env python3
"""Register official metadata transports for sources absent from full-text XML.

This is a transport-only addendum.  It preserves the registered scientific
identities, features, first capture, and v1 transport failures verbatim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def identity(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


PMCID_TO_PMID = {
    "CONSC-ATTENTIONAL-BLINK-2014": ("PMC3954951", "24434237"),
    "CONSC-SYNESTHESIA-BATTERY-2007": ("PMC4118597", "16919755"),
    "CONSC-SYNESTHETIC-COLOUR-MATCH-2008": ("PMC2423348", "18316107"),
    "CONSC-COLOUR-CATEGORY-LEARNING-2010": ("PMC2890491", "20479228"),
}


def main() -> None:
    registry = json.loads(
        (ROOT / "experiments/consciousness/source_registry.json").read_text(encoding="utf-8")
    )
    prior = json.loads(
        (ROOT / "experiments/external_sources/consciousness/capture_manifest_v2.json").read_text(encoding="utf-8")
    )
    failed = {row["source_id"] for row in prior["rows"] if row["capture_status"] != "captured"}
    if failed != set(PMCID_TO_PMID):
        raise ValueError("v2 failure set differs from the predeclared transport-only recovery set")

    registry_rows = {row["source_id"]: row for row in registry["sources"]}
    routes = []
    for source_id, (pmcid, pmid) in PMCID_TO_PMID.items():
        source = registry_rows[source_id]
        routes.append(
            {
                "source_id": source_id,
                "source_identity_uri": source["source_uri"],
                "pmcid": pmcid,
                "pmid": pmid,
                "transport_uri": (
                    "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                    f"?query={pmcid}&resultType=core&format=json"
                ),
                "transport_authority": "Europe PMC",
                "transport_scope": "bibliographic metadata and indexed abstract",
                "reason": "The registered PMC item is not available through Europe PMC fullTextXML.",
            }
        )

    payload = {
        "schema": "sft-v3-consciousness-source-transport-addendum/2",
        "registration_date": "2026-07-27",
        "source_registry_hash": registry["registry_hash"],
        "preserved_first_capture_manifest_hash": prior["preserved_first_capture_manifest_hash"],
        "preserved_v2_capture_manifest_hash": prior["capture_manifest_hash"],
        "scientific_source_identities_changed": False,
        "registered_features_changed": False,
        "scientific_outcomes_used_to_select_transport": False,
        "routes": routes,
    }
    payload["addendum_hash"] = identity(payload)
    path = ROOT / "experiments/consciousness/source_transport_addendum_v2.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered {len(routes)} metadata routes: {payload['addendum_hash']}")


if __name__ == "__main__":
    main()
