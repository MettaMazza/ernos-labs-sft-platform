#!/usr/bin/env python3
"""Capture all registered EXT sources after the target registry is sealed."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_ext_001_008_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/ext_001_008_v1"
REMOTE = (
    ("NIST-HIGH-PRESSURE-MATERIAL-TESTING", "https://www.nist.gov/programs-projects/materials-testing-hydrogen-gas", "nist-high-pressure-material-testing.html"),
    ("NIST-HIGH-TEMPERATURE-THERMOELECTRIC", "https://www.nist.gov/laboratories/tools-instruments/high-temperature-thermoelectric-properties-instrument", "nist-high-temperature-thermoelectric.html"),
    ("NIST-CRYOGENIC-MATERIAL-PROPERTIES", "https://www.nist.gov/publications/properties-selected-materials-cryogenic-temperatures", "nist-cryogenic-material-properties.html"),
    ("NIST-ELECTRIC-FIELD-RESPONSE", "https://www.nist.gov/publications/cavity-born-oppenheimer-approximation-molecules-and-materials-electric-field-response", "nist-electric-field-response.html"),
    ("NIST-HIGH-MAGNETIC-FIELD", "https://www.nist.gov/ncnr/sample-environment/sans-equipment/magnetic-field", "nist-high-magnetic-field.html"),
    ("NIST-SHOCKWAVE-MATERIAL-RESPONSE", "https://www.nist.gov/news-events/news/2024/10/new-polymer-technology-visualizes-shockwaves-offering-breakthroughs", "nist-shockwave-material-response.html"),
    ("NIST-RADIATION-DAMAGE-MEASUREMENT", "https://www.nist.gov/news-events/news/2024/11/nist-study-probes-damaging-effects-radiation-qubits", "nist-radiation-damage-measurement.html"),
    ("NIST-COMBINED-EXTREME-KOLSKY", "https://www.nist.gov/news-events/news/2024/03/spotlight-test-instrument-puts-materials-under-forces-high-speeds-mimic", "nist-combined-extreme-kolsky.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 8 or registry["target_content_present"] is not False:
        raise SystemExit("EXT registry changed")
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    OUT.mkdir(parents=True)
    documents = []
    for source_id, url, name in REMOTE:
        request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
        with urlopen(request, timeout=120) as response:
            body = response.read()
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "unreported")
        if status != 200 or len(body) < 1000:
            raise SystemExit(f"EXT capture halt {source_id} {status} {len(body)}")
        path = OUT / name
        path.write_bytes(body)
        documents.append({
            "source_id": source_id,
            "source_uri": url,
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_hash": digest(body),
            "byte_count": len(body),
            "http_status": status,
            "content_type": content_type,
            "status": "captured_post_registry",
            "used_for_favourable_comparison": True,
        })
    registered = {source_id for target in registry["targets"] for source_id in target["source_identities"]}
    if registered != {document["source_id"] for document in documents}:
        raise SystemExit("EXT source mismatch")
    manifest = {
        "schema": "sft-v3-materials-ext-source-custody/1",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "captured_count": len(documents),
        "unavailable_count": 0,
        "all_registered_source_identities_accounted_for": True,
        "all_result_classes_retained": True,
        "target_or_outcome_selected_source": False,
    }
    manifest["manifest_identity"] = canonical(manifest)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"documents": len(documents), "identity": manifest["manifest_identity"]}, indent=2))


if __name__ == "__main__":
    main()
