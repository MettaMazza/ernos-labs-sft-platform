#!/usr/bin/env python3
"""Build the complete post-registry OPT-001--010 authoritative evidence vector."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/opt_001_010_v1"
MANIFEST = BASE / "source_custody_manifest.json"
ADDENDUM_REGISTRY = ROOT / "census/materials_opt_003_quantum_yield_source_addendum_v1.json"
ADDENDUM_MANIFEST = BASE / "opt_003_quantum_yield_source_addendum_v1.json"
OUT = BASE / "complete_evidence_vector_v1.json"

BINDINGS = {
    "SFT-MAT-OPT-ABSORPTION-EXTINCTION-001": (
        ("NIST-SPECTROPHOTOMETRY", "transmittance or absorption properties", "reflectance, transmittance, absorbance"),
    ),
    "SFT-MAT-OPT-REFLECTION-TRANSMISSION-002": (
        ("NIST-SPECTROPHOTOMETRY", "quantitative measurement of the reflectance and transmittance", "geometrical and spectral conditions of measurement"),
        ("NIST-OPTICAL-SCATTERING", "Optical scattering from surfaces", "Bidirectional Optical Scattering Facility"),
    ),
    "SFT-MAT-OPT-LUMINESCENCE-YIELD-003": (
        ("NIST-FLUORESCENCE-RAMAN", "Both fluorescence and Raman spectroscopy yield absolute signals", "Fluorescence Intensity Correction Standards"),
        ("NIST-FLUORESCENCE-QUANTUM-YIELD-GUIDE", "ratio of the number of molecules that fluoresce a photon to the number of molecules that absorb a photon from the excitation source", "relative quantum yields are much more commonly measured than absolute"),
    ),
    "SFT-MAT-OPT-LIGHT-SCATTERING-004": (
        ("NIST-OPTICAL-SCATTERING", "Optical scattering from surfaces", "Optical Grating Scatterometry"),
        ("NIST-FLUORESCENCE-RAMAN", "fluorescence and Raman spectroscopy", "Raman Intensity Correction Standards"),
    ),
    "SFT-MAT-OPT-BIREFRINGENCE-ANISOTROPY-005": (
        ("NIST-BIREFRINGENCE", "crystal structure asymmetry", "two polarizations"),
    ),
    "SFT-MAT-OPT-NONLINEAR-MIXING-006": (
        ("NIST-NONLINEAR-MIXING", "nonlinear optical mixing", "three frequencies"),
    ),
    "SFT-MAT-OPT-WAVEGUIDE-CONFINEMENT-LOSS-007": (
        ("NIST-WAVEGUIDE-LOSS", "single-mode waveguide", "linear device losses"),
    ),
    "SFT-MAT-OPT-PHOTONIC-GAP-DEFECT-008": (
        ("NIST-PHOTONIC-BANDGAP", "forbids light propagation at others", "Photonic bandgap microcombs"),
    ),
    "SFT-MAT-OPT-PLASMONIC-RESPONSE-009": (
        ("NIST-PLASMONIC-MODES", "collective oscillation of conduction electrons", "nanoscale volumes of matter"),
    ),
    "SFT-MAT-OPT-EXCITON-DYNAMICS-010": (
        ("NIST-EXCITON-DYNAMICS", "exciton population decay", "radiative and non-radiative recombination"),
        ("NIST-CARRIER-DYNAMICS", "initially generated excitons", "charge recombination"),
    ),
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
    if canonical(manifest) != manifest_identity:
        raise SystemExit("OPT manifest changed")
    addendum_registry = json.loads(ADDENDUM_REGISTRY.read_text())
    addendum_registry_identity = addendum_registry.pop("addendum_identity")
    if canonical(addendum_registry) != addendum_registry_identity:
        raise SystemExit("OPT addendum registry changed")
    addendum = json.loads(ADDENDUM_MANIFEST.read_text())
    addendum_identity = addendum.pop("manifest_identity")
    if canonical(addendum) != addendum_identity or addendum["source_registry_identity"] != addendum_registry_identity:
        raise SystemExit("OPT addendum custody changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    documents[addendum["source_id"]] = {"source_id": addendum["source_id"], "source_uri": addendum["source_uri"], "snapshot_path": addendum["snapshot_path"], "snapshot_hash": addendum["snapshot_hash"], "byte_count": addendum["byte_count"], "http_status": addendum["http_status"], "content_type": addendum["content_type"], "status": addendum["status"], "used_for_favourable_comparison": True}
    text_path = BASE / "nistir7458-fluorescence-quantum-yield.txt"
    text_sources = {addendum["source_id"]: text_path}
    corpora = {}
    for source_id, row in documents.items():
        snapshot = ROOT / row["snapshot_path"]
        if file_hash(snapshot) != row["snapshot_hash"]:
            raise SystemExit("OPT source changed " + source_id)
        corpora[source_id] = normalized(text_sources.get(source_id, snapshot).read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for source_id, first, second in bindings:
            first_present = normalized(first) in corpora[source_id]
            second_present = normalized(second) in corpora[source_id]
            if not (first_present and second_present):
                raise SystemExit(f"OPT fragments absent {claim_id} {source_id} {first_present}/{second_present}")
            source = documents[source_id]
            comparisons.append({"source_id": source_id, "source_status": source["status"], "snapshot_path": source["snapshot_path"], "snapshot_hash": source["snapshot_hash"], "first_registered_fragment": first, "second_registered_fragment": second, "first_fragment_present": first_present, "second_fragment_present": second_present, "used_for_favourable_comparison": True})
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": True})
    payload = {
        "schema": "sft-v3-materials-opt-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_custody_manifest_identity": manifest_identity,
        "source_addendum_registry_identity": addendum_registry_identity,
        "source_addendum_manifest_identity": addendum_identity,
        "claim_count": len(rows),
        "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": len(documents),
        "unavailable_source_count": 0,
        "pdf_text_reconstructions": [{"source_id": addendum["source_id"], "text_path": text_path.relative_to(ROOT).as_posix(), "text_hash": file_hash(text_path)}],
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "initial_source_limitation_preserved": True,
        "target_content_selected_survivor": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(rows), "comparisons": sum(row["comparison_count"] for row in rows), "sources": len(documents), "identity": payload["complete_vector_identity"]}, indent=2))

if __name__ == "__main__":
    main()
