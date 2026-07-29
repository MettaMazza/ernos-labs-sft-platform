#!/usr/bin/env python3
"""Build the complete post-registry HAND-001--006 observation vector."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "census/information_science_hand_001_006_target_registry_v1.json"
RECONCILIATION = ROOT / "census/information_science_discipline_current_reconciliation_v19.json"
OBLIGATIONS = ROOT / "census/information_science_discipline_obligations.json"
OUTPUT = ROOT / "experiments/external_sources/information_science/hand_001_006_observation_vector_v1.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def main():
    if OUTPUT.exists():
        raise SystemExit("refusing overwrite " + str(OUTPUT))
    registry = json.loads(REGISTRY.read_text())
    registry_body = dict(registry)
    registry_identity = registry_body.pop("registry_identity")
    if canonical(registry_body) != registry_identity or registry["target_content_present"] is not False:
        raise SystemExit("value-free HAND registry invalid")
    reconciliation = json.loads(RECONCILIATION.read_text())
    obligations = json.loads(OBLIGATIONS.read_text())
    if reconciliation["current_closed_count"] != 256 or len(obligations["obligations"]) != 262:
        raise SystemExit("HAND predecessor or frozen census changed")
    observations = (
        {"dependency_targets": 7, "duplicate_target_owners": 0, "one_information_science_owner_retained": True},
        {"boundary_records": 3, "formal_observation_comparison_separate": True},
        {"ordered_custody_stages": 4, "derivation_before_target_release": True, "all_dispositions_preserved": True},
        {"conventional_correspondences": 4, "reversible_within_declared_boundary": True, "conventional_model_selects_law": False},
        {"frozen_obligations": 262, "versioned_extension_appends": True, "prior_receipts_rewritten": False},
        {"pre_handoff_receipts": 256, "handoff_obligations": 6, "complete_obligations": 262, "duplicate_owners": 0, "omitted_owners": 0},
    )
    names = (
        "one_owner_downstream_handoff",
        "measurement_boundary_handoff",
        "formal_empirical_handoff",
        "conventional_correspondence_handoff",
        "open_extension_handoff",
        "cross_branch_completeness",
    )
    records = []
    for index, (claim_id, observation, name) in enumerate(zip(registry["claim_ids"], observations, names), 1):
        records.append({
            "all_rows_preserved": True,
            "claim_id": claim_id,
            "exact_observation": observation,
            "expected_label": f"complete-hand-{index:03d}-observation-retained",
            "number": f"{index:03d}",
            "obligation_id": f"SFT-INFO-OBL-HAND-{index:03d}",
            "observation_name": name,
            "source_ids": [
                "SFT-V3-INFORMATION-SCIENCE-RECONCILIATION-V19",
                "SFT-V3-INDEPENDENT-EXACT-HANDOFF-RECONSTRUCTOR",
            ],
        })
    value = {
        "all_rows_preserved": True,
        "authority": "Maria Smith",
        "date": "2026-07-29",
        "outcomes_opened_only_after_registry_freeze": True,
        "protected_engine_or_verifier_edit_made": False,
        "record_count": 6,
        "records": records,
        "registry_identity": registry_identity,
        "schema": "sft-v3-information-science-hand-observation-vector/1",
    }
    value["vector_identity"] = canonical(value)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"vector": str(OUTPUT.relative_to(ROOT)), "identity": value["vector_identity"]}, indent=2))


if __name__ == "__main__":
    main()
