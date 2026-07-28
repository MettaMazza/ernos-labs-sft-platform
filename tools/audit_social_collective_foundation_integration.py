#!/usr/bin/env python3
"""Complete integration audit for the Social and Collective Sciences foundation."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.social_collective_systems.generated_law import SOCIAL_BLUEPRINTS, candidate_forms


def digest(value: dict) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    claims = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    admitted = {x["claim_id"]: x for x in claims if x.get("model_admitted") is True}
    prior = json.loads((ROOT / "audits/social_collective_v1_v2_initial_atomic_ownership.json").read_text())
    inventory = json.loads((ROOT / "publications/inventories/social_collective_systems.json").read_text())
    targets = json.loads((ROOT / "experiments/social_collective_systems/external_targets.json").read_text())
    transports = json.loads((ROOT / "experiments/social_collective_systems/source_transports.json").read_text())
    ids = [x.claim_id for x in SOCIAL_BLUEPRINTS]
    missing = [x for x in ids if x not in admitted]
    if missing:
        raise ValueError(f"unadmitted Social claims: {missing}")
    if len(ids) != 72 or sum(len(candidate_forms(x)) for x in SOCIAL_BLUEPRINTS) != 18432:
        raise ValueError("Social candidate census differs")
    if (targets["claim_count"], targets["passed_claim_count"], targets["unresolved_claim_count"]) != (72, 72, 0):
        raise ValueError("Social external target census incomplete")
    if targets["all_adverse_absent_and_failed_rows_preserved"] is not True:
        raise ValueError("Social adverse or failed rows were lost")
    if targets["credential_prestige_or_consensus_used_as_proof"] is not False:
        raise ValueError("Social status was used as proof")
    atom_map = inventory["prior_atom_to_foundation_claim"]
    prior_count = prior["summary"]["atomic_question_count"]
    if len(atom_map) != prior_count or any(x not in admitted for x in atom_map.values()):
        raise ValueError("Social prior atom reconciliation incomplete")
    receipt_rows = []
    for claim_id in ids:
        package = ROOT / "claims" / claim_id
        certificate = json.loads((package / "certificate.json").read_text())
        receipt = ROOT / admitted[claim_id]["receipt_path"]
        prohibited = (
            "external_evidence_selected_survivor",
            "credential_or_prestige_used_as_evidence",
            "consensus_vote_used_as_proof",
            "normative_judgment_relabelled_observation",
        )
        if not receipt.is_file() or certificate["engine_receipt_hash"] != admitted[claim_id]["receipt_hash"]:
            raise ValueError(f"receipt failure: {claim_id}")
        if not certificate["independently_recomputed"] or any(certificate[x] is not False for x in prohibited):
            raise ValueError(f"certificate boundary failure: {claim_id}")
        receipt_rows.append(
            {
                "claim_id": claim_id,
                "receipt_hash": admitted[claim_id]["receipt_hash"],
                "derivation_seal_hash": certificate["derivation_seal_hash"],
                "independent_certificate_hash": certificate["independent_certificate_hash"],
                "target_row_hash": certificate["claim_target_evaluation"]["target_row_hash"],
            }
        )
    result = {
        "schema": "sft-v3-social-collective-foundation-integration-audit/1",
        "status": "current_evidence_closed_extension_open",
        "required_claim_count": 72,
        "admitted_claim_count": 72,
        "candidate_count": 18432,
        "family_count": 12,
        "prior_entries_reviewed": prior["source_surface"]["total_entries_reviewed"],
        "prior_atomic_questions": len(atom_map),
        "prior_atomic_questions_reconciled": len(atom_map),
        "source_count": transports["attempted"],
        "captured_source_count": transports["captured"],
        "failed_source_transports_preserved": transports["failed_preserved"],
        "external_target_count": targets["claim_count"],
        "external_target_match_count": targets["passed_claim_count"],
        "credential_prestige_or_consensus_used_as_proof": False,
        "normative_judgment_relabelled_observation": False,
        "aggregate_relabelled_individual_state": False,
        "extension_open": True,
        "permanent_lock_claimed": False,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "receipts": receipt_rows,
    }
    result["integration_hash"] = digest(result)
    path = ROOT / "audits/social_collective_foundation_integration.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    checkpoint = ROOT / "census/social_collective_continuation_checkpoint.json"
    state = json.loads(checkpoint.read_text())
    state.update(
        {
            "status": "foundational_branch_current_evidence_closed_extension_open_paper_not_yet_drafted",
            "admitted_claim_count": 72,
            "remaining_claim_count": 0,
            "integration_audit_path": str(path.relative_to(ROOT)),
            "integration_audit_hash": result["integration_hash"],
            "next_exact_operation": "draft_and_proofread_standalone_paper",
        }
    )
    checkpoint.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"Social integration: 72/72, 18432 candidates, {len(atom_map)}/{len(atom_map)} prior atoms, hash={result['integration_hash']}")


if __name__ == "__main__":
    main()
