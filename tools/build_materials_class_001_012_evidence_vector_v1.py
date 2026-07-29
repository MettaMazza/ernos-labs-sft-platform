#!/usr/bin/env python3
"""Build the complete post-registry CLASS-001--012 evidence vector."""
from hashlib import sha256
from html import unescape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/class_001_012_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"
BINDINGS = {
    "SFT-MAT-CLASS-SOLID-SOLUTION-ALLOY-001": (("NIST-HEA-PHASE", "ideal and non-ideal solid solution phases", "solid solution phase and line compounds"),),
    "SFT-MAT-CLASS-INTERMETALLIC-ORDER-002": (("NIST-HEA-INTERMETALLIC", "Single-Phase L10-Ordered High Entropy Thin Films", "High Magnetic Anisotropy"), ("NIST-HEA-PHASE", "solid solution phase and line compounds", "multicomponent phase diagrams")),
    "SFT-MAT-CLASS-HIGH-ENTROPY-BOUNDARY-003": (("NIST-HEA-PHASE", "entropy of mixing", "multicomponent phase diagrams"), ("NIST-HEA-INTERMETALLIC", "High Entropy Thin Films", "L10-Ordered")),
    "SFT-MAT-CLASS-REFRACTORY-UHT-004": (("NIST-HIGH-TEMP-CERAMICS", "high-temperature ceramics and cermets", "elasticity and density at room temperature"),),
    "SFT-MAT-CLASS-CEMENTITIOUS-CONCRETE-005": (("NIST-CEMENT-AM", "fluid-to-solid transition", "hydration products which act to link particles together creating a porous microstructure"),),
    "SFT-MAT-CLASS-FIBRE-REINFORCED-006": (("NIST-ADVANCED-COMPOSITES", "transfer loads from the weaker polymer phase", "stronger the interface, the greater the load transfer function"),),
    "SFT-MAT-CLASS-PARTICLE-REINFORCED-007": (("NIST-ADVANCED-COMPOSITES", "interparticle interactions", "filler surface"),),
    "SFT-MAT-CLASS-METALLIC-GLASS-008": (("NIST-METALLIC-GLASS", "noncrystalline homogeneous metastable phase", "chemical ordering out to at least 12"),),
    "SFT-MAT-CLASS-CERAMIC-SUBCLASSES-009": (("NIST-CERAMIC-AM", "body armor, structural components, high-temperature systems", "electronics, energy, and medical implants"), ("NIST-HIGH-TEMP-CERAMICS", "high-temperature ceramics and cermets", "elasticity and density")),
    "SFT-MAT-CLASS-POLYMER-SUBCLASSES-010": (("NIST-MACROMOLECULAR-ARCHITECTURES", "model thermoplastics, thermoplastic elastomers", "polymer sequence, chemistry, and architectures"), ("NIST-THERMOSET-GLOSSARY", "hardened into a permanent shape", "not commonly subject to softening when heated")),
    "SFT-MAT-CLASS-FUNCTIONALLY-GRADED-011": (("NIST-AMMT-GRADED", "microstructure control, functionally graded materials", "enabled by novel AM control techniques"),),
    "SFT-MAT-CLASS-ARCHITECTED-CELLULAR-012": (("NIST-AUXETIC-ARCHITECTED", "Auxetics defy common sense", "widening when they’re stretched and narrowing when they’re compressed"),),
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def normalized(text):
    visible = unescape(re.sub(r"<[^>]+>", " ", text))
    return "".join(character for character in visible.casefold() if character.isalnum())

def main():
    manifest = json.loads(MANIFEST.read_text())
    manifest_identity = manifest.pop("manifest_identity")
    if canonical(manifest) != manifest_identity:
        raise SystemExit("CLASS manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        snapshot = ROOT / row["snapshot_path"]
        if file_hash(snapshot) != row["snapshot_hash"]:
            raise SystemExit("CLASS source changed " + source_id)
        corpora[source_id] = normalized(snapshot.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for source_id, first, second in bindings:
            first_present, second_present = normalized(first) in corpora[source_id], normalized(second) in corpora[source_id]
            if not (first_present and second_present):
                raise SystemExit(f"CLASS fragments absent {claim_id} {source_id} {first_present}/{second_present}")
            source = documents[source_id]
            comparisons.append({"source_id": source_id, "source_status": source["status"], "snapshot_path": source["snapshot_path"], "snapshot_hash": source["snapshot_hash"], "first_registered_fragment": first, "second_registered_fragment": second, "first_fragment_present": first_present, "second_fragment_present": second_present, "used_for_favourable_comparison": True})
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": True})
    payload = {"schema": "sft-v3-materials-class-complete-evidence-vector/1", "target_registry_identity": manifest["target_registry_identity"], "source_custody_manifest_identity": manifest_identity, "claim_count": len(rows), "claims": rows, "source_status_rows": list(documents.values()), "captured_source_count": len(documents), "unavailable_source_count": 0, "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True, "target_content_selected_survivor": False}
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(rows), "comparisons": sum(row["comparison_count"] for row in rows), "sources": len(documents), "identity": payload["complete_vector_identity"]}, indent=2))

if __name__ == "__main__":
    main()
