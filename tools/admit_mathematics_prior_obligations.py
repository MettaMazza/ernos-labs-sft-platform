#!/usr/bin/env python3
"""Admit only the ten Mathematics same-strength lineage reconstructions."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from sft.engine import EngineRepository  # noqa: E402
from sft.mathematics.lineage_laws import LINEAGE_SPECS  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("sft_math_lineage_" + claim_id.replace("-", "_"), path)
    if spec is None or spec.loader is None: raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    repository = EngineRepository(ROOT)
    existing_rows = {
        row["claim_id"]: row
        for row in json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))["claims"]
    }
    for spec in LINEAGE_SPECS:
        if spec.claim_id in existing_rows and existing_rows[spec.claim_id].get("model_admitted"):
            print(f"retained admitted receipt {spec.claim_id}: {existing_rows[spec.claim_id]['receipt_hash']}")
            continue
        execution = load_execution(spec.claim_id)
        receipt = repository.execute_official(execution.program, execution.independent_validator, execution.source_files, execution.empirical_validator)
        print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")

    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")); existing = {item["claim_id"] for item in manifest["claims"]}
    for spec in LINEAGE_SPECS:
        if spec.claim_id not in existing:
            manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
    write_json(manifest_path, manifest)

    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8")); rows = {row["claim_id"]: row for row in census["claims"]}
    for spec in LINEAGE_SPECS:
        package = ROOT / "claims" / spec.claim_id
        certificate_path = package / "certificate.json"
        if certificate_path.is_file():
            materialized_message = f"retained materialized evidence {spec.claim_id}"
        else:
            completed = subprocess.run((sys.executable, str(ROOT / "tools/materialize_claim_evidence.py"), spec.claim_id, spec.exact_result), cwd=ROOT, text=True, capture_output=True, check=False)
            if completed.returncode: raise RuntimeError(completed.stdout + completed.stderr)
            materialized_message = completed.stdout.strip()
        registration_path = package / "registration.json"
        if registration_path.is_file():
            registration = json.loads(registration_path.read_text(encoding="utf-8"))
        else:
            candidate = json.loads((package / "candidate_census.json").read_text(encoding="utf-8"))
            registration = {
                "$schema": "../../governance/claim.schema.json",
                "branch": "mathematics",
                "candidate_grammar": {
                    "boundary": spec.grammar_boundary,
                    "completeness_certificate": candidate["completeness_certificate_hash"],
                    "generator": spec.generation_rule,
                },
                "claim_id": spec.claim_id,
                "dependencies": list(spec.dependencies),
                "empirical_protocol": None,
                "excluded_inputs": list(spec.boundary_exclusions),
                "intended_certificate": "Independent regeneration of the complete candidate product, sole all-preserving survivor, closure properties, operational witnesses and controls.",
                "provenance_classes": ["forward_forcing"],
                "registered_by": "Maria Smith",
                "registration_date": "2026-07-24",
                "required_controls": ["false_premise", "tampered_source", "tampered_artifact", "boundary"],
                "statement": spec.statement,
                "title": spec.title,
            }
        registration["status"] = "independently_replicated"; write_json(registration_path, registration)
        certificate = json.loads((package / "certificate.json").read_text(encoding="utf-8")); row = rows[spec.claim_id]
        (package / "STATUS.md").write_text(
            f"# {spec.claim_id}\n\nStatus: `independently_replicated`\n\n"
            f"- Closure: `{certificate['closure_scope']}`\n"
            "- Empirical status: formal theorem; authoritative mathematical correspondence is post-seal only\n"
            f"- Derivation seal: `{certificate['derivation_seal_hash']}`\n"
            f"- External validation: `{certificate['external_validation_hash']}`\n"
            f"- Engine receipt: `{row['receipt_hash']}`\n"
            f"- Receipt path: `{row['receipt_path']}`\n", encoding="utf-8")
        print(materialized_message)


if __name__ == "__main__": main()
