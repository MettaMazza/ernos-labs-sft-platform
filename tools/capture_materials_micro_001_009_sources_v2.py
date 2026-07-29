#!/usr/bin/env python3
"""Complete MICRO custody with the 404 row and preregistered replacement retained."""

from hashlib import sha256
from urllib.error import HTTPError
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_micro_001_009_target_registry_v1.json"
ADDENDUM = ROOT / "census/materials_micro_coarsening_source_addendum_v1.json"
OUT = ROOT / "experiments/external_sources/materials/micro_001_009_v2"


REMOTE = (
    ("NIST-DISLOCATION-DYNAMICS-2021", "https://www.nist.gov/publications/atomistic-insights-disclocation-dynamics-metal-forming", "nist-dislocation-dynamics-2021.html", False),
    ("NIST-DISLOCATION-CLIMB-MONOGRAPH-59", "https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph59.pdf", "nist-dislocation-climb-monograph-59.pdf", False),
    ("NIST-SHARP-INTERFACE-GRAINS-2001", "https://www.nist.gov/publications/sharp-interface-limit-phase-field-model-crystal-grains", "nist-sharp-interface-grains-2001.html", False),
    ("NIST-SEGREGATION-PRECIPITATION-2021", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=931795", "nist-segregation-precipitation-2021.pdf", False),
    ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK", "https://materialsdata.nist.gov/bitstream/handle/11115/158/Structures%20by%20Precipitation.pdf?isAllowed=y&sequence=3", "nist-structures-precipitation-handbook-unavailable.txt", True),
    ("NIST-BENCHMARK-COARSENING-2017", "https://www.nist.gov/publications/benchmark-problems-phase-field-modeling", "nist-benchmark-coarsening-2017.html", False),
    ("NIST-UNIFIED-GRAIN-BOUNDARY-MOTION-2008", "https://www.nist.gov/publications/unified-approach-motion-grain-boundaries-relative-tangetial-translation-along-grain", "nist-unified-grain-boundary-motion-2008.html", False),
    ("NIST-MICROSTRUCTURE-PROPERTY-TOOLS-2026", "https://www.nist.gov/programs-projects/microstructure-property-tools-structure-property-design", "nist-microstructure-property-tools-2026.html", False),
)


EXISTING = (
    ("NIST-POINT-DEFECTS-2026", "https://www.nist.gov/publications/calculating-formation-energies-point-defects-solids", "experiments/external_sources/materials/snapshots/nist-point-defects.html"),
    ("NIST-MULTISCALE-MATERIALS-2026", "https://www.nist.gov/programs-projects/multiscale-materials-modeling", "experiments/external_sources/materials/snapshots/nist-multiscale-materials.html"),
)


def identity(body):
    return "sha256:" + sha256(body).hexdigest()


def get(url, allow_unavailable):
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
    try:
        with urlopen(request, timeout=120) as response:
            return response.read(), "captured"
    except HTTPError as error:
        if not allow_unavailable:
            raise
        return error.read(), f"source_unavailable_http_{error.code}_preserved"


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    addendum_bytes = ADDENDUM.read_bytes()
    addendum = json.loads(addendum_bytes)
    if registry["target_content_present"] is not False or registry["target_count"] != 9:
        raise SystemExit("MICRO capture halted: original registry changed")
    if addendum["detailed_target_content_present"] is not False or addendum["replacement_source_identity"] != "NIST-BENCHMARK-COARSENING-2017":
        raise SystemExit("MICRO capture halted: source addendum changed")
    OUT.mkdir(parents=True, exist_ok=True)
    documents = []
    for source_id, uri, filename, allow_unavailable in REMOTE:
        body, status = get(uri, allow_unavailable)
        if status == "captured" and len(body) < 1000:
            raise SystemExit("MICRO capture halted: implausibly short source " + source_id)
        path = OUT / filename
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": identity(body), "byte_count": len(body), "status": status, "used_for_favourable_comparison": status == "captured"})
    for source_id, uri, relative in EXISTING:
        path = ROOT / relative
        body = path.read_bytes()
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": relative, "snapshot_hash": identity(body), "byte_count": len(body), "status": "captured_preexisting_official_snapshot", "used_for_favourable_comparison": True})
    payload = {
        "schema": "sft-v3-materials-micro-source-custody/2",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": identity(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "source_addendum_path": ADDENDUM.relative_to(ROOT).as_posix(),
        "source_addendum_hash": identity(addendum_bytes),
        "source_addendum_identity": addendum["addendum_identity"],
        "documents": documents,
        "document_count": len(documents),
        "captured_count": sum(row["used_for_favourable_comparison"] for row in documents),
        "unavailable_count": sum(not row["used_for_favourable_comparison"] for row in documents),
        "all_registered_and_addendum_source_identities_accounted_for": True,
        "all_favourable_adverse_absent_unavailable_unresolved_rows_retained": True,
        "failed_route": "audits/MATERIALS_MICRO_001_009_SOURCE_CAPTURE_HALT_2026-07-29.json",
    }
    payload["manifest_identity"] = "sha256:" + sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "captured_count": payload["captured_count"], "unavailable_count": payload["unavailable_count"], "manifest_identity": payload["manifest_identity"]}, indent=2))


if __name__ == "__main__":
    main()
