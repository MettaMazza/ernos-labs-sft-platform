#!/usr/bin/env python3
"""Capture all registered PROC sources after the target registry is sealed."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_proc_001_010_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/proc_001_010_v1"
REMOTE = (
    ("NIST-MOULD-FILLING", "https://www.nist.gov/publications/minimalist-sensor-system-mold-filling", "nist-mould-filling.html"),
    ("NIST-CRYSTALLOGRAPHIC-TEXTURE", "https://www.nist.gov/publications/measurement-axisymmetric-crystallographic-texture", "nist-crystallographic-texture.html"),
    ("NIST-SUBSURFACE-DAMAGE", "https://www.nist.gov/publications/recommendation-inspection-standard-control-sub-surface-damage-single-crystal-sapphire", "nist-subsurface-damage.html"),
    ("NIST-MELT-POOL-COOLING", "https://www.nist.gov/publications/using-coaxial-melt-pool-monitoring-images-estimate-cooling-rate-powder-bed-fusion", "nist-melt-pool-cooling.html"),
    ("NIST-PULSED-LASER-DEPOSITION", "https://www.nist.gov/publications/pulsed-laser-deposition-and-characterization-hf-based-high-k-dielectric-thin-films", "nist-pulsed-laser-deposition.html"),
    ("NIST-NANOWIRE-LATTICE-MATCH", "https://www.nist.gov/publications/where-required-lattice-match-horizontal-growth-nanowires", "nist-nanowire-lattice-match.html"),
    ("NIST-WELD-MONITORING", "https://www.nist.gov/publications/analysis-welding-parameter-distribution-stud-arc-welding", "nist-weld-monitoring.html"),
    ("NIST-POLYMER-ORIENTATION", "https://www.nist.gov/publications/three-dimensional-molecular-orientation-imaging-semicrystalline-polymer-film-under", "nist-polymer-orientation.html"),
    ("NIST-POWDER-COMPACTION", "https://www.nist.gov/publications/low-temperature-compaction-nanosize-powders", "nist-powder-compaction.html"),
    ("NIST-REPRODUCIBLE-PROCESS-MONITORING", "https://www.nist.gov/publications/towards-reproducible-machine-learning-based-process-monitoring-and-quality-prediction", "nist-reproducible-process-monitoring.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 10 or registry["target_content_present"] is not False:
        raise SystemExit("PROC registry changed")
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
            raise SystemExit(f"PROC capture halt {source_id} {status} {len(body)}")
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
        raise SystemExit("PROC source mismatch")
    manifest = {
        "schema": "sft-v3-materials-proc-source-custody/1",
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
