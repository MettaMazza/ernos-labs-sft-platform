#!/usr/bin/env python3
"""Exact read-only replay of the twelve admitted Materials ELEC receipts."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine import AuthorityLedger, SFTAdmissionEngine
from sft.engine.receipt_io import read_receipt
from sft.engine.source import build_source_manifest
from sft.materials.elec_001_012_laws_v1 import ORDER
from sft.verification import _load_execution, _sealed_replay_environment

def main():
    census = json.loads((ROOT / "census/claims.json").read_text())["claims"]
    manifest = json.loads((ROOT / "census/execution_manifest.json").read_text())["claims"]
    if [row["claim_id"] for row in census] != [row["claim_id"] for row in manifest]:
        raise SystemExit("ELEC replay halted: census and execution manifest differ")
    indices = {row["claim_id"]: index for index, row in enumerate(census)}
    first = min(indices[claim_id] for claim_id in ORDER)
    authority = AuthorityLedger()
    for row in census[:first]:
        authority.admit(read_receipt(ROOT / row["receipt_path"]))
    engine = SFTAdmissionEngine(authority)
    results = []
    for claim_id in ORDER:
        index = indices[claim_id]
        row = census[index]
        execution = _load_execution(ROOT, manifest[index])
        with _sealed_replay_environment(ROOT, claim_id, execution.empirical_validator):
            receipt = engine.run(execution.program, execution.independent_validator, execution.empirical_validator, executed_source_hash=build_source_manifest(ROOT, execution.source_files).manifest_hash)
        stored = read_receipt(ROOT / row["receipt_path"])
        if receipt != stored or receipt.receipt_hash != row["receipt_hash"]:
            raise SystemExit("ELEC exact replay mismatch: " + claim_id)
        authority.admit(receipt)
        results.append({"claim_id": claim_id, "receipt_hash": receipt.receipt_hash, "exact_replay": True})
        print(f"[{len(results)}/{len(ORDER)}] exact replay {claim_id}: {receipt.receipt_hash}", flush=True)
    print(json.dumps({"replayed": len(results), "all_exact": True, "receipts": results}, indent=2))

if __name__ == "__main__":
    main()
