#!/usr/bin/env python3
"""Capture all registered NANO sources after the target registry is sealed."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_nano_001_010_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/nano_001_010_v1"
REMOTE = (
    ("NIST-NANOPARTICLE-SIZE-SHAPE", "https://www.nist.gov/news-events/news/2016/12/how-tell-when-nanoparticle-out-shape", "nist-nanoparticle-size-shape.html"),
    ("NIST-GAN-NANOWIRE-GROWTH", "https://www.nist.gov/programs-projects/gan-nanowire-growth", "nist-gan-nanowire-growth.html"),
    ("NIST-QUANTUM-TRANSPORT-2D-STACKING", "https://www.nist.gov/programs-projects/quantum-transport-measurements", "nist-quantum-transport-2d-stacking.html"),
    ("NIST-NANOWORLD-QUANTUM-DOTS", "https://www.nist.gov/programs-projects/designing-nanoworld-nanostructure-nanodevices-and-nano-optics", "nist-nanoworld-quantum-dots.html"),
    ("NIST-NANOPARTICLE-SURFACE-AREA", "https://www.nist.gov/programs-projects/assessing-environmental-health-and-safety-impact-nanoparticles", "nist-nanoparticle-surface-area.html"),
    ("NIST-NANOCONFINED-FUSION", "https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=926717", "nist-nanoconfined-fusion.pdf"),
    ("NIST-MOIRE-QUANTUM-PHASES", "https://www.nist.gov/programs-projects/moire-systems", "nist-moire-quantum-phases.html"),
    ("NIST-MOIRE-EXCITONS", "https://www.nist.gov/publications/evidence-moire-excitons-van-der-waals-heterostructures", "nist-moire-excitons.html"),
    ("NIST-NANOCOMPOSITE-INTERFACIAL-LAYER", "https://www.nist.gov/publications/understanding-static-interfacial-polymer-layer-exploring-dispersion-states", "nist-nanocomposite-interfacial-layer.html"),
    ("NIST-NANOPARTICLE-AGGREGATION-DISPERSION", "https://www.nist.gov/publications/electrospray-differential-mobility-hyphenated-single-particle-mass-spectrometry", "nist-nanoparticle-aggregation-dispersion.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 10 or registry["target_content_present"] is not False:
        raise SystemExit("NANO registry changed")
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
            raise SystemExit(f"NANO capture halt {source_id} {status} {len(body)}")
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
        raise SystemExit("NANO source mismatch")
    manifest = {
        "schema": "sft-v3-materials-nano-source-custody/1",
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

