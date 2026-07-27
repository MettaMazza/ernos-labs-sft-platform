#!/usr/bin/env python3
"""Frozen v1 publication gate for the foundational Biology branch."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CLAIMS = 75
EXPECTED_PRIOR_ATOMS = 30


def main() -> None:
    inventory = json.loads((ROOT / "publications/inventories/biology.json").read_text(encoding="utf-8"))
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    audit = json.loads((ROOT / "audits/biology_v1_v2_atomic_ownership.json").read_text(encoding="utf-8"))
    checkpoint = json.loads((ROOT / "census/biology_continuation_checkpoint.json").read_text(encoding="utf-8"))
    claim_ids = tuple(inventory["required_claim_ids"])
    admitted = {row["claim_id"]: row for row in census["claims"] if row.get("model_admitted") is True}
    assert inventory["schema"] == "sft-v3-biology-foundation-inventory/1"
    assert inventory["inventory_frozen"] is True
    assert inventory["required_claim_count"] == len(claim_ids) == EXPECTED_CLAIMS
    assert inventory["candidate_count"] == EXPECTED_CLAIMS * 256
    assert len(set(claim_ids)) == EXPECTED_CLAIMS
    missing = [claim_id for claim_id in claim_ids if claim_id not in admitted]
    assert not missing, f"missing Biology admissions: {missing}"
    for claim_id in claim_ids:
        row = admitted[claim_id]
        assert row["branch"] == "biology"
        assert row["closure_status"] == "depth_independent"
        assert row["external_status"] == "empirically_tested_and_independently_replicated"
        package = ROOT / "claims" / claim_id
        for name in ("registration.json", "candidate_census.json", "elimination_receipt.json", "controls.json", "empirical_validation.json", "certificate.json", "WHY_DERIVATION_CHECK.md", "STATUS.md"):
            assert (package / name).is_file(), f"missing {claim_id}/{name}"
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8"))
        assert certificate["engine_receipt_hash"] == row["receipt_hash"]
        assert certificate["controls_passed"] is True
        assert certificate["independently_recomputed"] is True
        assert certificate["all_external_rows_preserved"] is True
        assert certificate["specimen_dependent_magnitude_claimed_as_universal"] is False
    assert audit["source_surface"]["total_source_rows_reviewed"] == 763
    assert audit["summary"]["biology_owned_atom_count"] == EXPECTED_PRIOR_ATOMS
    assert audit["summary"]["same_strength_closed_atom_count"] == EXPECTED_PRIOR_ATOMS
    assert audit["summary"]["same_strength_open_atom_count"] == 0
    assert audit["audit_status"] == "current_evidence_closed_extension_open"
    assert checkpoint["status"] == "foundational_branch_current_evidence_closed_extension_open"
    assert checkpoint["admitted_claim_count"] == EXPECTED_CLAIMS
    assert checkpoint["next_exact_operation"] == "proofread_and_stage_biology_foundation_without_remote_publication"
    paper = ROOT / "publications/current/biology/FROM_FOLD_TO_LIFE.md"
    pdf = ROOT / "output/pdf/from-fold-to-life-biology-foundation-paper-001-v1.0.pdf"
    metadata = ROOT / "publication/biology_foundation_zenodo_metadata.json"
    assert paper.is_file() and pdf.is_file() and metadata.is_file()
    publication_metadata = json.loads(metadata.read_text(encoding="utf-8"))
    assert publication_metadata["publication_authorized"] is False
    assert publication_metadata["zenodo_draft_id"] is None
    assert publication_metadata["doi"] == ""
    paper_text = paper.read_text(encoding="utf-8")
    for required in ("Maria Smith", "Ernos Labs", "There Is No Nothing", "75", "19,200", "four", "sixty-four", "sixteen", "scale-free", "allometric", "open-source science", "Maria.Smith.Sftoe@gmail.com", "https://discord.gg/ucwGryVxGr", "https://github.com/MettaMazza"):
        assert required.casefold() in paper_text.casefold(), f"paper missing {required}"
    print(f"Biology foundation publication gate v1: PASS claims={EXPECTED_CLAIMS} prior_atoms={EXPECTED_PRIOR_ATOMS}")


if __name__ == "__main__":
    main()
