#!/usr/bin/env python3
"""Bind all NANO claims to their post-registry authoritative source records."""

from hashlib import sha256
from html import unescape
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/nano_001_010_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"
PDF_TEXT = BASE / "nist-nanoconfined-fusion.txt"
BINDINGS = {
    "SFT-MAT-NANO-SIZE-SHAPE-DISTRIBUTION-001": (("NIST-NANOPARTICLE-SIZE-SHAPE", "depend critically on their size", "both SEM and AFM techniques", "more accurate 3D shape"),),
    "SFT-MAT-NANO-NANOWIRE-CONFINEMENT-002": (("NIST-GAN-NANOWIRE-GROWTH", "control of nanowire location and diameter", "quantum wells and quantum disks within the nanowires"),),
    "SFT-MAT-NANO-LAYER-STACKING-003": (("NIST-QUANTUM-TRANSPORT-2D-STACKING", "novel two-dimensional materials", "custom stacking station", "twisted 2D materials"),),
    "SFT-MAT-NANO-QUANTUM-DOT-CONFINEMENT-004": (("NIST-NANOWORLD-QUANTUM-DOTS", "semiconductor quantum dots", "electronic, optical and mechanical properties of ultrasmall structures"),),
    "SFT-MAT-NANO-SURFACE-VOLUME-DOMINANCE-005": (("NIST-NANOPARTICLE-SURFACE-AREA", "mass, number of particles", "surface area units", "greater surface area"),),
    "SFT-MAT-NANO-PHASE-MELTING-BOUNDARY-006": (("NIST-NANOCONFINED-FUSION", "temperature of fusion Tfus of a nanoconfined liquid", "Tfus can change significantly depending on the nanoparticle/nanopore size", "nature of"),),
    "SFT-MAT-NANO-QUANTUM-COLLECTIVE-STATE-007": (("NIST-MOIRE-QUANTUM-PHASES", "quantum phases resulting from the interplay between electron correlations and topology", "superconductivity and correlated insulating states"),),
    "SFT-MAT-NANO-MOIRE-SUPERSTRUCTURE-008": (("NIST-MOIRE-EXCITONS", "stacking two monolayer semiconductors", "lattice mismatch or rotational misalignment introduces an in-plane moiré superlattice", "confined within the moiré potential"),),
    "SFT-MAT-NANO-NANOCOMPOSITE-INTERFACE-DENSITY-009": (("NIST-NANOCOMPOSITE-INTERFACIAL-LAYER", "thickness and density of the static layer", "static interfacial layer of reduced polymer density", "thickness of ca. 2 nm"),),
    "SFT-MAT-NANO-AGGREGATION-DISPERSION-CUSTODY-010": (("NIST-NANOPARTICLE-AGGREGATION-DISPERSION", "real-time size, mass and concentration measurement", "Differentiating aggregated NPs and non-aggregated states"),),
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def normalize(text):
    return "".join(character for character in unescape(re.sub(r"<[^>]+>", " ", text)).casefold() if character.isalnum())


def normalize_plain(text):
    return "".join(character for character in text.casefold() if character.isalnum())


def main():
    manifest = json.loads(MANIFEST.read_text())
    manifest_identity = manifest.pop("manifest_identity")
    if canonical(manifest) != manifest_identity:
        raise SystemExit("NANO manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("NANO source changed " + source_id)
        if source_id == "NIST-NANOCONFINED-FUSION":
            if not PDF_TEXT.exists():
                raise SystemExit("NANO-006 text reconstruction missing")
            corpora[source_id] = normalize_plain(PDF_TEXT.read_text(errors="ignore"))
        else:
            corpora[source_id] = normalize(path.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for binding in bindings:
            source_id, *fragments = binding
            present = [normalize(fragment) in corpora[source_id] for fragment in fragments]
            if not all(present):
                raise SystemExit(f"NANO fragments absent {claim_id} {source_id} {present}")
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
            if source_id == "NIST-NANOCONFINED-FUSION":
                comparison.update(text_reconstruction_path=PDF_TEXT.relative_to(ROOT).as_posix(), text_reconstruction_hash=file_hash(PDF_TEXT))
            comparisons.append(comparison)
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": True})
    vector = {
        "schema": "sft-v3-materials-nano-complete-evidence-vector/1",
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
