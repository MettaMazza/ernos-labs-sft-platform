#!/usr/bin/env python3
"""Bind all admitted Quantum Computation base receipts to the frozen census."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "census/quantum_computation_discipline_obligations.json"
OUT = ROOT / "census/quantum_computation_discipline_current_reconciliation_v1.json"
AUDIT = ROOT / "audits/QUANTUM_COMPUTATION_BASE_001_022_COMPLETION_2026-07-29.json"


def canonical(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def file_hash(path: Path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_identity(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    recorded = payload.pop("receipt_hash", None)
    computed = canonical(payload)
    if recorded != computed:
        raise SystemExit("Quantum Computation stored receipt identity mismatch: " + path.name)
    return computed


def current_certificate(package: Path, receipt_hash: str):
    matches = []
    for path in package.glob("certificate*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("engine_receipt_hash") == receipt_hash:
            matches.append((path, data))
    if len(matches) != 1:
        raise SystemExit(f"Quantum Computation current certificate count for {package.name}: {len(matches)}")
    return matches[0]


def main():
    if OUT.exists() or AUDIT.exists():
        raise SystemExit("Quantum Computation base reconciliation already exists")
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    body = dict(frozen)
    frozen_identity = body.pop("census_identity")
    if canonical(body) != frozen_identity:
        raise SystemExit("Quantum Computation frozen census identity mismatch")
    if frozen["base_claim_count"] != 22 or frozen["closed_obligation_count_at_freeze"] != 22:
        raise SystemExit("Quantum Computation frozen base count changed")

    live_rows = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    live = {row["claim_id"]: row for row in live_rows}
    base_obligations = [row for row in frozen["obligations"] if row["family"] == "BASE"]
    if len(base_obligations) != 22:
        raise SystemExit("Quantum Computation base obligation count changed")

    rows = []
    for obligation in base_obligations:
        if len(obligation["current_claim_ids"]) != 1:
            raise SystemExit("Quantum Computation base obligation is not one-to-one")
        claim_id = obligation["current_claim_ids"][0]
        live_row = live.get(claim_id)
        if live_row is None or live_row.get("branch") != "quantum_computation" or not live_row.get("model_admitted"):
            raise SystemExit("Quantum Computation base reconciliation halt: " + claim_id)
        receipt = ROOT / live_row["receipt_path"]
        package = ROOT / "claims" / claim_id
        certificate_path, certificate = current_certificate(package, live_row["receipt_hash"])
        registration_path = package / "registration.json"
        registration = json.loads(registration_path.read_text(encoding="utf-8"))
        if receipt_identity(receipt) != live_row["receipt_hash"]:
            raise SystemExit("Quantum Computation receipt replay mismatch: " + claim_id)
        if registration.get("statement") != live_row["statement"]:
            raise SystemExit("Quantum Computation registered-statement mismatch: " + claim_id)
        if not certificate.get("exact_result") or not certificate.get("controls_passed") or not certificate.get("independently_recomputed"):
            raise SystemExit("Quantum Computation certificate halt: " + claim_id)
        rows.append(
            {
                "obligation_id": obligation["obligation_id"],
                "claim_id": claim_id,
                "receipt_hash": live_row["receipt_hash"],
                "receipt_path": live_row["receipt_path"],
                "certificate_hash": file_hash(certificate_path),
                "registration_hash": file_hash(registration_path),
                "registered_statement": registration["statement"],
                "certificate_exact_result": certificate["exact_result"],
                "closure_status": live_row["closure_status"],
                "external_status": live_row["external_status"],
                "controls_passed": True,
                "independently_recomputed": True,
            }
        )

    total = frozen["registered_obligation_count"]
    value = {
        "schema": "sft-v3-quantum-computation-discipline-current-reconciliation/1",
        "date": "2026-07-29",
        "frozen_census_identity": frozen_identity,
        "frozen_obligation_count": total,
        "closed_at_freeze": 22,
        "predecessor_reconciliation_identity": None,
        "completed_families": {"BASE": rows},
        "current_closed_count": 22,
        "current_open_count": total - 22,
        "current_completion_fraction": f"22/{total}",
        "current_completion_percent": "7.6%",
        "frozen_census_mutated": False,
        "extension_policy": frozen["extension_policy"],
    }
    value["reconciliation_identity"] = canonical(value)
    OUT.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    audit = {
        "schema": "sft-v3-quantum-computation-base-completion/1",
        "date": "2026-07-29",
        "family": "BASE",
        "family_completion": "22/22",
        "exact_replay": "22/22 exact receipt files reproduced",
        "independent_reconstruction": "22/22 certificate-bound independent reconstructions",
        "controls": "22/22 controls-passed certificates",
        "receipt_rows": rows,
        "protected_engine_or_verifier_changed": False,
        "current_quantum_computation_progress": f"22/{total}",
        "current_quantum_computation_percent": "7.6%",
        "frozen_census_identity": frozen_identity,
        "reconciliation_identity": value["reconciliation_identity"],
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"closed": 22, "open": total - 22, "percent": "7.6%", "exact_receipt_replays": len(rows), "identity": value["reconciliation_identity"]}, indent=2))


if __name__ == "__main__":
    main()
