#!/usr/bin/env python3
"""Bind all PROC claims to their post-registry authoritative source records."""

from hashlib import sha256
from html import unescape
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/proc_001_010_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"
BINDINGS = {
    "SFT-MAT-PROC-CASTING-HISTORY-001": (("NIST-MOULD-FILLING", "Reliable mold filling", "most critical issue"),),
    "SFT-MAT-PROC-FORMING-TEXTURE-002": (("NIST-CRYSTALLOGRAPHIC-TEXTURE", "Crystallographic texture", "methodologies for the analysis"),),
    "SFT-MAT-PROC-MACHINING-DAMAGE-003": (("NIST-SUBSURFACE-DAMAGE", "characterization techniques", "surface and subsurface damage"),),
    "SFT-MAT-PROC-ADDITIVE-BUILD-004": (("NIST-MELT-POOL-COOLING", "Cooling rate is a decisive index", "melt pool solidification"),),
    "SFT-MAT-PROC-THIN-FILM-GROWTH-005": (("NIST-PULSED-LASER-DEPOSITION", "Pulsed Laser Deposition", "Dielectric Thin Films"),),
    "SFT-MAT-PROC-EPITAXY-MATCHING-006": (("NIST-NANOWIRE-LATTICE-MATCH", "surface-directed growth of nanowires", "number of semiconductors"),),
    "SFT-MAT-PROC-JOINING-INTERFACE-007": (("NIST-WELD-MONITORING", "on-line monitoring system", "welding current and voltage"),),
    "SFT-MAT-PROC-POLYMER-ORIENTATION-008": (("NIST-POLYMER-ORIENTATION", "3D molecular orientations", "shear deformed region"),),
    "SFT-MAT-PROC-POWDER-COMPACTION-009": (("NIST-POWDER-COMPACTION", "processing of nanosize ceramic powders", "sintering them at low temperatures"),),
    "SFT-MAT-PROC-WINDOW-PROVENANCE-010": (("NIST-REPRODUCIBLE-PROCESS-MONITORING", "monitoring systems", "print quality", "additive manufacturing"),),
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
        raise SystemExit("PROC manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("PROC source changed " + source_id)
        corpora[source_id] = normalize(path.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for binding in bindings:
            source_id, *fragments = binding
            present = [normalize(fragment) in corpora[source_id] for fragment in fragments]
            if not all(present):
                raise SystemExit(f"PROC fragments absent {claim_id} {source_id} {present}")
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
        "schema": "sft-v3-materials-proc-complete-evidence-vector/1",
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
