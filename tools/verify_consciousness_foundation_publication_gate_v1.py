#!/usr/bin/env python3
"""Frozen v1 publication gate for the Consciousness foundation paper."""

from __future__ import annotations

import json
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "publication/consciousness_foundation_publication_gate_spec_v1.json"
INVENTORY_PATH = ROOT / "publications/inventories/consciousness_cognitive_science.json"
INTEGRATION_PATH = ROOT / "audits/consciousness_foundation_integration.json"
RECONCILIATION_PATH = ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.json"
SOURCE_AUDIT_PATH = ROOT / "experiments/consciousness/source_feature_audit.json"
CENSUS_PATH = ROOT / "census/claims.json"
CHECKPOINT_PATH = ROOT / "census/consciousness_continuation_checkpoint.json"

REQUIRED_PACKAGE_FILES = (
    "registration.json",
    "candidate_census.json",
    "elimination_receipt.json",
    "controls.json",
    "empirical_validation.json",
    "certificate.json",
    "WHY_DERIVATION_CHECK.md",
    "STATUS.md",
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    spec = load(SPEC_PATH)
    inventory = load(INVENTORY_PATH)
    integration = load(INTEGRATION_PATH)
    reconciliation = load(RECONCILIATION_PATH)
    source_audit = load(SOURCE_AUDIT_PATH)
    census = load(CENSUS_PATH)
    checkpoint = load(CHECKPOINT_PATH)

    assert spec["schema"] == "sft-v3-consciousness-foundation-publication-gate-spec/1"
    assert spec["remote_publication_authorized"] is False
    assert spec["gate_conditions_selected_from_frozen_inventory_goal_and_roadmap_not_paper_outcome"] is True

    claim_ids = tuple(inventory["required_claim_ids"])
    expected_claims = spec["required_claim_count"]
    assert inventory["schema"] == "sft-v3-consciousness-foundation-inventory/1"
    assert inventory["inventory_frozen"] is True
    assert inventory["external_source_identities_selected_at_freeze"] is False
    assert inventory["external_outcomes_opened_at_freeze"] is False
    assert inventory["required_claim_count"] == len(claim_ids) == expected_claims
    assert len(set(claim_ids)) == expected_claims
    assert inventory["candidate_count"] == spec["required_candidate_count"]
    assert len(inventory["family_order"]) == spec["required_family_count"]
    assert inventory["prior_atomic_question_count"] == spec["required_prior_atom_count"]

    admitted = {
        row["claim_id"]: row
        for row in census["claims"]
        if row.get("model_admitted") is True
    }
    missing = [claim_id for claim_id in claim_ids if claim_id not in admitted]
    assert not missing, f"missing Consciousness admissions: {missing}"
    for claim_id in claim_ids:
        row = admitted[claim_id]
        assert row["branch"] == "consciousness_cognitive_science"
        assert row["closure_status"] == "depth_independent"
        assert row["external_status"] == "empirically_tested_and_independently_replicated"
        package = ROOT / "claims" / claim_id
        for name in REQUIRED_PACKAGE_FILES:
            assert (package / name).is_file(), f"missing {claim_id}/{name}"
        certificate = load(package / "certificate.json")
        assert certificate["engine_receipt_hash"] == row["receipt_hash"]
        assert certificate["closure_scope"] == "depth_independent"
        assert certificate["controls_passed"] is True
        assert certificate["independently_recomputed"] is True
        assert certificate["all_external_rows_preserved"] is True
        assert certificate["formal_structure_relabelled_as_empirical_phenomenal_fact"] is False
        assert certificate["phenomenal_occurrence_directly_observed_by_third_person"] is False
        assert certificate["registered_source_feature_count"] == spec["required_registered_feature_count"]
        assert certificate["present_source_feature_count"] == spec["required_present_feature_count"]
        assert certificate["absent_source_feature_count_preserved"] == spec["required_absent_feature_count_preserved"]
        assert certificate["transport_or_content_failure_rows_preserved"] == spec["required_transport_or_content_failure_rows_preserved"]

    assert integration["status"] == "current_evidence_closed_extension_open"
    assert integration["claim_count"] == expected_claims
    assert integration["candidate_count"] == spec["required_candidate_count"]
    assert integration["family_count"] == spec["required_family_count"]
    assert integration["branch_never_permanently_locked"] is True
    assert integration["engine_or_protected_authority_modified"] is False
    assert len(integration["claim_results"]) == expected_claims
    assert all(row["passed"] is True for row in integration["claim_results"])
    assert all(row["status"] == "current_evidence_closed_extension_open" for row in integration["family_results"])
    assert integration["prior_atomic_reconciliation"]["closed"] == spec["required_prior_atom_count"]
    assert integration["prior_atomic_reconciliation"]["open"] == 0
    external = integration["external_evidence"]
    assert external["source_count"] == spec["required_external_source_count"]
    assert external["registered_feature_count"] == spec["required_registered_feature_count"]
    assert external["present_feature_count"] == spec["required_present_feature_count"]
    assert external["absent_feature_count_preserved"] == spec["required_absent_feature_count_preserved"]
    assert external["transport_or_content_failure_rows_preserved"] == spec["required_transport_or_content_failure_rows_preserved"]
    assert external["claim_targets_passed"] == expected_claims
    assert external["claim_targets_unresolved"] == 0

    assert reconciliation["status"] == "current_evidence_closed_extension_open"
    assert reconciliation["atom_count"] == spec["required_prior_atom_count"]
    assert reconciliation["same_strength_closed_atom_count"] == spec["required_prior_atom_count"]
    assert reconciliation["same_strength_open_atom_count"] == 0
    assert reconciliation["all_engine_receipts_present"] is True
    assert reconciliation["prior_answers_used_as_v3_premises"] is False
    assert reconciliation["source_surface"]["total_v1_v2_entries_reviewed"] == 763

    assert source_audit["source_count"] == spec["required_external_source_count"]
    assert source_audit["registered_feature_count"] == spec["required_registered_feature_count"]
    assert source_audit["present_feature_count"] == spec["required_present_feature_count"]
    assert source_audit["absent_feature_count"] == spec["required_absent_feature_count_preserved"]
    assert source_audit["absence_is_not_relabelled_as_support"] is True
    assert source_audit["all_transport_and_content_failures_preserved"] is True

    assert checkpoint["status"] == "foundational_branch_current_evidence_closed_extension_open"
    assert checkpoint["admitted_claim_count"] == expected_claims
    assert checkpoint["remaining_claim_count"] == 0
    assert checkpoint["external_target_passed_claim_count"] == expected_claims
    assert checkpoint["external_target_unresolved_claim_count"] == 0
    assert checkpoint["protected_authority_modified"] is False
    assert checkpoint["remote_publication_authorized"] is False
    assert checkpoint["next_exact_operation"] == "await_explicit_commit_push_and_publication_authorization"

    paper = ROOT / spec["paper_path"]
    pdf = ROOT / spec["pdf_path"]
    metadata_path = ROOT / spec["metadata_path"]
    assert paper.is_file() and pdf.is_file() and metadata_path.is_file()
    metadata = load(metadata_path)
    assert metadata["publication_authorized"] is False
    assert metadata["zenodo_draft_id"] is None
    assert metadata["doi"] == ""

    paper_text = paper.read_text(encoding="utf-8")
    folded = paper_text.casefold()
    for required in (*spec["required_headline_topics"], *spec["required_evidence_distinctions"], *spec["required_mission_terms"], *spec["required_status_language"]):
        assert required.casefold() in folded, f"paper missing frozen requirement: {required}"
    for prohibited in ("todo", "tbd", "placeholder", "lorem ipsum", "turn0search", "turn1search"):
        assert prohibited not in folded, f"paper contains unresolved token: {prohibited}"
    assert paper_text.count("Phenomenal occurrence claimed as directly third-person possessed: `false`.") == expected_claims
    assert paper_text.count("Formal structure relabelled as empirical phenomenal fact: `false`.") == expected_claims

    reader = PdfReader(str(pdf))
    assert len(reader.pages) == 259
    extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    assert all(len((page.extract_text() or "").strip()) >= 20 for page in reader.pages)
    for required in ("From Fold to Consciousness", "Maria Smith", "Ernos Labs", "hard problem", "substrate independence", "red-of-red"):
        assert required.casefold() in extracted.casefold(), f"PDF missing: {required}"

    print(
        "Consciousness foundation publication gate v1: PASS "
        f"claims={expected_claims} candidates={spec['required_candidate_count']} "
        f"prior_atoms={spec['required_prior_atom_count']} pages={len(reader.pages)} "
        "publication_authorized=false"
    )


if __name__ == "__main__":
    main()
