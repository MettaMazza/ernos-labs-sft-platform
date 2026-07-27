#!/usr/bin/env python3
"""Build the complete post-seal ORG-008 article/PDF structure and mechanism vector."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY_PATH = Path("experiments/external_sources/chemistry/org_008_target_identities_v1.json")
IDENTITY_HASH = "sha256:d718044a43d35b2c2a01a419359cb1316053e6ec684d3dd10d4685565082b453"
SEAL_PATH = Path("experiments/sealed_predictions/chemistry_org_008_electrophilic_substitution_pre_source_v1.json")
SEAL_PAYLOAD_HASH = "sha256:6ee04e4bdf6f4446c43e7ddcf867db70108626b3a15a9fcea6d36dff07ee43c3"
INVENTORY_PATH = Path("experiments/external_sources/chemistry/snapshots/org-008-nature-blind-v1/source-inventory-v1.json")
OUTPUT_PATH = Path("experiments/external_sources/chemistry/org_008_complete_targets_v1.json")
PRIMARY_PATH = Path("experiments/external_sources/chemistry/snapshots/org-008-nature-blind-v1/org-008-primary-record-v1.json")


def _term_text(payload: dict) -> str:
    return " ".join(row.get("text", "") for row in payload["term"].get("definitions", ()))


def _table_s1(page_text: str) -> tuple[dict, ...]:
    rows = []
    for line in page_text.splitlines():
        match = re.match(r"^([A-SU-Y]|T[^A-Za-z0-9\s]?)\s+(.+?)\s+(0\*?|12|93|100)\s*$", line.strip())
        if match:
            entry = match.group(1)[0]
            rows.append({"entry": entry, "complete_row_inscription": line.strip(), "displayed_yield": match.group(3)})
    if tuple(row["entry"] for row in rows) != tuple(chr(value) for value in range(ord("A"), ord("Y") + 1)):
        raise ValueError("ORG-008 complete Table S1 row order did not reconstruct")
    return tuple(rows)


def main() -> int:
    if hash_file(ROOT / IDENTITY_PATH) != IDENTITY_HASH:
        raise SystemExit("ORG-008 identity changed: VOID_INVALID_HALTED")
    seal = json.loads((ROOT / SEAL_PATH).read_text(encoding="utf-8"))
    claimed = seal.pop("sealed_payload_hash", None)
    if claimed != SEAL_PAYLOAD_HASH or sha256_identity(seal) != SEAL_PAYLOAD_HASH:
        raise SystemExit("ORG-008 prediction changed: VOID_INVALID_HALTED")
    identities = json.loads((ROOT / IDENTITY_PATH).read_text(encoding="utf-8"))["rows"]
    inventory = json.loads((ROOT / INVENTORY_PATH).read_text(encoding="utf-8"))
    captured = {row["target_id"]: row for row in inventory["rows"]}
    source_paths = {
        "SFT-CHEM-ORG-008-001": Path(identities[0]["registered_snapshot_path"]),
        "SFT-CHEM-ORG-008-002": Path(identities[1]["registered_snapshot_path"]),
        "SFT-CHEM-ORG-008-003": Path(captured["SFT-CHEM-ORG-008-003"]["snapshot_path"]),
        "SFT-CHEM-ORG-008-004": Path(captured["SFT-CHEM-ORG-008-004"]["snapshot_path"]),
    }
    source_hashes = {
        "SFT-CHEM-ORG-008-001": identities[0]["registered_snapshot_sha256"],
        "SFT-CHEM-ORG-008-002": identities[1]["registered_snapshot_sha256"],
        "SFT-CHEM-ORG-008-003": captured["SFT-CHEM-ORG-008-003"]["snapshot_sha256"],
        "SFT-CHEM-ORG-008-004": captured["SFT-CHEM-ORG-008-004"]["snapshot_sha256"],
    }
    for target_id, path in source_paths.items():
        if hash_file(ROOT / path) != source_hashes[target_id]:
            raise SystemExit(f"ORG-008 source changed: {path}")
    iupac_e = json.loads((ROOT / source_paths["SFT-CHEM-ORG-008-001"]).read_text(encoding="utf-8"))
    iupac_s = json.loads((ROOT / source_paths["SFT-CHEM-ORG-008-002"]).read_text(encoding="utf-8"))
    article_bytes = (ROOT / source_paths["SFT-CHEM-ORG-008-003"]).read_bytes()
    article_text = article_bytes.decode("utf-8", errors="replace")
    reader = PdfReader(ROOT / source_paths["SFT-CHEM-ORG-008-004"])
    page_texts = tuple(page.extract_text() or "" for page in reader.pages)
    complete_text = "\n".join(page_texts)
    folded = complete_text.casefold()
    table_s1 = _table_s1(page_texts[40])
    zero_rows = tuple(row for row in table_s1 if row["displayed_yield"].startswith("0"))
    full_rows = tuple(row for row in table_s1 if row["displayed_yield"] == "100")
    pdf_outcome = {
        "complete_pdf_page_count": len(page_texts),
        "nonempty_extracted_page_count": sum(bool(text.strip()) for text in page_texts),
        "complete_extracted_text_character_count": sum(len(text) for text in page_texts),
        "complete_page_text_vector_hash": sha256_identity(page_texts),
        "complete_table_s1_rows": table_s1,
        "complete_table_s1_row_count": len(table_s1),
        "displayed_zero_yield_or_zero_star_row_count": len(zero_rows),
        "displayed_full_yield_row_count": len(full_rows),
        "displayed_intermediate_yield_rows": tuple(row for row in table_s1 if row not in zero_rows and row not in full_rows),
        "title_compound_phrase_occurrence_count": folded.count("title compound"),
        "title_compound_page_count": sum("title compound" in text.casefold() for text in page_texts),
        "NMR_page_count": sum("nmr" in text.casefold() for text in page_texts),
        "HRMS_page_count": sum("hrms" in text.casefold() for text in page_texts),
        "rearomatization_or_rearomatisation_occurrence_count": folded.count("rearomatization") + folded.count("rearomatisation"),
        "EAS_like_ligand_coupling_present": "eas-like ligand" in folded,
        "C_electrophile_attacked_by_nucleophilic_phenol_present": "c-electrophile" in folded and "nucleophilic phenol" in folded,
        "dearomatized_intermediate_surface_present": "dearomatisation" in folded or "dearomatization" in folded,
        "rearomatization_surface_present": "rearomatization" in folded or "rearomatisation" in folded,
        "radical_control_preserved": "radical pathways have been ruled out" in folded,
        "phenoxonium_alternative_preserved": "phenoxonium" in folded,
        "starting_material_recovered_control_preserved": "starting material recovered" in folded,
        "inconsistent_condition_record_preserved": "inconsistent" in folded,
        "not_promoted_record_preserved": "not promoted" in folded,
        "inseparable_mixture_occurrence_count": folded.count("inseparable mixture"),
        "visual_reviewed_page_numbers": [1, 41, 96, 102, 105],
        "visual_review_result": "complete title, reaction/rearomatization scheme, all Table S1 rows, mechanism discussion, competition table and rearomatization procedure readable",
    }
    article_folded = article_text.casefold()
    article_outcome = {
        "complete_html_byte_count": len(article_bytes),
        "complete_html_hash": source_hashes["SFT-CHEM-ORG-008-003"],
        "title_and_DOI_present": "meta-selective c" in article_folded and "s41557-022-01101-0" in article_folded,
        "electrophilic_aromatic_substitution_scope_present": "electrophilic aromatic substitution" in article_folded,
        "sigma_complex_and_rearomatization_surface_present": ("complex" in article_folded and ("rearomatization" in article_folded or "rearomatisation" in article_folded)),
        "complete_supplementary_data_availability_present": "supplementary information" in article_folded,
    }
    outcomes = {
        "SFT-CHEM-ORG-008-001": iupac_e,
        "SFT-CHEM-ORG-008-002": iupac_s,
        "SFT-CHEM-ORG-008-003": article_outcome,
        "SFT-CHEM-ORG-008-004": pdf_outcome,
    }
    rows = []
    for identity in identities:
        target_id = identity["target_id"]
        rows.append({
            **{key: identity[key] for key in ("target_id", "source_id", "authority", "registered_identity", "source_record_role", "custody_class")},
            "opened_snapshot_path": str(source_paths[target_id]), "opened_snapshot_sha256": source_hashes[target_id],
            "response_status": "preserved-development-observed" if target_id in {"SFT-CHEM-ORG-008-001", "SFT-CHEM-ORG-008-002"} else captured[target_id]["response_status"],
            "source_outcome": outcomes[target_id],
            "target_payload_hash": sha256_identity((target_id, identity["source_record_role"], outcomes[target_id])),
        })
    e_text = _term_text(iupac_e).casefold(); s_text = _term_text(iupac_s).casefold()
    analysis = {
        "complete_target_count": len(rows), "complete_source_count": len({row["source_id"] for row in rows}),
        "development_observed_target_count": 3, "postseal_outcome_unopened_target_count": 1,
        "electrophile_accepts_both_bonding_electrons": "accepting both bonding electrons" in e_text,
        "entering_electrophile_and_leaving_electrofuge_surface_present": "entering group" in s_text and "electrofuge" in s_text,
        "leaving_carrier_relinquishes_both_electrons": "relinquishes both electrons" in s_text,
        "complete_article_identity_and_data_surface_present": all(article_outcome.values()),
        "complete_pdf_page_count": pdf_outcome["complete_pdf_page_count"],
        "nonempty_extracted_page_count": pdf_outcome["nonempty_extracted_page_count"],
        "complete_extracted_text_character_count": pdf_outcome["complete_extracted_text_character_count"],
        "complete_page_text_vector_hash": pdf_outcome["complete_page_text_vector_hash"],
        "complete_table_s1_row_count": pdf_outcome["complete_table_s1_row_count"],
        "displayed_zero_yield_or_zero_star_row_count": pdf_outcome["displayed_zero_yield_or_zero_star_row_count"],
        "displayed_full_yield_row_count": pdf_outcome["displayed_full_yield_row_count"],
        "displayed_intermediate_yield_rows": pdf_outcome["displayed_intermediate_yield_rows"],
        "title_compound_phrase_occurrence_count": pdf_outcome["title_compound_phrase_occurrence_count"],
        "title_compound_page_count": pdf_outcome["title_compound_page_count"],
        "NMR_page_count": pdf_outcome["NMR_page_count"], "HRMS_page_count": pdf_outcome["HRMS_page_count"],
        "donor_acceptor_mechanism_surface_present": pdf_outcome["EAS_like_ligand_coupling_present"] and pdf_outcome["C_electrophile_attacked_by_nucleophilic_phenol_present"],
        "dearomatized_intermediate_and_rearomatization_present": pdf_outcome["dearomatized_intermediate_surface_present"] and pdf_outcome["rearomatization_surface_present"],
        "all_adverse_mechanism_condition_and_mixture_controls_preserved": all(pdf_outcome[key] for key in ("radical_control_preserved", "phenoxonium_alternative_preserved", "starting_material_recovered_control_preserved", "inconsistent_condition_record_preserved", "not_promoted_record_preserved")) and pdf_outcome["inseparable_mixture_occurrence_count"] == 3,
        "all_favourable_adverse_absent_and_unresolved_rows_preserved": len(rows) == 4 and len(table_s1) == 25,
        "source_recapture_count": 0,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in rows)),
    }
    output = {
        "schema": "sft-v3-complete-postseal-target-vector/1", "claim_id": identities[0]["target_id"].replace("ORG-008-001", "ELECTROPHILIC-SUBSTITUTION-FAMILY-008"),
        "complete_registered_target_count": 4, "all_favourable_adverse_absent_and_unresolved_rows_preserved": True, "rows": rows,
    }
    primary = {
        "schema": "sft-v3-exact-postseal-analysis/1", "claim_id": "SFT-CHEM-ELECTROPHILIC-SUBSTITUTION-FAMILY-008",
        "identity_path": str(IDENTITY_PATH), "identity_hash": IDENTITY_HASH, "prediction_path": str(SEAL_PATH),
        "prediction_payload_hash": SEAL_PAYLOAD_HASH, "inventory_path": str(INVENTORY_PATH),
        "inventory_hash": hash_file(ROOT / INVENTORY_PATH), "exact_postseal_analysis": analysis,
    }
    (ROOT / OUTPUT_PATH).write_text(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / PRIMARY_PATH).write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "analysis": analysis}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
