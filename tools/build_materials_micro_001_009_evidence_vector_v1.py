#!/usr/bin/env python3
"""Build the complete MICRO-001--009 post-registry evidence vector."""

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/micro_001_009_v2"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"


BINDINGS = {
    "SFT-MAT-MICRO-DEFECT-POPULATION-001": (("NIST-POINT-DEFECTS-2026", "dilute concentrations of point defects", "measured defect chemistry"),),
    "SFT-MAT-MICRO-DEFECT-MIGRATION-002": (("NIST-POINT-DEFECTS-2026", "vacancy diffusion", "mobility and local interaction of ionic charge carriers"), ("NIST-DISLOCATION-DYNAMICS-2021", "evolution of dislocation structures", "vacancy concentration")),
    "SFT-MAT-MICRO-DISLOCATION-REACTION-003": (("NIST-DISLOCATION-CLIMB-MONOGRAPH-59", "dislocation climb is necessary before unlike dislocations can unite", "lattice vacancies must deposit all along the dislocation line"), ("NIST-DISLOCATION-DYNAMICS-2021", "evolution of dislocation structures", "vacancy concentration")),
    "SFT-MAT-MICRO-GRAIN-GROWTH-004": (("NIST-SHARP-INTERFACE-GRAINS-2001", "normal velocity of the boundary is proportional to both its curvature", "interfacial energy and mobility"),),
    "SFT-MAT-MICRO-BOUNDARY-SEGREGATION-005": (("NIST-SEGREGATION-PRECIPITATION-2021", "grain boundary segregation", "composition"),),
    "SFT-MAT-MICRO-PRECIPITATE-INCLUSION-006": (("NIST-SEGREGATION-PRECIPITATION-2021", "precipitation of a secondary phase", "partially or completely incoherent with the host lattice"), ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK", "source unavailable 404 preserved", "not used for favourable comparison")),
    "SFT-MAT-MICRO-COARSENING-TRANSFER-007": (("NIST-BENCHMARK-COARSENING-2017", "growth and coarsening of a second phase", "ostwald ripening problem"), ("NIST-STRUCTURES-PRECIPITATION-HANDBOOK", "source unavailable 404 preserved", "replacement addendum retained")),
    "SFT-MAT-MICRO-INTERFACE-MOBILITY-008": (("NIST-SHARP-INTERFACE-GRAINS-2001", "normal velocity of the boundary is proportional to both its curvature", "interfacial energy and mobility"), ("NIST-UNIFIED-GRAIN-BOUNDARY-MOTION-2008", "normal motion of a grain boundary", "proportional to the normal motion of the interface")),
    "SFT-MAT-MICRO-MULTISCALE-CORRESPONDENCE-009": (("NIST-MULTISCALE-MATERIALS-2026", "over multiple length scales", "local microstructural arrangements"), ("NIST-MICROSTRUCTURE-PROPERTY-TOOLS-2026", "macroscopic properties from images of real or simulated microstructures", "structure-property linkages at the microstructure scale")),
}


def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return "".join(character for character in text.casefold() if character.isalnum())


def main():
    manifest = json.loads(MANIFEST.read_text())
    identity = manifest.pop("manifest_identity")
    if canonical(manifest) != identity or not manifest["all_registered_and_addendum_source_identities_accounted_for"]:
        raise SystemExit("MICRO vector halted: source manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    text_paths = {
        "NIST-DISLOCATION-CLIMB-MONOGRAPH-59": BASE / "nist-dislocation-climb-monograph-59.txt",
        "NIST-SEGREGATION-PRECIPITATION-2021": BASE / "nist-segregation-precipitation-2021.txt",
    }
    corpora = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("MICRO vector halted: source changed " + source_id)
        corpora[source_id] = normalized(text_paths.get(source_id, path).read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for source_id, first, second in bindings:
            source = documents[source_id]
            usable = source["used_for_favourable_comparison"]
            passed = not usable or (normalized(first) in corpora[source_id] and normalized(second) in corpora[source_id])
            if not passed:
                raise SystemExit(f"MICRO vector halted: fragments absent {claim_id} {source_id}")
            comparisons.append({"source_id": source_id, "source_status": source["status"], "snapshot_path": source["snapshot_path"], "snapshot_hash": source["snapshot_hash"], "first_registered_fragment": first, "second_registered_fragment": second, "fragments_present_or_unavailable_row_preserved": passed, "used_for_favourable_comparison": usable})
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_available_fragments_present": all(row["fragments_present_or_unavailable_row_preserved"] for row in comparisons)})
    payload = {
        "schema": "sft-v3-materials-micro-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_addendum_identity": manifest["source_addendum_identity"],
        "source_custody_manifest_identity": identity,
        "claim_count": len(rows), "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": manifest["captured_count"], "unavailable_source_count": manifest["unavailable_count"],
        "pdf_text_reconstructions": [{"source_id": source_id, "text_path": path.relative_to(ROOT).as_posix(), "text_hash": file_hash(path)} for source_id, path in text_paths.items()],
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "target_content_selected_survivor": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_count": len(rows), "comparison_count": sum(row["comparison_count"] for row in rows), "complete_vector_identity": payload["complete_vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
