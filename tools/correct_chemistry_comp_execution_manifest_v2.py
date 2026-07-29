#!/usr/bin/env python3
"""Align COMP manifest paths with the actually admitted v2 execution sources."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.computational_chemistry_batch_v1 import SPECS_BY_NUMBER


MANIFEST = ROOT / "census/execution_manifest.json"
AUDIT = ROOT / "audits/CHEMISTRY_COMP_001_014_EXECUTION_MANIFEST_V2_CORRECTION_2026-07-28.json"


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> None:
    if AUDIT.exists():
        raise SystemExit("manifest correction audit already exists")
    before_bytes = MANIFEST.read_bytes(); manifest = json.loads(before_bytes); by_id = {row["claim_id"]: row for row in manifest["claims"]}
    records = []
    for number, claim in SPECS_BY_NUMBER.items():
        execution_path = ROOT / "claims" / claim.claim_id / "execution_v2.py"
        module_spec = importlib.util.spec_from_file_location("manifest_v2_" + number, execution_path)
        module = importlib.util.module_from_spec(module_spec); module_spec.loader.exec_module(module)
        execution = module.build_execution(ROOT)
        certificate_path = ROOT / "claims" / claim.claim_id / "certificate.json"
        certificate = json.loads(certificate_path.read_text())
        if execution.program.registration.source_hash != certificate["source_manifest_hash"]:
            raise SystemExit(f"v2 source manifest does not match admitted certificate: {claim.claim_id}")
        row = by_id[claim.claim_id]
        old_path = row["execution_file"]
        new_path = f"claims/{claim.claim_id}/execution_v2.py"
        if old_path != f"claims/{claim.claim_id}/execution.py":
            raise SystemExit(f"unexpected pre-correction manifest path: {claim.claim_id}")
        row["execution_file"] = new_path
        records.append({
            "number": number, "claim_id": claim.claim_id, "old_execution_path": old_path,
            "new_execution_path": new_path, "admitted_source_manifest_hash": certificate["source_manifest_hash"],
            "v2_reconstructed_source_manifest_hash": execution.program.registration.source_hash,
            "engine_receipt_hash": certificate["engine_receipt_hash"],
        })
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    audit = {
        "schema": "sft-v3-factual-execution-manifest-path-correction/1", "date": "2026-07-28",
        "reason": "The versioned admission wrapper correctly executed execution_v2.py but its preserved v1 bookkeeping function appended execution.py. Every corrected path is independently proved by exact equality between the v2 reconstructed source manifest and the source manifest stored in the admitted claim certificate.",
        "manifest_before_hash": digest(before_bytes), "manifest_after_hash": digest(MANIFEST.read_bytes()),
        "correction_count": len(records), "records": records,
        "census_receipt_engine_verification_authority_law_target_comparison_or_result_changed": False,
        "rejected_v1_receipt_and_sources_preserved": True,
    }
    AUDIT.write_text(json.dumps(audit, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"corrected {len(records)} factual execution paths; manifest {audit['manifest_after_hash']}")


if __name__ == "__main__":
    main()
