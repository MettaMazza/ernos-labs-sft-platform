#!/usr/bin/env python3
"""Record the completed local Medicine foundation checkpoint without publishing."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CLAIMS = 72
LAST_CLAIM = "SFT-MED-CLINICAL-EVIDENCE-HANDOFF-001"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    inventory = read_json(ROOT / "publications/inventories/medicine.json")
    census = read_json(ROOT / "census/claims.json")
    audit = read_json(ROOT / "audits/medicine_v1_v2_atomic_ownership.json")
    sources = read_json(ROOT / "experiments/external_sources/medicine/source_manifest.json")
    metadata = read_json(ROOT / "publication/medicine_foundation_zenodo_metadata.json")
    required = tuple(inventory["required_claim_ids"])
    admitted = {
        row["claim_id"]: row
        for row in census["claims"]
        if row.get("model_admitted") is True and row.get("branch") == "medicine"
    }
    if len(required) != EXPECTED_CLAIMS or tuple(admitted) != required:
        raise RuntimeError("Medicine admissions do not exactly match the frozen ordered inventory")
    if audit["summary"]["same_strength_open_atom_count"] != 0:
        raise RuntimeError("Medicine V1/V2 atomic reconciliation remains open")
    if sources["captured_count"] != 11 or sources["failed_count"] != 2:
        raise RuntimeError("Medicine source transport ledger changed")
    if metadata["publication_authorized"] is not False:
        raise RuntimeError("remote publication authorization must remain false")
    for path in (
        ROOT / "publications/current/medicine/FROM_FOLD_TO_MEDICINE.md",
        ROOT / "output/pdf/from-fold-to-medicine-health-sciences-foundation-paper-001-v1.0.pdf",
    ):
        if not path.is_file() or path.stat().st_size < 1:
            raise RuntimeError(f"missing local paper artifact: {path.relative_to(ROOT)}")

    last = admitted[LAST_CLAIM]
    checkpoint = {
        "schema": "sft-v3-medicine-continuation-checkpoint/1",
        "branch": "medicine",
        "foundation_required_claim_count": EXPECTED_CLAIMS,
        "admitted_claim_count": EXPECTED_CLAIMS,
        "remaining_claim_count": 0,
        "last_admitted_claim_id": LAST_CLAIM,
        "last_admitted_receipt_hash": last["receipt_hash"],
        "closure_status": "depth_independent",
        "status": "foundational_branch_current_evidence_closed_extension_open",
        "next_exact_operation": "proofread_and_stage_medicine_foundation_without_remote_publication",
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "remote_publication_authorized": False,
    }
    write_json(ROOT / "census/medicine_continuation_checkpoint.json", checkpoint)

    branches_path = ROOT / "census/branches.json"
    branches = read_json(branches_path)
    row = next(item for item in branches["branches"] if item["branch_id"] == "medicine")
    wanted_inventory = "current_evidence_closed_72_of_72_claims_5_of_5_prior_obligations_extension_open"
    wanted_paper = "local_prepublication_paper_001_v1.0_ready_not_authorized"
    if row["inventory_status"] != wanted_inventory or row["paper_status"] != wanted_paper:
        original = branches_path.read_text(encoding="utf-8")
        old_line = next(line for line in original.splitlines() if '"branch_id": "medicine"' in line)
        indent = old_line[: len(old_line) - len(old_line.lstrip())]
        replacement = (
            f'{indent}{{"branch_id": "medicine", "inventory_status": "{wanted_inventory}", '
            f'"paper_status": "{wanted_paper}"}},'
        )
        branches_path.write_text(original.replace(old_line, replacement), encoding="utf-8")
    print("Medicine foundation checkpoint: CLOSED CURRENT EVIDENCE / EXTENSION OPEN; remote publication=false")


if __name__ == "__main__":
    main()
