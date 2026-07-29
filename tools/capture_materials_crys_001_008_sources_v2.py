#!/usr/bin/env python3
"""Retry the frozen CRYS source capture through a disclosed read-only text proxy."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_crys_001_008_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/crys_001_008_v2"
JINA = "https://r.jina.ai/http://"


SOURCES = (
    ("NIST-SP846-POWDER-DIFFRACTION-1992", "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication846.pdf", "nist-sp846-powder-diffraction.pdf", False),
    ("NIST-TOTAL-SCATTERING-PDF-2014", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=914719", "nist-total-scattering-pdf-2014.pdf", False),
    ("IUCR-MODULATION-WAVE-DIFFUSE-2015", "http://journals.iucr.org/m/issues/2015/01/00/gq5002/index.html", "iucr-modulation-wave-diffuse-2015.md", True),
    ("IUCR-STACKING-DIFFUSE-2023", "http://journals.iucr.org/b/issues/2023/02/00/je5050/index.html", "iucr-stacking-diffuse-2023.md", True),
    ("IUCR-STACKING-FAULT-LDH-2020", "http://journals.iucr.org/j/issues/2020/01/00/po5156/index.html", "iucr-stacking-fault-ldh-2020.md", True),
    ("IUCR-TWINNED-DIFFRACTION-DATA-2022", "http://iucrdata.iucr.org/x/issues/2022/09/00/he4557/index.html", "iucr-twinned-diffraction-data-2022.md", True),
    ("IUCR-TWIN-DICTIONARY-2026", "http://dictionary.iucr.org/Twin_%28diffraction_pattern_of%29", "iucr-twin-dictionary-2026.md", True),
    ("IUCR-MODULATED-STRUCTURES-2009", "http://journals.iucr.org/b/issues/2009/03/00/bk5084/index.html", "iucr-modulated-structures-2009.md", True),
    ("IUCR-INCOMMENSURATE-DICTIONARY-2026", "http://dictionary.iucr.org/Incommensurate_modulated_structure", "iucr-incommensurate-dictionary-2026.md", True),
)


def digest_bytes(body: bytes) -> str:
    return "sha256:" + sha256(body).hexdigest()


def get(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"})
    with urlopen(request, timeout=120) as response:
        return response.read()


def main() -> None:
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry.get("target_content_present") is not False or registry.get("target_count") != 8:
        raise SystemExit("CRYS source capture halted: target registry is not value-free and complete")
    OUT.mkdir(parents=True, exist_ok=True)
    documents = []
    for source_id, official_uri, filename, proxied in SOURCES:
        capture_uri = JINA + official_uri.removeprefix("http://") if proxied else official_uri
        body = get(capture_uri)
        if len(body) < 1000:
            raise SystemExit(f"CRYS source capture halted: implausibly short response for {source_id}")
        path = OUT / filename
        path.write_bytes(body)
        documents.append({
            "source_id": source_id,
            "official_source_uri": official_uri.replace("http://", "https://", 1),
            "capture_transport_uri": capture_uri,
            "transport_disclosure": "read-only text proxy of named official source" if proxied else "direct official-source download",
            "snapshot_path": path.relative_to(ROOT).as_posix(),
            "snapshot_hash": digest_bytes(body),
            "byte_count": len(body),
        })
    texture = ROOT / "experiments/external_sources/materials/snapshots/nist-texture-phase-fraction.html"
    body = texture.read_bytes()
    documents.append({
        "source_id": "NIST-NCAL-TEXTURE-PHASE-FRACTION-2026",
        "official_source_uri": "https://www.nist.gov/programs-projects/ncal-quantifying-crystallographic-texture-and-phase-fraction",
        "capture_transport_uri": "pre-existing direct official-source snapshot",
        "transport_disclosure": "direct official-source download retained before this family",
        "snapshot_path": texture.relative_to(ROOT).as_posix(),
        "snapshot_hash": digest_bytes(body),
        "byte_count": len(body),
    })
    manifest = {
        "schema": "sft-v3-materials-crys-source-custody/2",
        "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(),
        "target_registry_hash": digest_bytes(registry_bytes),
        "target_registry_identity": registry["registry_identity"],
        "documents": documents,
        "document_count": len(documents),
        "all_registered_source_identities_captured": True,
        "all_favourable_adverse_absent_unresolved_rows_retained": True,
        "direct_capture_halt_preserved": "audits/MATERIALS_CRYS_001_008_DIRECT_SOURCE_CAPTURE_HALT_2026-07-29.json",
    }
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    manifest["manifest_identity"] = "sha256:" + sha256(body).hexdigest()
    (OUT / "source_custody_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"document_count": len(documents), "manifest_identity": manifest["manifest_identity"], "bytes": sum(x["byte_count"] for x in documents)}, indent=2))


if __name__ == "__main__":
    main()
