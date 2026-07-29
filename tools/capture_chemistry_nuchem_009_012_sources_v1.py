#!/usr/bin/env python3
"""Capture the complete NUCHEM-009–012 sources once after all four seals."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "experiments/external_sources/chemistry/snapshots/nuchem-009-012-radiochemistry-v1"
INVENTORY = SNAP / "source-inventory-v1.json"
REGISTRY = ROOT / "experiments/external_sources/chemistry/nuchem_009_012_family_source_identity_registry_v1.json"
EXPECTED_REGISTRY = "sha256:ff9ae4d8616b9e5889028876f217e5d0c356d30fa146dd2b5ae90cb2bab06628"
SOURCES = (
    ("IAEA-TCS-31-RADIOTRACER-RTD-2008", "International Atomic Energy Agency", "https://www-pub.iaea.org/MTCD/publications/PDF/TCS-31_web.pdf", "iaea-tcs31-radiotracer-rtd-2008.pdf"),
    ("DOE-OSTI-1580278-HFSLM-ISOTOPE-HARVESTING", "United States Department of Energy Office of Scientific and Technical Information", "https://www.osti.gov/servlets/purl/1580278", "doe-osti-1580278-isotope-harvesting-hfslm.pdf"),
    ("DOE-ORNL-4865-FISSION-PRODUCT-BEHAVIOR-MSRE", "United States Department of Energy / Oak Ridge National Laboratory", "https://www.osti.gov/servlets/purl/4077644", "doe-ornl-4865-fission-product-behavior-msre.pdf"),
    ("NBS-NSRDS-45-RADIATION-CHEMISTRY-NITROUS-OXIDE", "National Bureau of Standards", "https://nvlpubs.nist.gov/nistpubs/Legacy/NSRDS/nbsnsrds45.pdf", "nbs-nsrds45-radiation-chemistry-nitrous-oxide.pdf"),
)
SEALS = {
    "009": ("experiments/sealed_predictions/chemistry_nuchem_009_pre_source_v1.json", "sha256:73cf904a4d34bbb7dfd0ffe7b52ed3e15c04cc32dac68d631f7c9ab4d3eade29"),
    "010": ("experiments/sealed_predictions/chemistry_nuchem_010_pre_source_v1.json", "sha256:7b4467b104dc19d96d2ce5e56e7ce84ad4dfeec22b7d2f9cd19a18f8681e30cc"),
    "011": ("experiments/sealed_predictions/chemistry_nuchem_011_pre_source_v1.json", "sha256:81482cf2d5aeb17080fdc5f69780838b7ac3910748ac27cf9bf21d0ae96ea204"),
    "012": ("experiments/sealed_predictions/chemistry_nuchem_012_pre_source_v1.json", "sha256:b180a00808ac40571ea6f07b4d7f0a9d6e6d873ded4218431d5ac024fa0454c1"),
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if INVENTORY.exists(): raise SystemExit("NUCHEM-009–012 source inventory already exists; recapture prohibited")
    if digest(REGISTRY.read_bytes()) != EXPECTED_REGISTRY: raise SystemExit("NUCHEM-009–012 source registry changed")
    for key, (path, expected) in SEALS.items():
        if digest((ROOT / path).read_bytes()) != expected: raise SystemExit(f"NUCHEM-{key} seal changed")
    SNAP.mkdir(parents=True, exist_ok=False)
    rows = []
    for source_id, authority, uri, name in SOURCES:
        request = Request(uri, headers={"User-Agent": "Ernos-Labs-SFT-Empirical-Capture/1.0"})
        with urlopen(request, timeout=120) as response:
            payload = response.read(); content_type = response.headers.get("Content-Type", "")
        if not payload.startswith(b"%PDF-"): raise SystemExit(f"registered source was not a PDF: {source_id}")
        path = SNAP / name; path.write_bytes(payload)
        rows.append({"source_id": source_id, "authority": authority, "uri": uri, "capture_status": "captured_once_after_all_four_claim_seals", "content_type": content_type, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_sha256": digest(payload), "snapshot_bytes": len(payload)})
        print(source_id, len(payload), digest(payload))
    inventory = {
        "schema": "sft-v3-chemistry-nuchem-009-012-source-inventory/1", "family": "NUCHEM-009-012",
        "all_four_claims_sealed_separately_before_complete_family_capture": True,
        "prior_source_exposure_disclosures_preserved_in_each_seal": True,
        "sealed_claims": [{"claim": key, "seal_sha256": expected} for key, (_, expected) in SEALS.items()], "rows": rows,
    }
    INVENTORY.write_text(json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    print("inventory", digest(INVENTORY.read_bytes()))


if __name__ == "__main__": main()
