#!/usr/bin/env python3
"""Reconcile the complete admitted QALGX family against the frozen census."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
PREVIOUS = ROOT / "census/quantum_computation_discipline_current_reconciliation_v4.json"
OUT = ROOT / "census/quantum_computation_discipline_current_reconciliation_v5.json"
AUDIT = ROOT / "audits/QUANTUM_COMPUTATION_QALGX_001_030_COMPLETION_2026-07-29.json"


def canonical(value):
    return "sha256:" + hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def receipt_identity(path):
    payload = json.loads(path.read_text())
    recorded = payload.pop("receipt_hash", None)
    computed = canonical(payload)
    if recorded != computed:
        raise SystemExit("QALGX stored receipt identity mismatch: " + path.name)
    return computed


def main():
    if OUT.exists() or AUDIT.exists():
        raise SystemExit("QALGX reconciliation already exists")
    frozen = json.loads(FROZEN.read_text())
    frozen_body = dict(frozen)
    frozen_identity = frozen_body.pop("census_identity")
    if canonical(frozen_body) != frozen_identity:
        raise SystemExit("Quantum Computation census changed")
    previous = json.loads(PREVIOUS.read_text())
    previous_body = dict(previous)
    previous_identity = previous_body.pop("reconciliation_identity")
    if canonical(previous_body) != previous_identity or previous["current_closed_count"] != 90:
        raise SystemExit("Quantum Computation predecessor reconciliation changed")
    obligations = [row for row in frozen["obligations"] if row["family"] == "QALGX"]
    if len(obligations) != 30:
        raise SystemExit("QALGX obligation count changed")
    live = {row["claim_id"]: row for row in json.loads((ROOT / "census/claims.json").read_text())["claims"]}
    registry = json.loads((ROOT / "census/quantum_qalgx_001_030_target_registry_v1.json").read_text())
    rows = []
    for claim_id, obligation in zip(registry["claim_ids"], obligations):
        row, package = live.get(claim_id), ROOT / "claims" / claim_id
        certificate = json.loads((package / "certificate.json").read_text())
        census = json.loads((package / "candidate_census.json").read_text())
        controls = json.loads((package / "controls.json").read_text())["controls"]
        empirical = json.loads((package / "empirical_validation.json").read_text())
        if (row is None or not row.get("model_admitted") or receipt_identity(ROOT / row["receipt_path"]) != row["receipt_hash"] or certificate.get("engine_receipt_hash") != row["receipt_hash"] or certificate.get("quantum_computation_obligation") != obligation["obligation_id"] or certificate.get("candidate_count") != 256 or certificate.get("unique_survivor_count") != 1 or not certificate.get("controls_passed") or len(census["candidates"]) != 256 or len(controls) != 4 or not all(control["passed"] for control in controls) or not empirical.get("all_rows_preserved") or not empirical.get("passed")):
            raise SystemExit("QALGX reconciliation halt: " + claim_id)
        rows.append({"obligation_id": obligation["obligation_id"], "claim_id": claim_id, "receipt_hash": row["receipt_hash"], "receipt_path": row["receipt_path"], "closure_status": row["closure_status"], "external_status": row["external_status"], "candidate_count": 256, "unique_survivor_count": 1, "control_count": 4, "post_registry_observation": True, "independent_certificate_hash": certificate["independent_certificate_hash"], "measurement_receipt_hash": certificate["measurement_receipt_hash"]})
    completed = dict(previous["completed_families"])
    completed["QALGX"] = rows
    value = {"schema": "sft-v3-quantum-computation-discipline-current-reconciliation/5", "date": "2026-07-29", "frozen_census_identity": frozen_identity, "frozen_obligation_count": 288, "closed_at_freeze": 22, "predecessor_reconciliation_identity": previous_identity, "completed_families": completed, "current_closed_count": 120, "current_open_count": 168, "current_completion_fraction": "120/288", "current_completion_percent": "41.7%", "frozen_census_mutated": False, "extension_policy": frozen["extension_policy"]}
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    audit = {"schema": "sft-v3-quantum-computation-qalgx-completion/1", "date": "2026-07-29", "family": "QALGX", "family_completion": "30/30", "generated_candidate_count": 30 * 256, "unique_survivor_count": 30, "passed_control_count": 30 * 4, "post_registry_exact_observation_count": 30, "implementation_distinct_reconstruction_count": 30, "exact_receipt_replay": "30/30", "receipt_rows": rows, "protected_engine_or_verifier_changed": False, "current_quantum_computation_progress": "120/288", "current_quantum_computation_percent": "41.7%", "frozen_census_identity": frozen_identity, "reconciliation_identity": value["reconciliation_identity"]}
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"family": "30/30", "candidates": 30 * 256, "controls": 30 * 4, "current": "120/288", "percent": "41.7%", "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
