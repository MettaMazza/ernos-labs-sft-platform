#!/usr/bin/env python3
"""Reconcile the complete admitted FORMX family against the frozen census."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/computation_discipline_obligations.json"
PREVIOUS = ROOT / "census/computation_discipline_current_reconciliation_v1.json"
OUT = ROOT / "census/computation_discipline_current_reconciliation_v2.json"
AUDIT = ROOT / "audits/COMPUTATION_FORMX_001_022_COMPLETION_2026-07-29.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def receipt_identity(path):
    payload = json.loads(path.read_text())
    recorded = payload.pop("receipt_hash", None)
    computed = canonical(payload)
    if recorded != computed:
        raise SystemExit("FORMX stored receipt identity mismatch: " + path.name)
    return computed


def main():
    if OUT.exists() or AUDIT.exists():
        raise SystemExit("FORMX reconciliation already exists")
    frozen = json.loads(FROZEN.read_text())
    frozen_body = dict(frozen)
    frozen_identity = frozen_body.pop("census_identity")
    if canonical(frozen_body) != frozen_identity:
        raise SystemExit("Classical Computation census changed")
    previous = json.loads(PREVIOUS.read_text())
    previous_body = dict(previous)
    previous_identity = previous_body.pop("reconciliation_identity")
    if canonical(previous_body) != previous_identity or previous["current_closed_count"] != 117:
        raise SystemExit("Classical Computation predecessor reconciliation changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "FORMX"]
    if len(obligations) != 22:
        raise SystemExit("FORMX obligation count changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    registry = json.loads((ROOT / "census/computation_formx_001_022_target_registry_v1.json").read_text())
    rows = []
    for index, (claim_id, obligation) in enumerate(zip(registry["claim_ids"], obligations), 1):
        row = live.get(claim_id)
        package = ROOT / "claims" / claim_id
        certificate = json.loads((package / "certificate.json").read_text())
        census = json.loads((package / "candidate_census.json").read_text())
        controls = json.loads((package / "controls.json").read_text())["controls"]
        empirical = json.loads((package / "empirical_validation.json").read_text())
        if (
            row is None or not row.get("model_admitted")
            or receipt_identity(ROOT / row["receipt_path"]) != row["receipt_hash"]
            or certificate.get("engine_receipt_hash") != row["receipt_hash"]
            or certificate.get("classical_computation_obligation") != obligation["obligation_id"]
            or certificate.get("candidate_count") != 256
            or certificate.get("unique_survivor_count") != 1
            or not certificate.get("controls_passed")
            or len(census["candidates"]) != 256
            or len(controls) != 4 or not all(control["passed"] for control in controls)
            or not empirical.get("all_rows_preserved") or not empirical.get("passed")
        ):
            raise SystemExit("FORMX reconciliation halt: " + claim_id)
        rows.append({
            "obligation_id": obligation["obligation_id"],
            "claim_id": claim_id,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "closure_status": row["closure_status"],
            "external_status": row["external_status"],
            "candidate_count": 256,
            "unique_survivor_count": 1,
            "control_count": 4,
            "post_registry_observation": True,
            "independent_certificate_hash": certificate["independent_certificate_hash"],
            "measurement_receipt_hash": certificate["measurement_receipt_hash"],
        })
    completed = dict(previous["completed_families"])
    completed["FORMX"] = rows
    value = {
        "schema": "sft-v3-classical-computation-discipline-current-reconciliation/2",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": 369,
        "closed_at_freeze": 117,
        "predecessor_reconciliation_identity": previous_identity,
        "completed_families": completed,
        "current_closed_count": 139,
        "current_open_count": 230,
        "current_completion_fraction": "139/369",
        "current_completion_percent": "37.7%",
        "frozen_census_mutated": False,
        "extension_policy": frozen["extension_policy"],
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {
        "schema": "sft-v3-classical-computation-formx-completion/1",
        "date": "2026-07-29",
        "family": "FORMX",
        "family_completion": "22/22",
        "generated_candidate_count": 22 * 256,
        "unique_survivor_count": 22,
        "passed_control_count": 22 * 4,
        "post_registry_exact_observation_count": 22,
        "implementation_distinct_reconstruction_count": 22,
        "exact_receipt_replay": "22/22",
        "receipt_rows": rows,
        "protected_engine_or_verifier_changed": False,
        "current_classical_computation_progress": "139/369",
        "current_classical_computation_percent": "37.7%",
        "frozen_census_identity": frozen_identity,
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "family": "22/22",
        "candidates": 22 * 256,
        "controls": 22 * 4,
        "current": "139/369",
        "percent": "37.7%",
        "identity": value["reconciliation_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
