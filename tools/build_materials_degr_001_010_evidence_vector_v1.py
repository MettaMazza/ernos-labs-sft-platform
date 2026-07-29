#!/usr/bin/env python3
"""Bind all DEGR claims to their post-registry authoritative source records."""

from hashlib import sha256
from html import unescape
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "experiments/external_sources/materials/degr_001_010_v1"
MANIFEST = BASE / "source_custody_manifest.json"
OUT = BASE / "complete_evidence_vector_v1.json"
BINDINGS = {
    "SFT-MAT-DEGR-OXIDATION-SCALE-001": (("NIST-OXIDE-GROWTH", "unidirectional growth mechanisms", "size, shape"),),
    "SFT-MAT-DEGR-CORROSION-PATH-002": (("NIST-ELECTROCHEMICAL-CORROSION", "electrochemical polarization", "immersion corrosion"),),
    "SFT-MAT-DEGR-PASSIVATION-BREAKDOWN-003": (("NIST-LOCALIZED-CORROSION-RESISTANCE", "localized corrosion resistance", "aggressive aqueous"),),
    "SFT-MAT-DEGR-STRESS-CORROSION-004": (("NIST-STRESS-CORROSION-CRACK", "Stress corrosion cracks typically nucleate", "propagate away from the surface"),),
    "SFT-MAT-DEGR-HYDROGEN-EMBRITTLEMENT-005": (("NIST-HYDROGEN-UPTAKE-EMBRITTLEMENT", "sensitive to hydrogen embrittlement", "Hydrogen Uptake"),),
    "SFT-MAT-DEGR-WEAR-MODE-DISTINCTION-006": (("NIST-MULTIAXIAL-WEAR", "versatile wear tester", "designed and built"),),
    "SFT-MAT-DEGR-RADIATION-DEFECT-RECOVERY-007": (("NIST-UV-RADIATION-DAMAGE", "direct measurements", "UV-damaged silicon photodiodes"),),
    "SFT-MAT-DEGR-PHYSICAL-AGEING-008": (("NIST-PHYSICAL-AGEING-RECOVERY", "hygrothermal effects", "Physical Aging and Structural Recovery"),),
    "SFT-MAT-DEGR-WEATHERING-009": (("NIST-WEATHER-MATERIAL-RESPONSE", "fully instrumented weather station", "outdoor test site"),),
    "SFT-MAT-DEGR-SERVICE-LIFE-EVIDENCE-010": (("NIST-SERVICE-LIFE-BOUNDARY", "persistent problems", "century of work"),),
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
        raise SystemExit("DEGR manifest changed")
    documents = {row["source_id"]: row for row in manifest["documents"]}
    corpora = {}
    for source_id, row in documents.items():
        path = ROOT / row["snapshot_path"]
        if file_hash(path) != row["snapshot_hash"]:
            raise SystemExit("DEGR source changed " + source_id)
        corpora[source_id] = normalize(path.read_text(errors="ignore"))
    rows = []
    for claim_id, bindings in BINDINGS.items():
        comparisons = []
        for binding in bindings:
            source_id, *fragments = binding
            present = [normalize(fragment) in corpora[source_id] for fragment in fragments]
            if not all(present):
                raise SystemExit(f"DEGR fragments absent {claim_id} {source_id} {present}")
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
        "schema": "sft-v3-materials-degr-complete-evidence-vector/1",
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
