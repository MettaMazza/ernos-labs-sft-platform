#!/usr/bin/env python3
"""Frozen local publication gate for the Earth foundation paper."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "publication/earth_environment_foundation_publication_gate_spec_v1.json"
INVENTORY = ROOT / "publications/inventories/earth_environment.json"
INTEGRATION = ROOT / "audits/earth_environment_foundation_integration.json"
RECONCILIATION = ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.json"
SOURCE_AUDIT = ROOT / "experiments/earth_environment/source_feature_audit.json"
CENSUS = ROOT / "census/claims.json"
CHECKPOINT = ROOT / "census/earth_environment_continuation_checkpoint.json"
REQUIRED_PACKAGE_FILES = (
    "registration.json", "candidate_census.json", "elimination_receipt.json",
    "controls.json", "empirical_validation.json", "certificate.json",
    "WHY_DERIVATION_CHECK.md", "STATUS.md", "execution.py", "independent_validator.py",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    spec = load(SPEC)
    inventory = load(INVENTORY)
    integration = load(INTEGRATION)
    reconciliation = load(RECONCILIATION)
    source_audit = load(SOURCE_AUDIT)
    census = load(CENSUS)
    checkpoint = load(CHECKPOINT)
    assert spec["schema"] == "sft-v3-earth-environment-foundation-publication-gate-spec/1"
    assert spec["remote_publication_authorized"] is False
    assert spec["gate_conditions_selected_from_frozen_inventory_goal_and_roadmap_not_paper_outcome"] is True
    claim_ids = tuple(inventory["required_claim_ids"])
    expected = spec["required_claim_count"]
    assert inventory["schema"] == "sft-v3-earth-environment-foundation-inventory/1"
    assert inventory["inventory_frozen"] is True
    assert inventory["external_source_identities_selected_at_freeze"] is False
    assert inventory["external_outcomes_opened_at_freeze"] is False
    assert inventory["required_claim_count"] == len(claim_ids) == expected
    assert len(set(claim_ids)) == expected
    assert inventory["candidate_count"] == spec["required_candidate_count"]
    assert len(inventory["family_order"]) == spec["required_family_count"]
    assert inventory["prior_atomic_question_count"] == spec["required_prior_atom_count"]
    admitted = {row["claim_id"]: row for row in census["claims"] if row.get("model_admitted") is True}
    assert not [claim_id for claim_id in claim_ids if claim_id not in admitted]
    for claim_id in claim_ids:
        row = admitted[claim_id]
        assert row["branch"] == "earth_environment"
        assert row["closure_status"] == "depth_independent"
        assert row["external_status"] == "empirically_tested_and_independently_replicated"
        package = ROOT / "claims" / claim_id
        assert all((package / name).is_file() for name in REQUIRED_PACKAGE_FILES)
        certificate = load(package / "certificate.json")
        assert certificate["engine_receipt_hash"] == row["receipt_hash"]
        assert certificate["closure_scope"] == "depth_independent"
        assert certificate["controls_passed"] is True
        assert certificate["independently_recomputed"] is True
        assert certificate["all_external_rows_preserved"] is True
        assert certificate["external_evidence_selected_survivor"] is False
        assert certificate["formal_structure_relabelled_as_direct_measurement"] is False
        assert certificate["model_or_forecast_relabelled_as_observation"] is False
        assert certificate["registered_source_feature_count"] == spec["required_registered_feature_count"]
        assert certificate["present_source_feature_count"] == spec["required_present_feature_count"]
        assert certificate["absent_source_feature_count_preserved"] == spec["required_absent_feature_count_preserved"]
        assert certificate["transport_failure_rows_preserved"] == spec["required_failed_transport_count_preserved"]
    assert integration["status"] == "current_evidence_closed_extension_open"
    assert integration["claim_count"] == expected
    assert integration["candidate_count"] == spec["required_candidate_count"]
    assert integration["control_count"] == spec["required_control_count"]
    assert integration["family_count"] == spec["required_family_count"]
    assert integration["branch_never_permanently_locked"] is True
    assert integration["engine_or_protected_authority_modified"] is False
    assert all(row["passed"] is True for row in integration["claim_results"])
    assert all(row["status"] == "current_evidence_closed_extension_open" for row in integration["family_results"])
    assert integration["prior_atomic_reconciliation"]["closed"] == spec["required_prior_atom_count"]
    assert integration["prior_atomic_reconciliation"]["open"] == 0
    external = integration["external_evidence"]
    assert external["source_count"] == spec["required_external_source_count"]
    assert external["registered_feature_count"] == spec["required_registered_feature_count"]
    assert external["present_feature_count"] == spec["required_present_feature_count"]
    assert external["absent_feature_count_preserved"] == spec["required_absent_feature_count_preserved"]
    assert external["transport_failure_rows_preserved"] == spec["required_failed_transport_count_preserved"]
    quake = integration["earthquake_unit_exponent_comparison"]
    assert quake["first_mixed_catalog_adverse_preserved"]["passed"] is False
    assert quake["first_adverse_result_reclassified"] is False
    assert quake["independent_homogeneous_holdout_compatible"]["passed"] is True
    assert reconciliation["status"] == "current_evidence_closed_extension_open"
    assert reconciliation["same_strength_closed_atom_count"] == spec["required_prior_atom_count"]
    assert reconciliation["same_strength_open_atom_count"] == 0
    assert reconciliation["source_surface"]["total_v1_v2_entries_reviewed"] == 763
    assert source_audit["source_count"] == spec["required_external_source_count"]
    assert source_audit["registered_feature_count"] == spec["required_registered_feature_count"]
    assert source_audit["present_feature_count"] == spec["required_present_feature_count"]
    assert source_audit["absent_feature_count"] == spec["required_absent_feature_count_preserved"]
    assert source_audit["original_failed_transport_count"] == spec["required_failed_transport_count_preserved"]
    assert source_audit["failed_transports_preserved"] is True
    assert checkpoint["admitted_claim_count"] == expected and checkpoint["remaining_claim_count"] == 0
    assert checkpoint["protected_authority_modified"] is False and checkpoint["remote_publication_authorized"] is False
    paper = ROOT / spec["paper_path"]
    pdf = ROOT / spec["pdf_path"]
    metadata = load(ROOT / spec["metadata_path"])
    assert paper.is_file() and pdf.is_file()
    assert metadata["publication_authorized"] is False and metadata["zenodo_draft_id"] is None and metadata["doi"] == ""
    text = paper.read_text(encoding="utf-8")
    folded = " ".join(text.casefold().split())
    for required in (*spec["required_headline_topics"], *spec["required_evidence_distinctions"], *spec["required_mission_terms"], *spec["required_status_language"]):
        assert " ".join(required.casefold().split()) in folded, f"paper missing frozen requirement: {required}"
    for prohibited in ("todo", "tbd", "placeholder", "lorem ipsum", "turn0search", "turn1search"):
        assert prohibited not in folded, f"paper contains unresolved token: {prohibited}"
    assert text.count("External evidence selected the survivor: `false`.") == expected
    assert text.count("Formal structure relabelled as direct measurement: `false`.") == expected
    assert text.count("Model, forecast, proxy or retrieval relabelled as observation: `false`.") == expected
    reader = PdfReader(str(pdf))
    assert len(reader.pages) >= 200
    assert all(len((page.extract_text() or "").strip()) >= 20 for page in reader.pages)
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages).casefold()
    for required in ("from one world to earth", "maria smith", "ernos labs", "18469/1494", "253/27", "earth-ionosphere"):
        assert required in extracted, f"PDF missing: {required}"
    print(f"Earth foundation publication gate v1: PASS claims={expected} candidates={spec['required_candidate_count']} prior_atoms={spec['required_prior_atom_count']} pages={len(reader.pages)} publication_authorized=false")


if __name__ == "__main__":
    main()
