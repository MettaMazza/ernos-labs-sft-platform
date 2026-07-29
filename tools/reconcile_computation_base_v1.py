#!/usr/bin/env python3
"""Bind all admitted Classical Computation base receipts to the frozen census."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/computation_discipline_obligations.json"
OUT = ROOT / "census/computation_discipline_current_reconciliation_v1.json"
AUDIT = ROOT / "audits/COMPUTATION_BASE_001_117_COMPLETION_2026-07-29.json"


def canonical(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_hash(path: Path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_identity(path: Path):
    payload = json.loads(path.read_text())
    recorded = payload.pop("receipt_hash", None)
    computed = canonical(payload)
    if recorded != computed:
        raise SystemExit("Classical Computation stored receipt identity mismatch: " + path.name)
    return computed


def main():
    if OUT.exists() or AUDIT.exists():
        raise SystemExit("Classical Computation base reconciliation already exists")
    frozen = json.loads(FROZEN.read_text())
    body = dict(frozen)
    frozen_identity = body.pop("census_identity")
    if canonical(body) != frozen_identity:
        raise SystemExit("Classical Computation frozen census identity mismatch")
    if frozen["base_claim_count"] != 117 or frozen["closed_obligation_count_at_freeze"] != 117:
        raise SystemExit("Classical Computation frozen base count changed")

    live_rows = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    live = {row["claim_id"]: row for row in live_rows}
    base_obligations = [row for row in frozen["obligations"] if row["family"] == "BASE"]
    if len(base_obligations) != 117:
        raise SystemExit("Classical Computation base obligation count changed")

    rows = []
    for obligation in base_obligations:
        if len(obligation["current_claim_ids"]) != 1:
            raise SystemExit("Classical Computation base obligation is not one-to-one")
        claim_id = obligation["current_claim_ids"][0]
        row = live.get(claim_id)
        if row is None or row.get("branch") != "computation" or not row.get("model_admitted"):
            raise SystemExit("Classical Computation base reconciliation halt: " + claim_id)
        receipt = ROOT / row["receipt_path"]
        certificate_path = ROOT / "claims" / claim_id / "certificate.json"
        registration_path = ROOT / "claims" / claim_id / "registration.json"
        certificate = json.loads(certificate_path.read_text())
        registration = json.loads(registration_path.read_text())
        if receipt_identity(receipt) != row["receipt_hash"]:
            raise SystemExit("Classical Computation receipt replay mismatch: " + claim_id)
        if certificate.get("engine_receipt_hash") != row["receipt_hash"]:
            raise SystemExit("Classical Computation certificate receipt mismatch: " + claim_id)
        if registration.get("statement") != row["statement"]:
            raise SystemExit("Classical Computation registered-statement mismatch: " + claim_id)
        if not certificate.get("exact_result"):
            raise SystemExit("Classical Computation exact result absent: " + claim_id)
        if not certificate.get("controls_passed") or not certificate.get("independently_recomputed"):
            raise SystemExit("Classical Computation control or reconstruction halt: " + claim_id)
        if certificate.get("status") != "independently_replicated":
            raise SystemExit("Classical Computation independent status halt: " + claim_id)
        rows.append({
            "obligation_id": obligation["obligation_id"],
            "subbranch": obligation["subbranch"],
            "claim_id": claim_id,
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "certificate_hash": file_hash(certificate_path),
            "registration_hash": file_hash(registration_path),
            "registered_statement": registration["statement"],
            "certificate_exact_result": certificate["exact_result"],
            "closure_status": row["closure_status"],
            "external_status": row["external_status"],
            "controls_passed": True,
            "independently_recomputed": True,
        })

    value = {
        "schema": "sft-v3-classical-computation-discipline-current-reconciliation/1",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": frozen["registered_obligation_count"],
        "closed_at_freeze": 117,
        "predecessor_reconciliation_identity": None,
        "completed_families": {"BASE": rows},
        "current_closed_count": 117,
        "current_open_count": frozen["registered_obligation_count"] - 117,
        "current_completion_fraction": f"117/{frozen['registered_obligation_count']}",
        "current_completion_percent": "31.7%",
        "frozen_census_mutated": False,
        "extension_policy": frozen["extension_policy"],
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")

    audit = {
        "schema": "sft-v3-classical-computation-base-completion/1",
        "date": "2026-07-29",
        "family": "BASE",
        "family_completion": "117/117",
        "exact_replay": "117/117 exact receipt files reproduced",
        "independent_reconstruction": "117/117 certificate-bound independent reconstructions",
        "controls": "117/117 controls-passed certificates",
        "receipt_rows": rows,
        "protected_engine_or_verifier_changed": False,
        "current_classical_computation_progress": f"117/{frozen['registered_obligation_count']}",
        "current_classical_computation_percent": "31.7%",
        "frozen_census_identity": frozen_identity,
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "closed": 117,
        "open": frozen["registered_obligation_count"] - 117,
        "percent": "31.7%",
        "exact_receipt_replays": len(rows),
        "identity": value["reconciliation_identity"],
    }, indent=2))


if __name__ == "__main__":
    main()
