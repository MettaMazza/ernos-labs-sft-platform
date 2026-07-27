#!/usr/bin/env python3
"""Versioned ORG-006 normalizer correcting only PDF label-spacing recognition."""
from __future__ import annotations

import json
from pathlib import Path
import sys

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402
from tools import build_chemistry_org_006_complete_external_v1 as v1  # noqa: E402

IDENTITY_HASH = "sha256:ba488c309eb8a3081959b7f1ae6850bd43c0db50abdf3d351532d9da76c69d17"
V1_BUILDER_HASH = "sha256:aa721846da2e03368f519dcf0bcc935406f66ae540cabb7e2fe5d62551394df0"


def corrected_pdf_facts() -> dict:
    path = ROOT / v1.PDF_PATH
    reader = PdfReader(path)
    complete = "\n".join((page.extract_text() or "") for page in reader.pages)
    required = (
        "441±114 cal mol−1", "−1.9±0.3 cal K−1 mol−1", "tt (0 .33± 0.03 [0.30])",
        "tg (0.51± 0.01 [0.54])", "pm (0.02±0.01 [0.005])", "pp (0.14±0.01 [0.16])",
        "tg = 480 cal mol−1", "= 3263 cal mol−1", "pp = 658 cal mol−1",
    )
    missing = [value for value in required if value not in complete]
    if missing:
        raise ValueError(f"ORG-006 corrected PDF extraction changed: {missing}")
    return {
        "pdf_page_count": len(reader.pages), "pdf_snapshot_path": v1.PDF_PATH, "pdf_snapshot_sha256": hash_file(path),
        "measured_spectrum_count": 22, "measured_1132_spectrum_count": 16, "measured_5CB_spectrum_count": 6,
        "external_condition": "298.5 K",
        "ordered_population_vector": {"tt": "0.33 ± 0.03", "tg": "0.51 ± 0.01", "pm": "0.02 ± 0.01", "pp": "0.14 ± 0.01"},
        "isotropic_population_vector": {"tt": "0.30", "tg": "0.54", "pm": "0.005", "pp": "0.16"},
        "ordered_population_exact_display_fractions": {"tt": "33/100", "tg": "51/100", "pm": "1/50", "pp": "7/50"},
        "ordered_population_exact_display_sum": "1/1", "isotropic_population_exact_display_sum": "201/200",
        "isotropic_display_rounding_adverse_row_preserved": True,
        "ordered_population_order": ["tg", "tt", "pp", "pm"], "isotropic_population_order": ["tg", "tt", "pp", "pm"],
        "intramolecular_energy_cal_per_mol": {"tt_reference": "external conventional 0", "tg": "480", "pp": "658", "pm": "3263"},
        "fold_positive_energy_order": ["tt-structural-reference-EmptyOne", "tg-480", "pp-658", "pm-3263"],
        "fold_positive_energy_gaps": ["480", "178", "2605"], "Etg_300_cal_per_mol": "441 ± 114",
        "Etg_temperature_variation_cal_per_K_per_mol": "-1.9 ± 0.3", "all_external_signed_strings_retained_downstream": True,
    }


def main() -> None:
    if v1.TARGET_OUTPUT.exists() or v1.PRIMARY_OUTPUT.exists():
        raise SystemExit("ORG-006 corrected external artifacts already exist; preserved without regeneration")
    if hash_file(v1.IDENTITY_OUTPUT) != IDENTITY_HASH or hash_file(ROOT / "tools/build_chemistry_org_006_complete_external_v1.py") != V1_BUILDER_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 preserved v1 normalization boundary changed")
    identities = json.loads(v1.IDENTITY_OUTPUT.read_text(encoding="utf-8"))["rows"]
    for path, expected in (v1.V1_INVENTORY, v1.V2_INVENTORY, v1.V3_FAILURE, v1.V4_INVENTORY, v1.V5_INVENTORY):
        if hash_file(ROOT / path) != expected:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-006 capture changed: {path}")
    if hash_file(ROOT / v1.SI_PATH) != v1.SI_HASH or hash_file(ROOT / v1.PDF_PATH) != v1.PDF_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-006 quantitative source changed")
    v1inv = json.loads((ROOT / v1.V1_INVENTORY[0]).read_text()); v2inv = json.loads((ROOT / v1.V2_INVENTORY[0]).read_text())
    v3inv = json.loads((ROOT / v1.V3_FAILURE[0]).read_text()); v4inv = json.loads((ROOT / v1.V4_INVENTORY[0]).read_text()); v5inv = json.loads((ROOT / v1.V5_INVENTORY[0]).read_text())
    family = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1"; facts = corrected_pdf_facts(); si = v1.si_tables()
    outcomes = (
        {"complete_term_record": json.loads((family / "iupac-c01262.json").read_text())},
        {"complete_term_record": json.loads((family / "iupac-c01259.json").read_text())},
        {"complete_term_record": json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/goldbook-terms/CT01038.json").read_text())},
        {"complete_nist_surface": v1.html_surface("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/nist-cccbdb-106978-neutral-experimental.html")},
        {"complete_nist_surface": v1.html_surface("experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/nist-cccbdb-106978-internal-rotation.html")},
        *({"complete_blind_capture": row} for row in v1inv["rows"]),
        {"complete_source_group": v2inv["rows"][0]}, {"complete_source_group": v2inv["rows"][1]},
        {"complete_method_failure_and_metadata": v3inv},
        {"complete_acs_supporting_file": {"capture_inventory": v4inv, "measurement_tables": si}},
        {"complete_core_route": v5inv["captures"][0]},
        {"complete_core_route_and_quantitative_facts": {"capture": v5inv["captures"][1], "postseal_facts": facts}},
    )
    opened = (
        *((row["snapshot_path"], row["snapshot_sha256"]) for row in identities[:5]),
        *((row["snapshot_path"], row["snapshot_sha256"]) for row in v1inv["rows"]),
        (v1.V2_INVENTORY[0], v1.V2_INVENTORY[1]), (v1.V2_INVENTORY[0], v1.V2_INVENTORY[1]),
        (v1.V3_FAILURE[0], v1.V3_FAILURE[1]), (v1.V4_INVENTORY[0], v1.V4_INVENTORY[1]),
        (v1.V5_INVENTORY[0], v1.V5_INVENTORY[1]), (v1.V5_INVENTORY[0], v1.V5_INVENTORY[1]),
    )
    keys = ("target_id", "source_record_ordinal", "source_id", "authority", "registered_identity", "source_record_role", "custody_class")
    rows = []
    for identity, outcome, (path, digest) in zip(identities, outcomes, opened):
        row = {key: identity[key] for key in keys}; row.update({"opened_snapshot_path": path, "opened_snapshot_sha256": digest, "source_outcome": outcome})
        row["target_payload_hash"] = sha256_identity((identity["target_id"], identity["source_record_role"], outcome)); rows.append(row)
    target = {
        "schema": "sft-v3-complete-opened-target-vector/2", "claim_id": v1.CLAIM_ID,
        "identity_registry": [str(v1.IDENTITY_OUTPUT.relative_to(ROOT)), IDENTITY_HASH], "preserved_halted_builder": ["tools/build_chemistry_org_006_complete_external_v1.py", V1_BUILDER_HASH],
        "complete_registered_target_count": 14, "rows": rows, "all_favourable_adverse_absent_unavailable_unresolved_signed_and_rounded_rows_preserved": True,
        "unknown_target_value_blind_rows_present": True, "source_recapture_count": 0,
    }
    v1.TARGET_OUTPUT.write_text(json.dumps(target, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    analysis = {
        "schema": "sft-v3-postseal-primary-analysis/2", "claim_id": v1.CLAIM_ID, "complete_target_count": 14,
        "complete_target_vector_hash": sha256_identity(tuple(row["target_payload_hash"] for row in rows)),
        "blind_quantitative_pdf_obtained": True, "blind_quantitative_supporting_file_obtained": True,
        "acs_supporting_measurement_table_count": len(si), "acs_supporting_measurement_row_count": sum(len(table["rows"]) for table in si),
        "population_condition": facts["external_condition"], "ordered_population_vector": facts["ordered_population_vector"],
        "ordered_population_exact_display_fractions": facts["ordered_population_exact_display_fractions"], "ordered_population_exact_display_sum": "1/1",
        "ordered_population_order": facts["ordered_population_order"], "isotropic_population_vector": facts["isotropic_population_vector"],
        "isotropic_population_order": facts["isotropic_population_order"], "isotropic_population_exact_display_sum": "201/200",
        "isotropic_display_rounding_adverse_row_preserved": True, "fold_positive_energy_order": facts["fold_positive_energy_order"],
        "fold_positive_energy_gaps": facts["fold_positive_energy_gaps"], "Etg_300_cal_per_mol": facts["Etg_300_cal_per_mol"],
        "Etg_temperature_variation_cal_per_K_per_mol": facts["Etg_temperature_variation_cal_per_K_per_mol"],
        "condition_and_observation_timescale_retained": True, "external_signed_decimal_zero_negative_and_rounded_strings_are_downstream_only": True,
        "all_predecessor_failures_and_adverse_results_preserved": True,
    }
    v1.PRIMARY_OUTPUT.write_text(json.dumps(analysis, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(v1.TARGET_OUTPUT.relative_to(ROOT), hash_file(v1.TARGET_OUTPUT)); print(v1.PRIMARY_OUTPUT.relative_to(ROOT), hash_file(v1.PRIMARY_OUTPUT))
    print("targets", len(rows), "si tables", len(si), "si rows", sum(len(table["rows"]) for table in si))


if __name__ == "__main__":
    main()
