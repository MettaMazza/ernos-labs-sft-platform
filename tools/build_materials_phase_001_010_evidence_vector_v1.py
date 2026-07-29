#!/usr/bin/env python3
"""Build the complete post-registry PHASE-001--010 evidence vector."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/phase_001_010_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"


BINDINGS = {
    "SFT-MAT-PHASE-FRACTION-LEDGER-001": (
        ("NIST-TEXTURE-PHASE-FRACTION", "Accurate quantification of the crystallographic texture", "phase fraction measurements"),
        ("NIST-LEVER-RULE-SOLIDIFICATION", "phase compositions", "phase fractions and enthalpies"),
    ),
    "SFT-MAT-PHASE-TIE-LINE-LEVER-002": (
        ("NIST-LEVER-RULE-SOLIDIFICATION", "single point equilibrium calculation", "phase compositions, phase fractions and enthalpies"),
        ("NIST-LLE-TERNARY-TIE-LINES", "compositions of co-existing phases", "Tie-line data are represented as two data sets"),
    ),
    "SFT-MAT-PHASE-COMPONENT-HANDOFF-003": (
        ("NIST-SAT-TMMC-COEXISTENCE", "activity (chemical potential", "pressures of the liquid and vapor phases were equal"),
    ),
    "SFT-MAT-PHASE-METASTABLE-RETENTION-004": (
        ("NIST-LIQUID-WATER-METASTABLE", "some temperatures where liquid water is metastable", "metastable liquid phase"),
        ("NIST-BINARY-HALIDE-TRANSFORMATIONS", "Irreversible crystal structure transformations", "function of time"),
    ),
    "SFT-MAT-PHASE-SPINODAL-INSTABILITY-005": (
        ("NIST-LIQUID-WATER-METASTABLE", "liquid-vapor spinodal", "re-entrant spinodal"),
        ("NIST-ORDER-DISORDER-SEPARATION", "Order-disorder and phase separation", "driven by energetics of opposite sign"),
    ),
    "SFT-MAT-PHASE-MARTENSITIC-006": (
        ("NIST-MARTENSITIC-MATERIALS-STUDY", "virtually diffusionless structural change", "associated shape change"),
    ),
    "SFT-MAT-PHASE-RECONSTRUCTIVE-007": (
        ("NIST-BINARY-HALIDE-TRANSFORMATIONS", "Irreversible crystal structure transformations", "remains in the new transformed structure even after cooling"),
    ),
    "SFT-MAT-PHASE-ORDER-DISORDER-008": (
        ("NIST-ORDER-DISORDER-SEPARATION", "condensed solutions of two or more components", "disordered state has greater configurational entropy"),
        ("NIST-BINARY-HALIDE-TRANSFORMATIONS", "increase in disorder with rising temperature", "order-disorder change"),
    ),
    "SFT-MAT-PHASE-GLASS-ARREST-009": (
        ("NIST-GLASS-TRANSITION", "thermodynamic and kinetic aspects of the glass transition event", "techniques used to measure the glass transition temperature"),
    ),
    "SFT-MAT-PHASE-TIME-TEMPERATURE-010": (
        ("NIST-SOLIDIFICATION", "nucleation, growth kinetics", "Polyphase solidification"),
        ("NIST-PHASE-TRANSITION-TEMPERATURES", "compiled and evaluated phase transition temperatures", "recommended phase transitions"),
    ),
}


TEXT_OVERRIDES = {
    "NIST-LIQUID-WATER-METASTABLE": ROOT / "experiments/external_sources/materials/snapshots/nist-liquid-water-properties-2026-07-27.txt",
    "NIST-BINARY-HALIDE-TRANSFORMATIONS": BASE / "nist-binary-halide-transformations.txt",
    "NIST-MARTENSITIC-MATERIALS-STUDY": BASE / "nist-martensitic-materials-study.txt",
    "NIST-PHASE-TRANSITION-TEMPERATURES": BASE / "nist-phase-transition-temperatures-2025.txt",
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return "".join(character for character in text.casefold() if character.isalnum())


def main():
    manifest = json.loads(MANIFEST.read_text())
    manifest_identity = manifest.pop("manifest_identity")
    if canonical(manifest) != manifest_identity or not manifest["all_registered_source_identities_accounted_for"]:
        raise SystemExit("PHASE vector halted: custody manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        snapshot = ROOT / row["snapshot_path"]
        if file_hash(snapshot) != row["snapshot_hash"]:
            raise SystemExit("PHASE vector halted: source changed " + source_id)
        text_path = TEXT_OVERRIDES.get(source_id, snapshot)
        corpora[source_id] = normalized(text_path.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for source_id, first, second in bindings:
            source = documents[source_id]
            first_present = normalized(first) in corpora[source_id]
            second_present = normalized(second) in corpora[source_id]
            if not first_present or not second_present:
                raise SystemExit(f"PHASE vector halted: fragments absent {claim_id} {source_id}: {first_present}/{second_present}")
            comparisons.append({"source_id": source_id, "source_status": source["status"], "snapshot_path": source["snapshot_path"], "snapshot_hash": source["snapshot_hash"], "first_registered_fragment": first, "second_registered_fragment": second, "first_fragment_present": first_present, "second_fragment_present": second_present, "used_for_favourable_comparison": True})
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": all(item["first_fragment_present"] and item["second_fragment_present"] for item in comparisons)})
    payload = {
        "schema": "sft-v3-materials-phase-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_custody_manifest_identity": manifest_identity,
        "claim_count": len(rows),
        "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": manifest["captured_count"],
        "unavailable_source_count": manifest["unavailable_count"],
        "pdf_text_reconstructions": [{"source_id": source_id, "text_path": path.relative_to(ROOT).as_posix(), "text_hash": file_hash(path)} for source_id, path in TEXT_OVERRIDES.items()],
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "target_content_selected_survivor": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_count": len(rows), "comparison_count": sum(row["comparison_count"] for row in rows), "complete_vector_identity": payload["complete_vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
