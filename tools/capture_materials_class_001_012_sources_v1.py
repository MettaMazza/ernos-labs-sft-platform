#!/usr/bin/env python3
"""Capture every registered authoritative CLASS source after target freeze."""
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/materials_class_001_012_target_registry_v1.json"
OUT = ROOT / "experiments/external_sources/materials/class_001_012_v1"
REMOTE = (
    ("NIST-HEA-PHASE", "https://www.nist.gov/publications/understanding-high-entropy-alloy-phase-diagram-calculation", "nist-hea-phase.html"),
    ("NIST-HEA-INTERMETALLIC", "https://www.nist.gov/publications/single-phase-l10-ordered-high-entropy-thin-films-high-magnetic-anisotropy", "nist-hea-intermetallic.html"),
    ("NIST-HIGH-TEMP-CERAMICS", "https://www.nist.gov/publications/properties-high-temperature-ceramics-and-cermets-elasticity-and-density-room", "nist-high-temperature-ceramics.html"),
    ("NIST-CEMENT-AM", "https://www.nist.gov/programs-projects/additive-manufacturing-cement-based-materials", "nist-cement-am.html"),
    ("NIST-ADVANCED-COMPOSITES", "https://www.nist.gov/programs-projects/advanced-composites-pilot-materials-genome-initiative-0", "nist-advanced-composites.html"),
    ("NIST-METALLIC-GLASS", "https://www.nist.gov/publications/ordered-metallic-glass-solid-solution-phase-grows-melt-crystal", "nist-metallic-glass.html"),
    ("NIST-CERAMIC-AM", "https://www.nist.gov/programs-projects/additive-manufacturing-ceramics", "nist-ceramic-am.html"),
    ("NIST-MACROMOLECULAR-ARCHITECTURES", "https://www.nist.gov/programs-projects/macromolecular-architectures", "nist-macromolecular-architectures.html"),
    ("NIST-THERMOSET-GLOSSARY", "https://www.nist.gov/glossary-term/33531", "nist-thermoset-glossary.html"),
    ("NIST-AMMT-GRADED", "https://www.nist.gov/el/ammt", "nist-ammt-graded.html"),
    ("NIST-AUXETIC-ARCHITECTED", "https://www.nist.gov/news-events/news/2024/05/new-way-designing-auxetic-materials", "nist-auxetic-architected.html"),
)

def digest(data):
    return "sha256:" + sha256(data).hexdigest()

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def main():
    registry_bytes = REGISTRY.read_bytes()
    registry = json.loads(registry_bytes)
    if registry["target_count"] != 12 or registry["target_content_present"] is not False:
        raise SystemExit("CLASS registry changed")
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
            raise SystemExit(f"CLASS capture halt {source_id} {status} {len(body)}")
        path = OUT / filename
        path.write_bytes(body)
        documents.append({"source_id": source_id, "source_uri": source_uri, "snapshot_path": path.relative_to(ROOT).as_posix(), "snapshot_hash": digest(body), "byte_count": len(body), "http_status": status, "content_type": content_type, "status": "captured_post_registry", "used_for_favourable_comparison": True})
    registered = {source for target in registry["targets"] for source in target["source_identities"]}
    captured = {document["source_id"] for document in documents}
    if registered != captured:
        raise SystemExit("CLASS source mismatch")
    payload = {"schema": "sft-v3-materials-class-source-custody/1", "target_registry_path": REGISTRY.relative_to(ROOT).as_posix(), "target_registry_hash": digest(registry_bytes), "target_registry_identity": registry["registry_identity"], "documents": documents, "document_count": len(documents), "captured_count": len(documents), "unavailable_count": 0, "all_registered_source_identities_accounted_for": True, "all_result_classes_retained": True, "target_or_outcome_selected_source": False}
    payload["manifest_identity"] = canonical(payload)
    (OUT / "source_custody_manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"documents": len(documents), "identity": payload["manifest_identity"]}, indent=2))

if __name__ == "__main__":
    main()
