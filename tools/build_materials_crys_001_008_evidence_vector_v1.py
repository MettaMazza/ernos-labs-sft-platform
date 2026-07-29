#!/usr/bin/env python3
"""Build the complete post-registry CRYS-001--008 evidence vector."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/crys_001_008_v3"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"


CLAIMS = {
    "SFT-MAT-CRYS-DIFFRACTION-AMPLITUDE-001": (
        ("NIST-TOTAL-SCATTERING-PDF-2014", "total scattering function", "related to interatomic distances"),
        ("IUCR-TWINNED-DIFFRACTION-DATA-2022", "twin domains scatter coherently", "bragg reflections and diffuse streaks"),
    ),
    "SFT-MAT-CRYS-STRUCTURE-FACTOR-002": (
        ("NIST-SP846-POWDER-DIFFRACTION-1992", "structure factor for reflection", "relates the intensity to the crystal structure parameters"),
        ("NIST-TOTAL-SCATTERING-PDF-2014", "atomic scattering factors", "scattering vector magnitude"),
    ),
    "SFT-MAT-CRYS-TEXTURE-ORIENTATION-003": (
        ("NIST-NCAL-TEXTURE-PHASE-FRACTION-2026", "grains sharing a common crystal structure but having different crystallographic orientations", "cross comparison between measurement techniques such as neutron diffraction"),
        ("NIST-NCAL-TEXTURE-PHASE-FRACTION-2026", "uncertainty metrics are also typically unquantified", "phase fraction measurements may exhibit bias"),
    ),
    "SFT-MAT-CRYS-SHORT-RANGE-DIFFUSE-004": (
        ("IUCR-MODULATION-WAVE-DIFFUSE-2015", "both longer range order and truly short-range order are simultaneously encoded", "highly structured diffuse intensity distributions"),
        ("IUCR-STACKING-DIFFUSE-2023", "any faulted sequence of layers produces streaks of diffuse scattering", "preferred local structure"),
    ),
    "SFT-MAT-CRYS-STACKING-FAULT-DIFFRACTION-005": (
        ("IUCR-STACKING-FAULT-LDH-2020", "recursive routine for generating and averaging supercells", "measured diffraction data"),
        ("IUCR-STACKING-FAULT-LDH-2020", "occurrence of stacking faults causes diffuse scattering", "degree and type of faulting"),
    ),
    "SFT-MAT-CRYS-TWIN-DOMAIN-006": (
        ("IUCR-TWINNED-DIFFRACTION-DATA-2022", "non-merohedrally twinned with a twofold rotation", "twin domains scatter coherently"),
        ("IUCR-TWIN-DICTIONARY-2026", "source unavailable 403 preserved", "not used for favourable comparison"),
    ),
    "SFT-MAT-CRYS-MODULATED-INCOMMENSURATE-007": (
        ("IUCR-MODULATED-STRUCTURES-2009", "additional bragg reflections", "integer indexing with three indices hkl is not possible"),
        ("IUCR-MODULATED-STRUCTURES-2009", "satellite reflections", "loss of periodicity in three dimensions"),
        ("IUCR-INCOMMENSURATE-DICTIONARY-2026", "source unavailable 403 preserved", "not used for favourable comparison"),
    ),
    "SFT-MAT-CRYS-PAIR-DISTRIBUTION-008": (
        ("NIST-TOTAL-SCATTERING-PDF-2014", "fourier transform of the was data", "pair-distribution function"),
        ("NIST-TOTAL-SCATTERING-PDF-2014", "total scattering function", "related to interatomic distances"),
    ),
}


def digest(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> str:
    return "sha256:" + sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def normalized(text: str) -> str:
    return "".join(character for character in text.casefold() if character.isalnum())


def main() -> None:
    manifest = json.loads(MANIFEST.read_text())
    claimed = manifest.pop("manifest_identity")
    if canonical(manifest) != claimed or not manifest["all_registered_source_identities_accounted_for"]:
        raise SystemExit("CRYS evidence-vector build halted: source custody manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    text_paths = {
        "NIST-SP846-POWDER-DIFFRACTION-1992": BASE / "nist-sp846-powder-diffraction.txt",
        "NIST-TOTAL-SCATTERING-PDF-2014": BASE / "nist-total-scattering-pdf-2014.txt",
    }
    corpora = {}
    for source_id, row in documents.items():
        source_path = ROOT / row["snapshot_path"]
        if digest(source_path) != row["snapshot_hash"]:
            raise SystemExit(f"CRYS evidence-vector build halted: source changed {source_id}")
        text_path = text_paths.get(source_id, source_path)
        corpora[source_id] = normalized(text_path.read_text(encoding="utf-8", errors="ignore"))

    rows = []
    for claim_id, requirements in CLAIMS.items():
        comparisons = []
        for source_id, first, second in requirements:
            source = documents[source_id]
            unavailable = source["status"] != "captured"
            present = unavailable or (normalized(first) in corpora[source_id] and normalized(second) in corpora[source_id])
            if not present:
                raise SystemExit(f"CRYS evidence-vector build halted: required source fragments absent for {claim_id} / {source_id}")
            comparisons.append({
                "source_id": source_id,
                "source_status": source["status"],
                "snapshot_path": source["snapshot_path"],
                "snapshot_hash": source["snapshot_hash"],
                "first_registered_fragment": first,
                "second_registered_fragment": second,
                "fragments_present_or_unavailable_row_preserved": present,
                "used_for_favourable_comparison": source["used_for_favourable_comparison"],
            })
        rows.append({
            "claim_id": claim_id,
            "comparisons": comparisons,
            "comparison_count": len(comparisons),
            "all_comparisons_preserved": True,
            "all_available_fragments_present": all(x["fragments_present_or_unavailable_row_preserved"] for x in comparisons),
        })
    payload = {
        "schema": "sft-v3-materials-crys-complete-evidence-vector/1",
        "target_registry_identity": manifest["target_registry_identity"],
        "source_custody_manifest_identity": claimed,
        "claim_count": len(rows),
        "claims": rows,
        "source_status_rows": list(documents.values()),
        "captured_source_count": sum(x["status"] == "captured" for x in documents.values()),
        "unavailable_source_count": sum(x["status"] != "captured" for x in documents.values()),
        "pdf_text_reconstructions": [
            {"source_id": source_id, "text_path": path.relative_to(ROOT).as_posix(), "text_hash": digest(path)}
            for source_id, path in text_paths.items()
        ],
        "all_favourable_adverse_absent_unavailable_unresolved_rows_preserved": True,
        "target_content_selected_survivor": False,
    }
    payload["complete_vector_identity"] = canonical(payload)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"claim_count": len(rows), "comparison_count": sum(x["comparison_count"] for x in rows), "complete_vector_identity": payload["complete_vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
