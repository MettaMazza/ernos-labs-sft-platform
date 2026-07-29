#!/usr/bin/env python3
"""Capture the complete official Materials CRYS-001--008 source family after registry freeze."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_crys_001_008_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/crys_001_008_v1"


SOURCES = (
    ("NIST-SP846-POWDER-DIFFRACTION-1992", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication846.pdf", "nist-sp846-powder-diffraction.pdf"),
    ("NIST-TOTAL-SCATTERING-PDF-2014", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914719", "nist-total-scattering-pdf-2014.pdf"),
    ("IUCR-MODULATION-WAVE-DIFFUSE-2015", "https://journals.iucr.org/m/issues/2015/01/00/gq5002/index.html", "iucr-modulation-wave-diffuse-2015.html"),
    ("IUCR-STACKING-DIFFUSE-2023", "https://journals.iucr.org/b/issues/2023/02/00/je5050/index.html", "iucr-stacking-diffuse-2023.html"),
    ("IUCR-STACKING-FAULT-LDH-2020", "https://journals.iucr.org/j/issues/2020/01/00/po5156/index.html", "iucr-stacking-fault-ldh-2020.html"),
    ("IUCR-TWINNED-DIFFRACTION-DATA-2022", "https://iucrdata.iucr.org/x/issues/2022/09/00/he4557/index.html", "iucr-twinned-diffraction-data-2022.html"),
    ("IUCR-TWIN-DICTIONARY-2026", "https://dictionary.iucr.org/Twin_%28diffraction_pattern_of%29", "iucr-twin-dictionary-2026.html"),
    ("IUCR-MODULATED-STRUCTURES-2009", "https://journals.iucr.org/b/issues/2009/03/00/bk5084/index.html", "iucr-modulated-structures-2009.html"),
    ("IUCR-INCOMMENSURATE-DICTIONARY-2026", "https://dictionary.iucr.org/Incommensurate_modulated_structure", "iucr-incommensurate-dictionary-2026.html"),
)


def digest(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(request, timeout=90) as response:
        return response.read()


def main() -> None:
    registry = json.loads(REGISTRY.read_text())
    if registry.get("target_content_present") is not False or registry.get("target_count") != 8:
        raise SystemExit("CRYS source capture halted: target registry is not value-free and complete")
    OUT.mkdir(parents=True, exist_ok=True)
    captured = []
    for source_id, uri, filename in SOURCES:
        path = OUT / filename
        body = get(uri)
        if len(body) < 1000:
            raise SystemExit(f"CRYS source capture halted: implausibly short response for {source_id}")
        path.write_bytes(body)
        captured.append({
            "source_id": source_id,
            "source_uri": uri,
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_hash": digest(path),
            "byte_count": len(body),
        })

    existing = ROOT / "experiments/external_sources/materials/snapshots/nist-texture-phase-fraction.html"
    if not existing.is_file():
        raise SystemExit("CRYS source capture halted: registered NIST texture snapshot absent")
    captured.append({
        "source_id": "NIST-NCAL-TEXTURE-PHASE-FRACTION-2026",
        "source_uri": "https://www.nist.gov/programs-projects/ncal-quantifying-crystallographic-texture-and-phase-fraction",
        "snapshot_path": existing.relative_to(ROOT).as_posix(),
        "snapshot_hash": digest(existing),
        "byte_count": existing.stat().st_size,
    })
    manifest = {
        "schema": "sft-v3-materials-crys-source-custody/1",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest(REGISTRY),
        "target_registry_identity": registry["registry_identity"],
        "documents": captured,
        "document_count": len(captured),
        "all_registered_source_identities_captured": True,
        "all_outcomes_retained": True,
    }
    manifest["manifest_identity"] = "sha256:" + sha256(json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    (OUT / "source_custody_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(captured), "manifest_identity": manifest["manifest_identity"], "bytes": sum(x["byte_count"] for x in captured)}, indent=2))


if __name__ == "__main__":
    main()
