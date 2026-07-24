#!/usr/bin/env python3
"""Project the closed Mathematics owner ledger into global reconciliation status."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def write(path: str, payload: object): (ROOT / path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ledger = read("census/mathematics_prior_obligations.json")
    summary = ledger["mathematics_summary"]
    if ledger["status"] != "closed" or summary["open_count"] != 0:
        raise SystemExit("Mathematics owner ledger is not closed")

    v1 = read("audits/v1_theorem_manifest_observation_census.json")
    v2 = read("audits/v2_407_step_observation_census.json")
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}
    v2_rows = {row["step"]: row for row in v2["steps"]}
    composite_v1 = {"PH2", "PH3", "D9p", "D9m", "B9", "B10", "XIII-3", "G6", "G7", "G10", "G14", "G15"}
    composite_v2 = {3, 4, 89, 102, 103, 121, 124, 129, 158, 179, 185, 191, 192, 203, 205, 224, 288, 292, 306}
    for entry in ledger["source_entries"]:
        claims = sorted({claim for atom in entry["atomic_obligations"] for claim in atom["v3_claim_ids"]})
        if entry["source"] == "v1":
            row = v1_rows[entry["source_entry"]]; composite = entry["source_entry"] in composite_v1
        else:
            row = v2_rows[entry["source_entry"]]; composite = entry["source_entry"] in composite_v2
        row["explicit_v3_claim_ids"] = sorted(set(row.get("explicit_v3_claim_ids", ())).union(claims))
        row["missing_mapped_claim_ids"] = []
        row["explicit_mapping_status"] = "mapped_to_current_admitted_claims"
        if composite:
            row["same_strength_disposition"] = {
                "closed": False,
                "status": "mathematics_component_closed_other_owner_components_remain",
                "ledger": "census/mathematics_prior_obligations.json",
            }
        else:
            row["same_strength_disposition"] = {
                "closed": True,
                "status": "closed_by_atomic_mathematics_reconstruction",
                "ledger": "census/mathematics_prior_obligations.json",
            }

    for payload, key in ((v1, "rows"), (v2, "steps")):
        mapped = sum(bool(row.get("explicit_v3_claim_ids")) for row in payload[key])
        closed = sum(bool(row.get("same_strength_disposition", {}).get("closed")) for row in payload[key])
        if key == "rows":
            payload["mapped_row_count"] = mapped; payload["unmapped_row_count"] = len(payload[key]) - mapped
            payload["same_strength_closed_row_count"] = closed; payload["same_strength_open_row_count"] = len(payload[key]) - closed
        else:
            payload["mapped_step_count"] = mapped; payload["unmapped_step_count"] = len(payload[key]) - mapped
            payload["same_strength_closed_step_count"] = closed; payload["same_strength_open_step_count"] = len(payload[key]) - closed
        payload["status"] = "open_blocking" if closed != len(payload[key]) else "closed"
    write("audits/v1_theorem_manifest_observation_census.json", v1)
    write("audits/v2_407_step_observation_census.json", v2)

    ownership = read("census/prior_obligation_ownership.json")
    ownership["branch_summary"]["mathematics"] = {
        "status": "closed_same_strength",
        "branch_ledger": "census/mathematics_prior_obligations.json",
        "reviewed_source_entries": 763,
        "atomic_obligations": summary["atomic_obligation_count"],
        "open_obligations": 0,
        "explicit_corrections_or_invalidations": summary["explicit_correction_or_invalidation_count"],
    }
    ownership["next_required_action"] = "Continue the 763-entry branch-specific ownership and same-strength reconstruction with Information Science."
    write("census/prior_obligation_ownership.json", ownership)

    lineage = read("census/lineage_reconciliation.json")
    lineage["v1_manifest_census"]["explicitly_mapped_rows"] = v1["mapped_row_count"]
    lineage["v1_manifest_census"]["unmapped_rows"] = v1["unmapped_row_count"]
    lineage["v2_step_census"]["explicitly_mapped_steps"] = v2["mapped_step_count"]
    lineage["v2_step_census"]["unmapped_steps"] = v2["unmapped_step_count"]
    write("census/lineage_reconciliation.json", lineage)
    print(f"registered Mathematics closure: {summary['atomic_obligation_count']}/71; next=information_science")


if __name__ == "__main__": main()

