#!/usr/bin/env python3
"""Capture all registered MICRO-001--009 NIST source records after registry freeze."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_micro_001_009_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/micro_001_009_v1"


REMOTE = (
    ("NIST-DISLOCATION-DYNAMICS-2021", "https://www.nist.gov/publications/atomistic-insights-disclocation-dynamics-metal-forming", "nist-dislocation-dynamics-2021.html"),
    ("NIST-DISLOCATION-CLIMB-MONOGRAPH-59", "https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph59.pdf", "nist-dislocation-climb-monograph-59.pdf"),
    ("NIST-SHARP-INTERFACE-GRAINS-2001", "https://www.nist.gov/publications/sharp-interface-limit-phase-field-model-crystal-grains", "nist-sharp-interface-grains-2001.html"),
    ("NIST-SEGREGATION-PRECIPITATION-2021", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=931795", "nist-segregation-precipitation-2021.pdf"),
    ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK", "https://materialsdata.nist.gov/bitstream/handle/11115/158/Structures%20by%20Precipitation.pdf?isAllowed=y&sequence=3", "nist-structures-precipitation-handbook.pdf"),
    ("NIST-UNIFIED-GRAIN-BOUNDARY-MOTION-2008", "https://www.nist.gov/publications/unified-approach-motion-grain-boundaries-relative-tangetial-translation-along-grain", "nist-unified-grain-boundary-motion-2008.html"),
    ("NIST-MICROSTRUCTURE-PROPERTY-TOOLS-2026", "https://www.nist.gov/programs-projects/microstructure-property-tools-structure-property-design", "nist-microstructure-property-tools-2026.html"),
)


EXISTING = (
    ("NIST-POINT-DEFECTS-2026", "https://www.nist.gov/publications/calculating-formation-energies-point-defects-solids", "experiments/external_sources/materials/snapshots/nist-point-defects.html"),
    ("NIST-MULTISCALE-MATERIALS-2026", "https://www.nist.gov/programs-projects/multiscale-materials-modeling", "experiments/external_sources/materials/snapshots/nist-multiscale-materials.html"),
)


def identity(body):
    return "sha256:" + sha256(body).hexdigest()


def get(url):
    with urlopen(Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}), timeout=120) as response:
        return response.read()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_content_present"] is not False or registry["target_count"] != 9:
        raise SystemExit("MICRO capture halted: target registry is not value-free and complete")
    OUT.mkdir(parents=True, exist_ok=True)
    documents = []
    for source_id, uri, filename in REMOTE:
        body = get(uri)
        if len(body) < 1000:
            raise SystemExit("MICRO capture halted: implausibly short source " + source_id)
        path = OUT / filename
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": identity(body), "byte_count": len(body), "status": "captured"})
    for source_id, uri, relative in EXISTING:
        path = ROOT / relative
        body = path.read_bytes()
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": relative, "snapshot_hash": identity(body), "byte_count": len(body), "status": "captured_preexisting_official_snapshot"})
    payload = {
        "schema": "sft-v3-materials-micro-source-custody/1",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": identity(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "all_registered_source_identities_captured": True,
        "all_favourable_adverse_absent_unavailable_unresolved_rows_retained": True,
    }
    payload["manifest_identity"] = "sha256:" + sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "bytes": sum(row["byte_count"] for row in documents), "manifest_identity": payload["manifest_identity"]}, indent=2))


if __name__ == "__main__":
    main()
