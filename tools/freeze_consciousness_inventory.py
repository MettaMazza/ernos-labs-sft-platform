#!/usr/bin/env python3
"""Freeze the complete foundational Consciousness obligation inventory."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.consciousness_cognitive_science.generated_law import CONSCIOUSNESS_BLUEPRINTS  # noqa: E402
from sft.consciousness_cognitive_science.obligations import CONSCIOUSNESS_OBLIGATIONS, FAMILY_ORDER  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    branches_path = ROOT / "census/branches.json"
    branches = json.loads(branches_path.read_text(encoding="utf-8"))
    branch = next(row for row in branches["branches"] if row["branch_id"] == "consciousness_cognitive_science")
    if branch["inventory_status"] not in {"registered_not_started", "foundation_frozen_0_of_72_registered_not_admitted"}:
        raise ValueError("Consciousness branch has an unexpected pre-freeze state")
    branch["inventory_status"] = "foundation_frozen_0_of_72_registered_not_admitted"
    branch["paper_status"] = "not_ready"
    write_json(branches_path, branches)

    audit = json.loads((ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.json").read_text(encoding="utf-8"))
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    admitted = {row["claim_id"] for row in census["claims"] if row.get("model_admitted") is True}
    blueprints = {row.claim_id: row for row in CONSCIOUSNESS_BLUEPRINTS}
    rows = []
    for position, obligation in enumerate(CONSCIOUSNESS_OBLIGATIONS, 1):
        payload = asdict(obligation)
        payload.update({"position": position, "candidate_count": 256, "unique_survivor": blueprints[obligation.claim_id].exact_result, "status": "model_admitted" if obligation.claim_id in admitted else "registered_not_admitted"})
        rows.append(payload)
    counts = Counter(row.family for row in CONSCIOUSNESS_OBLIGATIONS)
    inventory = {
        "schema": "sft-v3-consciousness-foundation-inventory/1",
        "branch_id": "consciousness_cognitive_science",
        "inventory_frozen": True,
        "inventory_date": "2026-07-27",
        "derivation_target": "current-evidence foundational closure, extension-open",
        "scope": "Observation and interior observation; access, report and phenomenal presence; binding and unity; subject, perspective and interiority; introspection; memory and identity; finite self-models; attention; cognition; substrate realization; qualia; and the specific red-of-red result.",
        "evidential_non_substitution_law": ["phenomenal occurrence", "first-person discrimination and report", "behaviour", "biological or neural correlation", "cognitive access", "computational representation", "physical stimulus and measurement", "substrate realization"],
        "prior_audit": "audits/consciousness_v1_v2_initial_atomic_ownership.json",
        "prior_audit_identity": audit["audit_identity"],
        "prior_atomic_question_count": audit["summary"]["total_atomic_question_count"],
        "inventory_completion_explanation": "The 46 atomic prior questions fix the inherited accountability surface. The current roadmap then contributes only nonduplicate carrier, relation, evidence-boundary and falsification obligations needed to make those questions testable. Their explicit union is the 72-row inventory below; the number is an output of the listed rows, not a target used to generate them.",
        "family_order": list(FAMILY_ORDER),
        "family_counts": {family: counts[family] for family in FAMILY_ORDER},
        "required_claim_count": len(rows),
        "required_claim_ids": [row.claim_id for row in CONSCIOUSNESS_OBLIGATIONS],
        "candidate_count": len(rows) * 256,
        "admitted_claim_count_at_freeze": sum(row.claim_id in admitted for row in CONSCIOUSNESS_OBLIGATIONS),
        "pre_source_complete_branch_seal": "experiments/sealed_predictions/consciousness_foundation_complete_pre_source.json",
        "external_source_identities_selected_at_freeze": False,
        "external_outcomes_opened_at_freeze": False,
        "unclassified_obligations": [],
        "foundation_frontier_obligations": [],
        "later_full_field_extensions": ["complete perceptual modalities", "pain and affect", "embodiment and multimodal phenomenology", "developmental and comparative consciousness", "complete altered-state and anaesthesia census", "nonhuman and artificial realization programmes", "collective-mind boundary", "clinical disorders handoff", "ethical consequences"],
        "obligations": rows,
    }
    inventory["inventory_hash"] = sha256_identity(inventory)
    write_json(ROOT / "publications/inventories/consciousness_cognitive_science.json", inventory)

    checkpoint_path = ROOT / "census/consciousness_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "foundation_inventory_frozen_predictions_not_yet_sealed",
        "foundation_required_claim_count": len(rows), "candidate_count": len(rows) * 256,
        "admitted_claim_count": sum(row.claim_id in admitted for row in CONSCIOUSNESS_OBLIGATIONS),
        "remaining_claim_count": len(rows) - sum(row.claim_id in admitted for row in CONSCIOUSNESS_OBLIGATIONS),
        "inventory_path": "publications/inventories/consciousness_cognitive_science.json",
        "inventory_hash": inventory["inventory_hash"],
        "next_exact_operation": "seal_complete_foundation_predictions_before_external_source_selection",
    })
    write_json(checkpoint_path, checkpoint)
    print(f"frozen Consciousness foundation inventory: {len(rows)} obligations; {len(rows) * 256} candidates; {inventory['inventory_hash']}")


if __name__ == "__main__":
    main()

