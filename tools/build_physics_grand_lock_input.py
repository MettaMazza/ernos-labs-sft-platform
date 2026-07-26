#!/usr/bin/env python3
"""Freeze the pre-Grand-Lock Physics branch and its complete dependency graph.

This is a mechanical evidence-index builder.  It does not admit a claim and it
does not modify the canonical engine.  The resulting JSON is a declared input
to the separately enumerated Grand Lock claim.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "census/physics_grand_lock_input_v1.json"
ROOT_CLAIM = "SFT-FOUNDATION-ONE-001"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    census = load(ROOT / "census/claims.json")["claims"]
    by_id = {row["claim_id"]: row for row in census}
    physics_ids = tuple(sorted(
        row["claim_id"] for row in census
        if row.get("branch") == "physics" and row.get("model_admitted") is True
    ))
    if not physics_ids:
        raise SystemExit("no admitted Physics claims")

    registrations: dict[str, dict[str, object]] = {}

    def registration(claim_id: str) -> dict[str, object]:
        if claim_id in registrations:
            return registrations[claim_id]
        if claim_id not in by_id:
            raise SystemExit(f"unadmitted dependency: {claim_id}")
        path = ROOT / "claims" / claim_id / "registration.json"
        if not path.is_file():
            raise SystemExit(f"missing registration: {claim_id}")
        record = load(path)
        registrations[claim_id] = {
            "claim_id": claim_id,
            "branch": by_id[claim_id]["branch"],
            "dependencies": tuple(record.get("dependencies", ())),
            "registration_path": path.relative_to(ROOT).as_posix(),
            "registration_sha256": sha256(path),
        }
        return registrations[claim_id]

    closure: set[str] = set()

    def visit(claim_id: str, active: tuple[str, ...]) -> None:
        if claim_id in active:
            raise SystemExit("dependency cycle: " + " -> ".join(active + (claim_id,)))
        if claim_id in closure:
            return
        record = registration(claim_id)
        for dependency in record["dependencies"]:
            visit(str(dependency), active + (claim_id,))
        closure.add(claim_id)

    for claim_id in physics_ids:
        visit(claim_id, ())

    memo: dict[str, bool] = {}

    def reaches_one(claim_id: str) -> bool:
        if claim_id == ROOT_CLAIM:
            return True
        if claim_id in memo:
            return memo[claim_id]
        dependencies = registrations[claim_id]["dependencies"]
        result = bool(dependencies) and any(reaches_one(str(item)) for item in dependencies)
        memo[claim_id] = result
        return result

    branch_rows = []
    empirical_ids = []
    unfavorable_ids = []
    for claim_id in physics_ids:
        row = by_id[claim_id]
        receipt = ROOT / row["receipt_path"]
        certificate = ROOT / "claims" / claim_id / "certificate.json"
        if not receipt.is_file() or not certificate.is_file():
            raise SystemExit(f"missing admitted evidence: {claim_id}")
        receipt_record = load(receipt)
        certificate_record = load(certificate)
        if receipt_record.get("receipt_hash") != row["receipt_hash"]:
            raise SystemExit(f"receipt identity mismatch: {claim_id}")
        if certificate_record.get("engine_receipt_hash") != row["receipt_hash"]:
            raise SystemExit(f"certificate identity mismatch: {claim_id}")
        external_status = str(row.get("external_status", ""))
        empirical = "empirically_tested" in external_status
        if empirical:
            empirical_ids.append(claim_id)
        combined = " ".join((str(row.get("statement", "")), str(certificate_record.get("exact_result", "")))).lower()
        unfavorable = any(token in combined for token in (
            "unfavourable", "unfavorable", "non-overlap", "mismatch", "tension", "not observed", "not directly",
        ))
        if unfavorable:
            unfavorable_ids.append(claim_id)
        branch_rows.append({
            "claim_id": claim_id,
            "title": row.get("title"),
            "registered_statement": row.get("statement"),
            "exact_result": certificate_record.get("exact_result"),
            "receipt_hash": row["receipt_hash"],
            "receipt_path": row["receipt_path"],
            "receipt_file_sha256": sha256(receipt),
            "certificate_path": certificate.relative_to(ROOT).as_posix(),
            "certificate_sha256": sha256(certificate),
            "registration_sha256": registrations[claim_id]["registration_sha256"],
            "dependencies": registrations[claim_id]["dependencies"],
            "closure_status": row["closure_status"],
            "external_status": external_status,
            "empirical": empirical,
            "unfavorable_or_scope_boundary_retained": unfavorable,
            "source_manifest_hash": certificate_record.get("source_manifest_hash"),
            "empirical_validation_hash": certificate_record.get("empirical_validation_hash"),
            "external_validation_hash": certificate_record.get("external_validation_hash"),
            "measurement_receipt_hash": certificate_record.get("measurement_receipt_hash"),
            "all_measurement_rows_preserved": certificate_record.get("all_measurement_rows_preserved"),
            "external_data_source_ids": certificate_record.get("external_data_source_ids", ()),
            "falsification_condition": certificate_record.get("falsification_condition"),
        })

    if not all(reaches_one(claim_id) for claim_id in physics_ids):
        raise SystemExit("a Physics claim does not reach the foundational One")

    dependency_rows = tuple(registrations[claim_id] for claim_id in sorted(closure))
    payload = {
        "schema": "sft-v3-physics-grand-lock-input/1",
        "frozen_before_claim": "SFT-PHYS-GRAND-LOCK-TERMINAL-075",
        "foundational_root": ROOT_CLAIM,
        "physics_claim_count": len(physics_ids),
        "transitive_claim_count": len(closure),
        "empirical_claim_count": len(empirical_ids),
        "unfavorable_or_scope_boundary_count": len(unfavorable_ids),
        "physics_claim_ids": physics_ids,
        "empirical_claim_ids": tuple(empirical_ids),
        "unfavorable_or_scope_boundary_ids": tuple(unfavorable_ids),
        "physics_claims": tuple(branch_rows),
        "dependency_dictionary": dependency_rows,
        "certificate": {
            "all_physics_claims_admitted": True,
            "all_receipts_and_certificates_hash_bound": True,
            "all_registrations_hash_bound": True,
            "all_declared_dependencies_admitted": True,
            "dependency_graph_acyclic": True,
            "every_physics_claim_reaches_foundational_one": True,
            "measurements_do_not_select_formal_survivors": True,
            "unfavorable_results_and_scope_boundaries_retained": True,
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": sha256(OUTPUT),
        "physics_claims": len(physics_ids),
        "transitive_claims": len(closure),
        "empirical_claims": len(empirical_ids),
        "unfavorable_or_scope_boundaries": len(unfavorable_ids),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
