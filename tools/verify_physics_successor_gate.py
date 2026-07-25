#!/usr/bin/env python3
"""Fail closed on the corrected categorical Physics publication boundary.

This is a publication-only verifier.  It neither imports nor edits the
admission engine, executes a derivation, or mutates an immutable receipt.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE_EXPECTED = "ad30f4866c18b2adbade95a0b2de40d5caa61308"
ALPHA = "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001"
ALPHA_CHECK = "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001"
TERMINAL = "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_tree(path: str) -> str:
    import subprocess
    result = subprocess.run(
        ["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, check=True,
        capture_output=True, text=True,
    )
    return result.stdout.strip()


def blockers() -> list[str]:
    failures: list[str] = []
    if git_tree("sft/engine") != ENGINE_EXPECTED:
        failures.append("admission engine tree differs from the trusted frozen identity")
    inventory = read(ROOT / "publications/inventories/physics.json")
    ownership = read(ROOT / "census/prior_obligation_ownership.json")
    physics_ownership = ownership.get("branch_summary", {}).get("physics", {})
    if ownership.get("assignment_complete") is not True or physics_ownership.get("complete_v1_v2_reconstruction_proven") is not True:
        failures.append("complete one-owner V1/V2 Physics reconstruction is not yet proven")
    census_rows = read(ROOT / "census/claims.json")["claims"]
    live = [row for row in census_rows if row.get("branch") == "physics" and row.get("model_admitted") is True]
    ids = inventory.get("required_claim_ids", [])
    if ids != [row["claim_id"] for row in live] or len(ids) != 285:
        failures.append("categorical inventory is not the complete ordered live Physics census")
    if inventory.get("admitted_claim_count") != len(ids) or inventory.get("unclassified_obligations"):
        failures.append("categorical inventory is not completely classified and admitted")
    paper = (ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md").read_text(encoding="utf-8")
    for required in (ALPHA, ALPHA_CHECK, TERMINAL):
        if required not in paper:
            failures.append(f"paper omits required headline/terminal claim: {required}")
    evidence = read(ROOT / "publications/current/physics/evidence_map.json")
    if [row["claim_id"] for row in evidence.get("claims", [])] != ids:
        failures.append("paper evidence map is not one-to-one with the Physics inventory")
    manifest = read(ROOT / "publications/current/physics/manifest.json")
    if not (manifest.get("ready_to_publish") and manifest.get("required_claim_count") == 285):
        failures.append("Physics paper-specific publication gate is not ready")
    forbidden = (
        ROOT / "census/physics_prior_obligations.json",
        ROOT / "tools/build_physics_prior_obligations.py",
        ROOT / "tools/build_physics_receipt_reconciliation.py",
        ROOT / "audits/physics_prior_receipt_reconciliation_candidates.json",
    )
    if any(path.exists() for path in forbidden):
        failures.append("invalid cross-branch Physics ledger artifacts remain")
    for row in live:
        receipt = ROOT / row["receipt_path"]
        if not receipt.is_file():
            failures.append(f"missing engine receipt: {row['claim_id']}")
            continue
        payload = read(receipt)
        if payload.get("model_admitted") is not True or payload.get("receipt_hash") != row["receipt_hash"]:
            failures.append(f"engine receipt mismatch: {row['claim_id']}")
    return failures


def main() -> None:
    failures = blockers()
    if failures:
        raise SystemExit("PHYSICS SUCCESSOR PUBLICATION GATE: FAIL\n" + "\n".join(f"- {item}" for item in failures))
    print("PHYSICS SUCCESSOR PUBLICATION GATE: PASS")
    print("trusted engine tree: " + ENGINE_EXPECTED)
    print("categorical Physics claims: 285")


if __name__ == "__main__":
    main()
