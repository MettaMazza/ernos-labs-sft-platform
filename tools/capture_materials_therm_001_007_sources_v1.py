#!/usr/bin/env python3
"""Capture the complete preregistered Materials THERM source set."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "census/materials_therm_001_007_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/therm_001_007_v1"

REMOTE = (
    ("NIST-MATERIALS-DATA-GUIDE", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication960-11.pdf", "nist-materials-data-guide.pdf"),
    ("NIST-THERMAL-DIFFUSIVITY-AM", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=924024", "nist-thermal-diffusivity-am.pdf"),
    ("NIST-FDTR-TRANSPORT", "https://www.nist.gov/programs-projects/transport-property-measurements-semiconductors-and-energy-materials", "nist-fdtr-transport.html"),
    ("NIST-INTERFACE-SCATTERING", "https://www.nist.gov/publications/interface-scattering-polycrystalline-thermoelectrics", "nist-interface-scattering.html"),
    ("NIST-INFRARED-OPTICAL-PROPERTIES", "https://www.nist.gov/programs-projects/infrared-optical-properties-materials-and-components", "nist-infrared-optical-properties.html"),
    ("NIST-THERMOELECTRIC-MEASUREMENTS", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=956623", "nist-thermoelectric-measurements.pdf"),
    ("NIST-PHASE-CHANGE-STORAGE", "https://www.nist.gov/programs-projects/phase-change-material-thermal-energy-storage-hvacr-systems-utility-load-balancing", "nist-phase-change-storage.html"),
    ("NIST-NANOCALORIMETRY", "https://www.nist.gov/programs-projects/nanocalorimetry-measurements", "nist-nanocalorimetry.html"),
    ("NIST-FRACTOGRAPHY-THERMAL-SHOCK", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=920070", "nist-fractography-thermal-shock.pdf"),
    ("NIST-THERMAL-SHOCK-SILICON-NITRIDE", "https://www.nist.gov/publications/thermal-shock-resistance-silicon-nitrides-using-indentation-quench-test", "nist-thermal-shock-silicon-nitride.html"),
)
EXISTING = (
    ("NIST-PHONON-THERMAL-LIMITS", "https://nvlpubs.nist.gov/nistpubs/Legacy/NSRDS/nbsnsrds8.pdf", "experiments/external_sources/materials/snapshots/nist-phonon-thermal-limits-2026-07-27.pdf"),
    ("NIST-TRANSPORT-THERMOELECTRIC", "https://www.nist.gov/programs-projects/transport-property-measurements-semiconductors-and-energy-materials", "experiments/external_sources/materials/snapshots/nist-transport-thermoelectric.html"),
)

def digest(body):
    return "sha256:" + sha256(body).hexdigest()

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    registry_bytes = REG.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 7 or registry["target_content_present"] is not False:
        raise SystemExit("THERM capture halted: target registry changed")
    if OUT.exists():
        raise SystemExit("refusing to overwrite THERM source custody")
    OUT.mkdir(parents=True)
    documents = []
    for source_id, uri, name in REMOTE:
        request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
        with urlopen(request, timeout=120) as response:
            body = response.read()
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "unreported")
        if status != 200 or len(body) < 1000:
            raise SystemExit(f"THERM capture halted: {source_id} {status} {len(body)}")
        path = OUT / name
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": digest(body), "byte_count": len(body), "http_status": status, "content_type": content_type, "status": "captured_post_registry", "used_for_favourable_comparison": True})
    for source_id, uri, relative in EXISTING:
        path = ROOT / relative
        body = path.read_bytes()
        documents.append({"source_id": source_id, "source_uri": uri, "snapshot_path": relative, "snapshot_hash": digest(body), "byte_count": len(body), "http_status": "preexisting", "content_type": "preserved-official-snapshot", "status": "captured_preexisting_official_snapshot", "used_for_favourable_comparison": True})
    registered = {source for target in registry["targets"] for source in target["source_identities"]}
    captured = {row["source_id"] for row in documents}
    if registered != captured:
        raise SystemExit(f"THERM source mismatch: missing={registered-captured}; extra={captured-registered}")
    payload = {
        "schema": "sft-v3-materials-therm-source-custody/1",
        "target_registry_path": REG.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "captured_count": len(documents),
        "unavailable_count": 0,
        "all_registered_source_identities_accounted_for": True,
        "all_result_classes_retained": True,
    }
    payload["manifest_identity"] = canonical(payload)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "manifest_identity": payload["manifest_identity"]}, indent=2))

if __name__ == "__main__":
    main()
