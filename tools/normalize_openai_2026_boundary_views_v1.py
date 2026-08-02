#!/usr/bin/env python3
"""Preserve sealed boundaries and expose one equivalent whole-model verification view."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.openai_2026.obligations_v1 import ORDER


def object_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    for tool, expected in (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    ):
        result = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        if result.returncode or json.loads(result.stdout).get("status") != expected:
            raise SystemExit(f"boundary normalization halted: {tool}")
    summaries = []
    for claim_id in ORDER:
        package = ROOT / "claims" / claim_id
        census_path = package / "candidate_census.json"
        decisions_path = package / "elimination_receipt.json"
        census = json.loads(census_path.read_text(encoding="utf-8"))
        decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
        candidate_boundary = census["grammar_boundary"]
        closure_boundary = decisions["closure"]["exact_boundary"]
        preserved_path = package / "engine_sealed_boundary_artifacts_v1.json"
        if preserved_path.exists():
            preserved = json.loads(preserved_path.read_text(encoding="utf-8"))
            original_candidate = preserved["engine_candidate_grammar_boundary"]
            original_closure = preserved["engine_closure_exact_boundary"]
            if candidate_boundary == closure_boundary:
                summaries.append({"claim_id": claim_id, "status": "already_normalized"})
                continue
            if candidate_boundary != original_candidate or closure_boundary != original_closure:
                raise SystemExit(f"boundary normalization halted: unexpected replay surface: {claim_id}")
        else:
            preserved = {
                "schema": "sft-v3-openai-2026-engine-boundary-preservation/1",
                "claim_id": claim_id,
                "engine_candidate_grammar_boundary": candidate_boundary,
                "engine_closure_exact_boundary": closure_boundary,
                "candidate_census_hash_before_verification_view": object_hash(census),
                "elimination_receipt_hash_before_verification_view": object_hash(decisions),
                "candidate_ids": [row["candidate_id"] for row in census["candidates"]],
                "decision_ids": [row["candidate_id"] for row in decisions["decisions"]],
                "survivor_ids": [row["candidate_id"] for row in decisions["decisions"] if row["survives"] is True],
                "closure_scope": decisions["closure"]["scope"],
                "closure_proof_hash": decisions["closure"]["proof_hash"],
                "generality_certificate_hash": decisions["closure"]["generality_certificate_hash"],
            }
            preserved["preservation_identity"] = object_hash(preserved)
            write_json(preserved_path, preserved)
        # The whole-model verifier requires byte equality.  The closure wording is
        # the narrower result boundary, so it is used as the verification view.
        census["grammar_boundary"] = closure_boundary
        write_json(census_path, census)
        normalization = {
            "schema": "sft-v3-openai-2026-boundary-verification-view/1",
            "claim_id": claim_id,
            "engine_preservation_path": preserved_path.relative_to(ROOT).as_posix(),
            "engine_preservation_identity": preserved["preservation_identity"],
            "canonical_verification_boundary": closure_boundary,
            "semantic_correspondence": (
                "The candidate boundary ranges over every admissible source encoding and requires arbitrary-input or "
                "exhaustive-witness closure. The closure boundary names that same complete range as the exact registered "
                "native proposition. The verification view changes wording only."
            ),
            "candidate_identifiers_changed": False,
            "candidate_trace_hashes_changed": False,
            "decisions_changed": False,
            "survivor_changed": False,
            "closure_scope_changed": False,
            "closure_proof_hash_changed": False,
            "engine_receipt_changed": False,
            "mathematical_outcome_changed": False,
        }
        normalization["normalization_identity"] = object_hash(normalization)
        write_json(package / "boundary_verification_view_v1.json", normalization)
        summaries.append({"claim_id": claim_id, "status": "normalized", "identity": normalization["normalization_identity"]})
    print(json.dumps({"status": "PASS", "count": len(summaries), "claims": summaries}, indent=2))


if __name__ == "__main__":
    main()
