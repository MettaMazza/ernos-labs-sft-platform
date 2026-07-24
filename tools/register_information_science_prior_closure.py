#!/usr/bin/env python3
"""Project the closed Information Science owner ledger into reconciliation status."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def write(path: str, payload: object): (ROOT / path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


PURE_V1 = {"Q5", "Q6"}
PURE_V2 = {326, 328, 329, 348, 384, 385, 386, 387, 388, 389, 390}


def main() -> None:
    ledger = read("census/information_science_prior_obligations.json")
    summary = ledger["information_science_summary"]
    if ledger["status"] != "closed" or summary["open_count"] != 0:
        raise SystemExit("Information Science owner ledger is not closed")

    v1 = read("audits/v1_theorem_manifest_observation_census.json")
    v2 = read("audits/v2_407_step_observation_census.json")
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}; v2_rows = {row["step"]: row for row in v2["steps"]}
    for entry in ledger["source_entries"]:
        claims = sorted({claim for atom in entry["atomic_obligations"] for claim in atom["v3_claim_ids"]})
        if entry["source"] == "v1":
            row = v1_rows[entry["source_entry"]]; pure = entry["source_entry"] in PURE_V1
        else:
            row = v2_rows[entry["source_entry"]]; pure = entry["source_entry"] in PURE_V2
        row["explicit_v3_claim_ids"] = sorted(set(row.get("explicit_v3_claim_ids", ())).union(claims))
        row["missing_mapped_claim_ids"] = []
        row["explicit_mapping_status"] = "mapped_to_current_admitted_claims"
        if pure:
            row["same_strength_disposition"] = {"closed": True, "status": "closed_by_atomic_information_science_reconstruction", "ledger": "census/information_science_prior_obligations.json"}
        elif not row.get("same_strength_disposition", {}).get("closed"):
            row["same_strength_disposition"] = {"closed": False, "status": "information_science_component_closed_other_owner_components_remain", "ledger": "census/information_science_prior_obligations.json"}

    for payload, key in ((v1, "rows"), (v2, "steps")):
        mapped = sum(bool(row.get("explicit_v3_claim_ids")) for row in payload[key]); closed = sum(bool(row.get("same_strength_disposition", {}).get("closed")) for row in payload[key])
        if key == "rows":
            payload["mapped_row_count"] = mapped; payload["unmapped_row_count"] = len(payload[key]) - mapped
            payload["same_strength_closed_row_count"] = closed; payload["same_strength_open_row_count"] = len(payload[key]) - closed
        else:
            payload["mapped_step_count"] = mapped; payload["unmapped_step_count"] = len(payload[key]) - mapped
            payload["same_strength_closed_step_count"] = closed; payload["same_strength_open_step_count"] = len(payload[key]) - closed
        payload["status"] = "open_blocking" if closed != len(payload[key]) else "closed"
    write("audits/v1_theorem_manifest_observation_census.json", v1); write("audits/v2_407_step_observation_census.json", v2)

    ownership = read("census/prior_obligation_ownership.json")
    ownership["branch_summary"]["information_science"] = {
        "status": "closed_same_strength", "branch_ledger": "census/information_science_prior_obligations.json", "reviewed_source_entries": 763,
        "atomic_obligations": summary["atomic_obligation_count"], "open_obligations": 0,
        "external_validation_kind": "formal_independent_exact_regeneration; natural measured value not applicable to this formal branch",
    }
    ownership["next_required_action"] = "Continue the 763-entry branch-specific ownership and same-strength reconstruction with Classical Computation."
    write("census/prior_obligation_ownership.json", ownership)

    lineage = read("census/lineage_reconciliation.json")
    lineage["v1_manifest_census"]["explicitly_mapped_rows"] = v1["mapped_row_count"]; lineage["v1_manifest_census"]["unmapped_rows"] = v1["unmapped_row_count"]
    lineage["v2_step_census"]["explicitly_mapped_steps"] = v2["mapped_step_count"]; lineage["v2_step_census"]["unmapped_steps"] = v2["unmapped_step_count"]
    write("census/lineage_reconciliation.json", lineage)
    print(f"registered Information Science closure: {summary['atomic_obligation_count']}/{summary['atomic_obligation_count']}; next=computation")


if __name__ == "__main__": main()
