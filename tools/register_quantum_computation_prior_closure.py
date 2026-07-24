#!/usr/bin/env python3
"""Register Quantum Computation same-strength closure in the global censuses."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write(path: str, payload: object) -> None:
    (ROOT / path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ledger = read("census/quantum_computation_prior_obligations.json")
    summary = ledger["quantum_computation_summary"]
    if ledger["status"] != "closed" or summary["open_count"]:
        raise SystemExit("Quantum Computation owner ledger is not closed")
    v2 = read("audits/v2_407_step_observation_census.json")
    rows = {row["step"]: row for row in v2["steps"]}
    for entry in ledger["source_entries"]:
        row = rows[entry["source_entry"]]
        claims = sorted({claim for atom in entry["atomic_obligations"] for claim in atom["v3_claim_ids"]})
        row["explicit_v3_claim_ids"] = sorted(set(row.get("explicit_v3_claim_ids", ())).union(claims))
        row["missing_mapped_claim_ids"] = []
        row["explicit_mapping_status"] = "mapped_to_current_admitted_claims"
        if entry["source_entry"] == 402:
            row["same_strength_disposition"] = {"closed": True, "status": "closed_by_all_atomic_owner_reconstructions", "ledger": "census/quantum_computation_prior_obligations.json"}
        else:
            row["same_strength_disposition"] = {"closed": True, "status": "closed_by_atomic_quantum_computation_reconstruction", "ledger": "census/quantum_computation_prior_obligations.json"}
    v2["mapped_step_count"] = sum(bool(row.get("explicit_v3_claim_ids")) for row in v2["steps"])
    v2["unmapped_step_count"] = len(v2["steps"]) - v2["mapped_step_count"]
    v2["same_strength_closed_step_count"] = sum(bool(row.get("same_strength_disposition", {}).get("closed")) for row in v2["steps"])
    v2["same_strength_open_step_count"] = len(v2["steps"]) - v2["same_strength_closed_step_count"]
    v2["status"] = "closed" if not v2["same_strength_open_step_count"] else "open_blocking"
    write("audits/v2_407_step_observation_census.json", v2)
    ownership = read("census/prior_obligation_ownership.json")
    ownership["branch_summary"]["quantum_computation"] = {
        "status": "closed_same_strength", "branch_ledger": "census/quantum_computation_prior_obligations.json",
        "reviewed_source_entries": 763, "atomic_obligations": summary["atomic_obligation_count"],
        "open_obligations": 0, "new_same_strength_claims": 1,
        "external_validation_kind": "formal independent exact regeneration; natural measured value not applicable; physical quantum measurements remain Physics-owned",
    }
    ownership["next_required_action"] = "Continue the 763-entry branch-specific ownership, measured-value and same-strength reconstruction with Physics."
    write("census/prior_obligation_ownership.json", ownership)
    lineage = read("census/lineage_reconciliation.json")
    lineage["v2_step_census"]["explicitly_mapped_steps"] = v2["mapped_step_count"]
    lineage["v2_step_census"]["unmapped_steps"] = v2["unmapped_step_count"]
    write("census/lineage_reconciliation.json", lineage)
    print(f"registered Quantum Computation closure: {summary['atomic_obligation_count']}/{summary['atomic_obligation_count']}; next=physics")


if __name__ == "__main__":
    main()
