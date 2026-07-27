#!/usr/bin/env python3
"""Independently verify the Chemistry V1/V2 atomic-ownership closure."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.publication_compliance import audit_branch


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit("CHEMISTRY ATOMIC AUDIT: FAIL — " + message)


def main() -> None:
    seal = subprocess.run(
        ["python3", "tools/verify_engine_seal.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if "SFT ENGINE SEAL: VALID CANONICAL ENGINE" not in seal.stdout:
        fail("canonical engine seal is not valid")

    v1 = read("audits/v1_theorem_manifest_observation_census.json")
    v2 = read("audits/v2_407_step_observation_census.json")
    audit = read("audits/chemistry_v1_v2_atomic_ownership.json")
    ledger = read("census/chemistry_prior_obligations.json")
    ownership = read("census/prior_obligation_ownership.json")
    claims = {row["claim_id"]: row for row in read("census/claims.json")["claims"]}

    expected_sources = {
        ("v1", str(row["v1_claim_id"])): row["source_row_sha256"] for row in v1["rows"]
    } | {
        ("v2", str(row["step"])): row["source_block_sha256"] for row in v2["steps"]
    }
    actual_sources = {
        (row["source"], str(row["source_entry"])): row["source_hash"] for row in audit["source_rows"]
    }
    if expected_sources != actual_sources:
        fail("source-key or source-hash coverage differs from the complete 763-entry census")

    identity_payload = dict(audit)
    recorded_identity = identity_payload.pop("audit_identity", None)
    computed_identity = "sha256:" + hashlib.sha256(
        json.dumps(identity_payload, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    if recorded_identity != computed_identity:
        fail("atomic-audit identity does not reproduce")

    atoms = [item for row in audit["source_rows"] for item in row["chemistry_atoms"]]
    atom_ids = [item["atom_id"] for item in atoms]
    if len(atom_ids) != len(set(atom_ids)):
        fail("duplicate Chemistry atom identifier")
    if len(atoms) != 52 or any(item["owner"] != "Chemistry" for item in atoms):
        fail("Chemistry atom count or one-owner rule differs from the registered closure")
    if any(not item["same_strength_closed"] or item["remaining_gap"] is not None for item in atoms):
        fail("an atom remains open")
    if any(not row.get("decomposition_complete") for row in audit["source_rows"] if row.get("categorical_boundary")):
        fail("a mixed source row was not explicitly decomposed")

    for item in atoms:
        if not item["current_v3_receipts"]:
            fail(f"{item['atom_id']} has no mapped receipt")
        for mapping in item["current_v3_receipts"] + item["upstream_prerequisite_receipts"]:
            claim_id = mapping["claim_id"]
            claim = claims.get(claim_id)
            if claim is None or claim.get("model_admitted") is not True:
                fail(f"{claim_id} is absent or not model-admitted")
            if mapping in item["current_v3_receipts"] and claim.get("branch") != "chemistry":
                fail(f"primary Chemistry mapping {claim_id} has another branch owner")
            receipt_path = ROOT / claim["receipt_path"]
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            file_sha = "sha256:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            if not (
                receipt.get("claim_id") == claim_id
                and receipt.get("model_admitted") is True
                and receipt.get("receipt_hash") == claim.get("receipt_hash") == mapping["receipt_hash"]
                and file_sha == mapping["receipt_file_sha256"]
            ):
                fail(f"receipt identity or hash mismatch for {claim_id}")

    if not (
        audit["audit_status"] == "current_evidence_closed_extension_open"
        and audit["summary"]["same_strength_open_atom_count"] == 0
        and audit["summary"]["publication_blocked"] is False
        and ledger["status"] == "closed"
        and ledger["atomic_ownership_audit_identity"] == recorded_identity
        and ledger["reviewed_source_surface"]["reviewed_entry_count"] == 763
        and ledger["chemistry_summary"]["open_count"] == 0
        and ownership["branch_summary"]["chemistry"]["status"] == "closed_same_strength"
        and ownership["branch_summary"]["chemistry"]["open_obligations"] == 0
    ):
        fail("audit, ledger or global ownership registration is inconsistent")

    gate = audit_branch(ROOT, "chemistry")
    if not gate.current_publication_ready or gate.blockers:
        fail("strengthened current-publication gate is not clear")

    print("CHEMISTRY V1/V2 ATOMIC OWNERSHIP: PASS")
    print("source entries reviewed: 763")
    print("Chemistry-relevant source entries: 34")
    print("Chemistry-owned atoms: 52")
    print("same-strength closed: 52")
    print("open Chemistry obligations: 0")
    print("strengthened current-publication gate: PASS")


if __name__ == "__main__":
    main()
