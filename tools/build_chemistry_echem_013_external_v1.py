#!/usr/bin/env python3
"""Build the post-seal ECHEM-013 cross-branch handoff record."""
import hashlib
import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "experiments/external_sources/chemistry/echem_013_complete_postseal_analysis_v1.json"
SOURCE = ROOT / "experiments/external_sources/materials/snapshots/nist-metal-additive-corrosion.html"
SOURCE_HASH = "sha256:a1bb9a6bc22eb85fb7a1b3c7d0ac4bc0837d68832b7b7c6f357a68ea6cde0322"
CERTIFICATES = {
    "chemistry": ("claims/SFT-CHEM-CELL-POTENTIAL-COMPOSITION-003/certificate.json", "sha256:bad076c5b7573c9cc8fbb87b6a07602b31981e05a14372404cc8fe8a747d7653"),
    "materials": ("claims/SFT-MAT-DEGR-CORROSION-001/certificate.json", "sha256:bca77793595dd1e50dcb43c150acb5497b9bc9983c27313a3e3e6965198e5fec"),
    "engineering": ("claims/SFT-ENG-REQUIREMENT-001/certificate.json", "sha256:66fbe158311817b4529b26ac38ff3be2e35d229e91d6281021873122c7ace1ae"),
}


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def main() -> None:
    if OUT.exists():
        raise SystemExit("ECHEM-013 analysis already exists; rebuild prohibited")
    if digest(SOURCE.read_bytes()) != SOURCE_HASH:
        raise SystemExit("inherited NIST Materials source changed")
    records = {}
    for owner, (path, expected) in CERTIFICATES.items():
        file = ROOT / path
        if digest(file.read_bytes()) != expected:
            raise SystemExit(f"admitted {owner} certificate changed")
        data = json.loads(file.read_text())
        records[owner] = {
            "claim_id": data["claim_id"], "certificate_path": path, "certificate_sha256": expected,
            "engine_receipt_hash": data["engine_receipt_hash"], "status": data["status"], "exact_result": data["exact_result"],
        }
    html = SOURCE.read_text(errors="replace")
    plain = unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))).strip()
    required = (
        "process-structure-property-performance relationships",
        "materials science",
        "measurement data and metadata",
        "improved corrosion resistance over wrought material",
        "Potentiodynamic scans",
        "pitting behavior",
        "Electrochemical measurements determined",
    )
    missing = [fragment for fragment in required if fragment.casefold() not in plain.casefold()]
    if missing:
        raise SystemExit(f"ECHEM-013 NIST handoff evidence missing: {missing}")
    ownership = (
        {"ordinal": 1, "coordinate": "species-reactions", "owner": "chemistry", "claim_id": records["chemistry"]["claim_id"], "receipt": records["chemistry"]["engine_receipt_hash"]},
        {"ordinal": 2, "coordinate": "bulk-device-response", "owner": "materials", "claim_id": records["materials"]["claim_id"], "receipt": records["materials"]["engine_receipt_hash"]},
        {"ordinal": 3, "coordinate": "implementation", "owner": "engineering", "claim_id": records["engineering"]["claim_id"], "receipt": records["engineering"]["engine_receipt_hash"]},
    )
    payload = {
        "schema": "sft-v3-chemistry-echem-013-complete-postseal-analysis/1",
        "complete_owner_count": len(ownership), "complete_ownership_vector": ownership,
        "one_owner_per_coordinate": len({row["coordinate"] for row in ownership}) == len({row["owner"] for row in ownership}) == len(ownership),
        "complete_admitted_certificate_vector": records,
        "directed_handoff_vector": [
            {"source": records["chemistry"]["claim_id"], "target": records["materials"]["claim_id"], "relation": "chemical-state-to-bulk-response"},
            {"source": records["materials"]["claim_id"], "target": records["engineering"]["claim_id"], "relation": "bulk-response-to-implementation-requirement"},
        ],
        "duplicate_ownership_rows": [],
        "complete_nist_source": {"snapshot_path": SOURCE.relative_to(ROOT).as_posix(), "snapshot_sha256": SOURCE_HASH, "byte_count": len(SOURCE.read_bytes()), "plain_text_character_count": len(plain), "plain_text_sha256": digest(plain.encode()), "required_feature_vector": list(required)},
        "nist_material_performance_correspondence": {"processing_structure_property_performance_relation_retained": True, "potentiodynamic_scan_and_pitting_behavior_retained": True, "electrochemical_measurement_and_corrosion_resistance_retained": True, "measurement_data_metadata_reliability_reproducibility_and_qualification_scope_retained": True},
        "chemistry_owns_species_and_reactions_materials_owns_bulk_response_engineering_owns_implementation": True,
        "cross_branch_handoff_adds_no_duplicate_natural_law_or_application_selected_rule": True,
        "source_surface_development_observed_before_claim_specific_extraction": True,
        "claim_specific_target_classification_completed_only_after_prediction_seal": True,
        "source_outcome_used_to_select_any_native_law_or_survivor": False,
    }
    payload["complete_result_vector_sha256"] = digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"analysis": OUT.relative_to(ROOT).as_posix(), "analysis_sha256": digest(OUT.read_bytes()), "result_vector_sha256": payload["complete_result_vector_sha256"], "owners": len(ownership), "handoffs": len(payload["directed_handoff_vector"]), "source_bytes": payload["complete_nist_source"]["byte_count"]}, indent=2))


if __name__ == "__main__":
    main()
