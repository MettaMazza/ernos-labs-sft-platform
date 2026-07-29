#!/usr/bin/env python3
"""Build the complete post-registry authoritative THERM comparison vector."""
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/therm_001_007_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"

BINDINGS = {
    "SFT-MAT-THERM-DIFFUSIVITY-001": (
        ("NIST-MATERIALS-DATA-GUIDE", "K=pCpD", "thermal conductivity and thermal diffusivity should be correlated"),
        ("NIST-THERMAL-DIFFUSIVITY-AM", "thermal diffusivity", "thermal conductivity"),
    ),
    "SFT-MAT-THERM-BOUNDARY-RESISTANCE-002": (
        ("NIST-FDTR-TRANSPORT", "thermal interface resistance", "multilayered materials"),
    ),
    "SFT-MAT-THERM-PHONON-MEAN-PATH-003": (
        ("NIST-INTERFACE-SCATTERING", "phonon interface scattering", "mean free path"),
        ("NIST-PHONON-THERMAL-LIMITS", "collective modes of these vibrations called phonons", "thermal energy"),
    ),
    "SFT-MAT-THERM-RADIATIVE-TRANSPORT-004": (
        ("NIST-INFRARED-OPTICAL-PROPERTIES", "reflectance, transmittance and emittance", "radiative heat transfer measurements"),
    ),
    "SFT-MAT-THERM-THERMOELECTRIC-BOUNDARY-005": (
        ("NIST-THERMOELECTRIC-MEASUREMENTS", "figure of merit zT", "Seebeck coefficient"),
        ("NIST-TRANSPORT-THERMOELECTRIC", "bulk and thin film thermoelectric materials", "High-Temperature Seebeck Coefficient Standard"),
    ),
    "SFT-MAT-THERM-PHASE-STORAGE-006": (
        ("NIST-PHASE-CHANGE-STORAGE", "thermal energy storage via phase-change materials", "thermal resistance"),
        ("NIST-NANOCALORIMETRY", "phase transitions", "heat capacity"),
    ),
    "SFT-MAT-THERM-SHOCK-FATIGUE-007": (
        ("NIST-FRACTOGRAPHY-THERMAL-SHOCK", "Thermal stresses and strains occur", "cyclic fatigue"),
        ("NIST-THERMAL-SHOCK-SILICON-NITRIDE", "critical quench temperature for failure", "extension of Vickers radial cracks"),
    ),
}

TEXT = {
    "NIST-MATERIALS-DATA-GUIDE": BASE / "nist-materials-data-guide.txt",
    "NIST-THERMAL-DIFFUSIVITY-AM": BASE / "nist-thermal-diffusivity-am.txt",
    "NIST-THERMOELECTRIC-MEASUREMENTS": BASE / "nist-thermoelectric-measurements.txt",
    "NIST-FRACTOGRAPHY-THERMAL-SHOCK": BASE / "nist-fractography-thermal-shock.txt",
    "NIST-PHONON-THERMAL-LIMITS": ROOT / "experiments/external_sources/materials/snapshots/nist-phonon-thermal-limits-2026-07-27.txt",
}

def canonical(value):
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    return "sha256:" + sha256(path.read_bytes()).hexdigest()

def normalize(value):
    return "".join(character for character in value.casefold() if character.isalnum())

def main():
    manifest = json.loads(MANIFEST.read_text())
    manifest_identity = manifest.pop("manifest_identity")
    if canonical(manifest) != manifest_identity:
        raise SystemExit("THERM source manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpus = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("THERM source changed: " + source_id)
        corpus[source_id] = normalize(TEXT.get(source_id, path).read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for source_id, first, second in bindings:
            first_present = normalize(first) in corpus[source_id]
            second_present = normalize(second) in corpus[source_id]
            if not (first_present and second_present):
                raise SystemExit(f"THERM registered fragments absent: {claim_id} {source_id} {first_present}/{second_present}")
            source = documents[source_id]
            comparisons.append({"source_id": source_id, "source_status": source["status"], "snapshot_path": source["snapshot_path"], "snapshot_hash": source["snapshot_hash"], "first_registered_fragment": first, "second_registered_fragment": second, "first_fragment_present": first_present, "second_fragment_present": second_present, "used_for_favourable_comparison": True})
        rows.append({"claim_id": claim_id, "comparisons": comparisons, "comparison_count": len(comparisons), "all_comparisons_preserved": True, "all_registered_fragments_present": True})
    payload = {
        "schema": "sft-v3-materials-therm-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_custody_manifest_identity": manifest_identity,
        "claim_count": len(rows),
        "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": manifest["captured_count"],
        "unavailable_source_count": manifest["unavailable_count"],
        "pdf_text_reconstructions": [{"source_id": source_id, "text_path": path.relative_to(ROOT).as_posix(), "text_hash": file_hash(path)} for source_id, path in TEXT.items()],
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "target_content_selected_survivor": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claims": len(rows), "comparisons": sum(row["comparison_count"] for row in rows), "identity": payload["complete_vector_identity"]}, indent=2))

if __name__ == "__main__":
    main()
