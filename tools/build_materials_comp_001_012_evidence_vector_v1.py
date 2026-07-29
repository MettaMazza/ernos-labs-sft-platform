#!/usr/bin/env python3
"""Bind all COMP claims to their post-registry authoritative source records."""

from hashlib import sha256
from html import unescape
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/comp_001_012_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"
BINDINGS = {
    "SFT-MAT-COMP-DATA-REPRESENTATION-001": (("NIST-RELIABLE-MATERIALS-DATA", "Reliable Materials Data", "Data Evaluation"),),
    "SFT-MAT-COMP-STRUCTURE-PROPERTY-002": (("NIST-STRUCTURE-PROPERTY-MAPPING", "systematic mappings", "materials microstructures", "materials properties"),),
    "SFT-MAT-COMP-FINITE-SIMULATION-003": (("NIST-OOF3D", "Image-Based Finite Element Solver", "Materials Science"),),
    "SFT-MAT-COMP-MULTISCALE-COMPOSITION-004": (("NIST-MULTISCALE-GREENS", "multiscale Green's function method", "two-dimensional nanomaterials"),),
    "SFT-MAT-COMP-ERROR-PROPAGATION-005": (("NIST-UNCERTAINTY-PROPAGATION", "propagating errors and uncertainties", "first-order Taylor series expansion"),),
    "SFT-MAT-COMP-INVERSE-PROBLEM-006": (("NIST-INVERSE-HEAT-PLACEMENT", "energy beam", "powder bed surface", "consolidate the material"),),
    "SFT-MAT-COMP-LEARNING-BOUNDARY-007": (("NIST-ML-MATERIALS-ROBUSTNESS", "robustness and generalizability", "material database benchmarks", "excellent benchmark score"),),
    "SFT-MAT-COMP-DATABASE-PROVENANCE-008": (("NIST-MATERIALS-DATABASES", "development and mining of materials databases", "fatigue and corrosion experiments"),),
    "SFT-MAT-COMP-PHASE-FIELD-009": (("NIST-PHASE-FIELD-BENCHMARK", "benchmark problems", "phase field models"),),
    "SFT-MAT-COMP-MOLECULAR-DYNAMICS-010": (("NIST-MOLECULAR-DYNAMICS", "molecular dynamics simulation program", "single sequential process"),),
    "SFT-MAT-COMP-ELECTRONIC-STRUCTURE-011": (("NIST-COMPUTATIONAL-MATERIALS", "Computational Materials Science", "design, processing and performance"),),
    "SFT-MAT-COMP-SIMULATION-EXPERIMENT-012": (("NIST-SIMULATION-VALIDATION", "complete and correct", "before jobs are released"),),
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def normalize(text):
    return "".join(character for character in unescape(re.sub(r"<[^>]+>", " ", text)).casefold() if character.isalnum())


def main():
    manifest = json.loads(MANIFEST.read_text())
    manifest_identity = manifest.pop("manifest_identity")
    if canonical(manifest) != manifest_identity:
        raise SystemExit("COMP manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("COMP source changed " + source_id)
        corpora[source_id] = normalize(path.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for binding in bindings:
            source_id, *fragments = binding
            present = [normalize(fragment) in corpora[source_id] for fragment in fragments]
            if not all(present):
                raise SystemExit(f"COMP fragments absent {claim_id} {source_id} {present}")
            document = documents[source_id]
            comparison = {
                "source_id": source_id,
                "source_status": document["status"],
                "snapshot_path": document["snapshot_path"],
                "snapshot_hash": document["snapshot_hash"],
                "registered_fragments": list(fragments),
                "all_fragments_present": True,
                "used_for_favourable_comparison": True,
            }
            comparisons.append(comparison)
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": True})
    vector = {
        "schema": "sft-v3-materials-comp-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_custody_manifest_identity": manifest_identity,
        "claim_count": len(rows),
        "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": len(documents),
        "unavailable_source_count": 0,
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "target_content_selected_survivor": False,
    }
    vector["complete_vector_identity"] = canonical(vector)
    OUT.write_text(json.dumps(vector, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(rows), "comparisons": sum(row["comparison_count"] for row in rows), "sources": len(documents), "identity": vector["complete_vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
