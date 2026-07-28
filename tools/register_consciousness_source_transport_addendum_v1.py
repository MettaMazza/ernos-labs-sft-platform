#!/usr/bin/env python3
"""Register deterministic official transports after PMC interstitial failures."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def identity(value: object) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    registry = json.loads((ROOT / "experiments/consciousness/source_registry.json").read_text(encoding="utf-8"))
    first = json.loads((ROOT / "experiments/external_sources/consciousness/capture_manifest.json").read_text(encoding="utf-8"))
    routes = []
    for row in registry["sources"]:
        uri = row["source_uri"]
        if "pmc.ncbi.nlm.nih.gov/articles/PMC" in uri:
            pmcid = uri.rstrip("/").split("/")[-1]
            routes.append({"source_id": row["source_id"], "source_identity_uri": uri, "transport_uri": f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", "transport_authority": "Europe PMC", "reason": "The registered NCBI PMC identity returned a preserved Google interstitial rather than article content."})
        elif row["source_id"] == "CONSC-CIE-1931-CMF":
            routes.append({"source_id": row["source_id"], "source_identity_uri": uri, "transport_uri": "https://files.cie.co.at/CIE_xyz_1931_2deg.csv_metadata.json", "transport_authority": "International Commission on Illumination", "reason": "Official metadata companion to the registered CIE dataset page."})
    payload = {
        "schema": "sft-v3-consciousness-source-transport-addendum/1",
        "registration_date": "2026-07-27", "source_registry_hash": registry["registry_hash"],
        "preserved_first_capture_manifest_hash": first["capture_manifest_hash"],
        "scientific_source_identities_changed": False, "registered_features_changed": False,
        "routes": routes,
    }
    payload["addendum_hash"] = identity(payload)
    path = ROOT / "experiments/consciousness/source_transport_addendum_v1.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"registered {len(routes)} official transport routes: {payload['addendum_hash']}")


if __name__ == "__main__":
    main()

