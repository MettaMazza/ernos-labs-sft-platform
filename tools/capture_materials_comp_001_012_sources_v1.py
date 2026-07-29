#!/usr/bin/env python3
"""Capture all registered COMP sources after the target registry is sealed."""

from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_comp_001_012_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/comp_001_012_v1"
REMOTE = (
    ("NIST-RELIABLE-MATERIALS-DATA", "https://www.nist.gov/publications/reliable-materials-data-whys-and-wherefores-data-evaluation", "nist-reliable-materials-data.html"),
    ("NIST-STRUCTURE-PROPERTY-MAPPING", "https://www.nist.gov/publications/active-learning-regression-structure-property-mapping-importance-sampling-and", "nist-structure-property-mapping.html"),
    ("NIST-OOF3D", "https://www.nist.gov/publications/oof3d-image-based-finite-element-solver-materials-science", "nist-oof3d.html"),
    ("NIST-MULTISCALE-GREENS", "https://www.nist.gov/publications/multiscale-greens-functions-modeling-graphene-and-other-xenes", "nist-multiscale-greens.html"),
    ("NIST-UNCERTAINTY-PROPAGATION", "https://www.nist.gov/publications/higher-order-corrections-propagating-uncertainties", "nist-uncertainty-propagation.html"),
    ("NIST-INVERSE-HEAT-PLACEMENT", "https://www.nist.gov/publications/inverse-heat-placement-problem-metal-additive-manufacturing-why-rational-approach", "nist-inverse-heat-placement.html"),
    ("NIST-ML-MATERIALS-ROBUSTNESS", "https://www.nist.gov/publications/critical-examination-robustness-and-generalizability-machine-learning-prediction", "nist-ml-materials-robustness.html"),
    ("NIST-MATERIALS-DATABASES", "https://www.nist.gov/publications/developing-and-mining-materials-databases-corrosion-and-fatigue-data", "nist-materials-databases.html"),
    ("NIST-PHASE-FIELD-BENCHMARK", "https://www.nist.gov/publications/phase-field-benchmark-problems-dendritic-growth-and-linear-elasticity", "nist-phase-field-benchmark.html"),
    ("NIST-MOLECULAR-DYNAMICS", "https://www.nist.gov/publications/parallel-implementation-molecular-dynamics-simulation-program", "nist-molecular-dynamics.html"),
    ("NIST-COMPUTATIONAL-MATERIALS", "https://www.nist.gov/publications/computational-materials-science-and-industrial-rd-accelerating-progress", "nist-computational-materials.html"),
    ("NIST-SIMULATION-VALIDATION", "https://www.nist.gov/publications/manufacturing-data-validation-through-simulation", "nist-simulation-validation.html"),
)


def digest(body):
    return "sha256:" + sha256(body).hexdigest()


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 12 or registry["target_content_present"] is not False:
        raise SystemExit("COMP registry changed")
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
            raise SystemExit(f"COMP capture halt {source_id} {status} {len(body)}")
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
        raise SystemExit("COMP source mismatch")
    manifest = {
        "schema": "sft-v3-materials-comp-source-custody/1",
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
