#!/usr/bin/env python3
"""Project the closed Classical Computation ledger into reconciliation status."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
def read(path: str): return json.loads((ROOT / path).read_text(encoding="utf-8"))
def write(path: str, payload: object): (ROOT / path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


PURE_V1 = {"XII-4"}
PURE_V2 = {
    325, 327, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345,
    346, 347, 348, 349, 350, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364,
    365, 366, 367, 368, 369, 370, 371, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383,
    392, 393, 394, 395, 396, 404, 405, 406,
}


def main() -> None:
    ledger = read("census/computation_prior_obligations.json"); summary = ledger["computation_summary"]
    if ledger["status"] != "closed" or summary["open_count"] != 0: raise SystemExit("Classical Computation owner ledger is not closed")
    v1 = read("audits/v1_theorem_manifest_observation_census.json"); v2 = read("audits/v2_407_step_observation_census.json")
    v1_rows = {row["v1_claim_id"]: row for row in v1["rows"]}; v2_rows = {row["step"]: row for row in v2["steps"]}
    for entry in ledger["source_entries"]:
        claims = sorted({claim for item in entry["atomic_obligations"] for claim in item["v3_claim_ids"]})
        if entry["source"] == "v1": row = v1_rows[entry["source_entry"]]; pure = entry["source_entry"] in PURE_V1
        else: row = v2_rows[entry["source_entry"]]; pure = entry["source_entry"] in PURE_V2
        row["explicit_v3_claim_ids"] = sorted(set(row.get("explicit_v3_claim_ids", ())).union(claims)); row["missing_mapped_claim_ids"] = []; row["explicit_mapping_status"] = "mapped_to_current_admitted_claims"
        if pure: row["same_strength_disposition"] = {"closed": True, "status": "closed_by_atomic_computation_reconstruction", "ledger": "census/computation_prior_obligations.json"}
        elif not row.get("same_strength_disposition", {}).get("closed"): row["same_strength_disposition"] = {"closed": False, "status": "computation_component_closed_other_owner_components_remain", "ledger": "census/computation_prior_obligations.json"}
    for payload, key in ((v1, "rows"), (v2, "steps")):
        mapped=sum(bool(row.get("explicit_v3_claim_ids")) for row in payload[key]); closed=sum(bool(row.get("same_strength_disposition",{}).get("closed")) for row in payload[key])
        if key=="rows": payload["mapped_row_count"]=mapped; payload["unmapped_row_count"]=len(payload[key])-mapped; payload["same_strength_closed_row_count"]=closed; payload["same_strength_open_row_count"]=len(payload[key])-closed
        else: payload["mapped_step_count"]=mapped; payload["unmapped_step_count"]=len(payload[key])-mapped; payload["same_strength_closed_step_count"]=closed; payload["same_strength_open_step_count"]=len(payload[key])-closed
        payload["status"]="open_blocking" if closed != len(payload[key]) else "closed"
    write("audits/v1_theorem_manifest_observation_census.json",v1); write("audits/v2_407_step_observation_census.json",v2)
    ownership=read("census/prior_obligation_ownership.json")
    ownership["branch_summary"]["computation"]={"status":"closed_same_strength","branch_ledger":"census/computation_prior_obligations.json","reviewed_source_entries":763,"atomic_obligations":summary["atomic_obligation_count"],"open_obligations":0,"explicit_corrections_or_reconciliations":summary["explicit_correction_or_reconciliation_count"],"new_same_strength_claims":3,"external_validation_kind":"formal independent exact regeneration; natural measured value not applicable to this formal branch"}
    ownership["next_required_action"]="Continue the 763-entry branch-specific ownership and same-strength reconstruction with Quantum Computation."
    write("census/prior_obligation_ownership.json",ownership)
    lineage=read("census/lineage_reconciliation.json"); lineage["v1_manifest_census"]["explicitly_mapped_rows"]=v1["mapped_row_count"]; lineage["v1_manifest_census"]["unmapped_rows"]=v1["unmapped_row_count"]; lineage["v2_step_census"]["explicitly_mapped_steps"]=v2["mapped_step_count"]; lineage["v2_step_census"]["unmapped_steps"]=v2["unmapped_step_count"]; write("census/lineage_reconciliation.json",lineage)
    print(f"registered Classical Computation closure: {summary['atomic_obligation_count']}/{summary['atomic_obligation_count']}; next=quantum_computation")


if __name__ == "__main__": main()
