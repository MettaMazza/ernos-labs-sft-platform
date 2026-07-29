#!/usr/bin/env python3
"""Capture every registered authoritative OPT source after the target freeze."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_opt_001_010_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/opt_001_010_v1"
REMOTE = (
    ("NIST-SPECTROPHOTOMETRY", "https://www.nist.gov/programs-projects/spectrophotometry", "nist-spectrophotometry.html"),
    ("NIST-OPTICAL-SCATTERING", "https://www.nist.gov/pml/sensor-science/optical-properties-materials", "nist-optical-properties-materials.html"),
    ("NIST-FLUORESCENCE-RAMAN", "https://www.nist.gov/programs-projects/relative-intensity-correction-standards-fluorescence-and-raman-spectroscopy", "nist-fluorescence-raman.html"),
    ("NIST-BIREFRINGENCE", "https://www.nist.gov/programs-projects/birefringence-properties-optical-materials-012-mm-2-mm", "nist-birefringence.html"),
    ("NIST-NONLINEAR-MIXING", "https://www.nist.gov/publications/mixing-polarization-states-zincblende-nonlinear-optical-crystals", "nist-nonlinear-mixing.html"),
    ("NIST-WAVEGUIDE-LOSS", "https://www.nist.gov/publications/measurement-small-birefringence-and-loss-nonlinear-single-mode-waveguide", "nist-waveguide-loss.html"),
    ("NIST-PHOTONIC-BANDGAP", "https://www.nist.gov/news-events/news/2024/06/some-bumps-nist-scientists-devise-novel-way-extend-wavelength-range", "nist-photonic-bandgap.html"),
    ("NIST-PLASMONIC-MODES", "https://www.nist.gov/publications/nanoscale-imaging-and-spectroscopy-plasmonic-modes-ptir-technique", "nist-plasmonic-modes.html"),
    ("NIST-EXCITON-DYNAMICS", "https://www.nist.gov/publications/exciton-dynamics-monolayer-transition-metal-michalcogenides", "nist-exciton-dynamics.html"),
    ("NIST-CARRIER-DYNAMICS", "https://www.nist.gov/programs-projects/carrier-dynamics-measured-ultrafast-time-resolved-terahertz-spectroscopy", "nist-carrier-dynamics.html"),
)

def digest(data):
    return "sha256:" + sha256(data).hexdigest()

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 10 or registry["target_content_present"] is not False:
        raise SystemExit("OPT registry changed")
    if OUT.exists():
        raise SystemExit("refusing overwrite")
    OUT.mkdir(parents=True)
    documents = []
    for source_id, source_uri, filename in REMOTE:
        with urlopen(Request(source_uri, headers={"User-Agent": "Ernos-Labs-SFT/3 (mailto:Maria.Smith.Sftoe@gmail.com)"}), timeout=120) as response:
            body = response.read()
            status = getattr(response, "status", 200)
            content_type = response.headers.get("Content-Type", "unreported")
        if status != 200 or len(body) < 1000:
            raise SystemExit(f"OPT capture halt {source_id} {status} {len(body)}")
        path = OUT / filename
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": source_uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": digest(body), "byte_count": len(body), "http_status": status, "content_type": content_type, "status": "captured_post_registry", "used_for_favourable_comparison": True})
    registered = {source for target in registry["targets"] for source in target["source_identities"]}
    captured = {document["source_id"] for document in documents}
    if registered != captured:
        raise SystemExit("OPT source mismatch")
    payload = {"schema": "sft-v3-materials-opt-source-custody/1", "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(), "target_registry_hash": digest(registry_bytes), "target_registry_identity": registry["registry_identity"], "documents": documents, "document_count": len(documents), "captured_count": len(documents), "unavailable_count": 0, "all_registered_source_identities_accounted_for": True, "all_result_classes_retained": True}
    payload["manifest_identity"] = canonical(payload)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"documents": len(documents), "identity": payload["manifest_identity"]}, indent=2))

if __name__ == "__main__":
    main()
