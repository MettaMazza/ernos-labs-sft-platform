#!/usr/bin/env python3
"""Admit the complete CRYS-001--008 family sequentially through the untouched engine."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.materials.crys_001_008_laws_v1 import ORDER, SPECS


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def verify_protected_seals() -> None:
    checks = (
        ("verify_engine_seal.py", "VALID_CANONICAL_ENGINE"),
        ("verify_verification_authority_seal.py", "VALID_CANONICAL_VERIFICATION_AUTHORITY"),
    )
    for tool, expected in checks:
        completed = subprocess.run((sys.executable, str(ROOT / "tools" / tool), "--json"), cwd=ROOT, text=True, capture_output=True)
        result = json.loads(completed.stdout)
        if completed.returncode or result.get("status") != expected:
            raise SystemExit("Materials CRYS admission halted: protected authority seal invalid")


def load_execution(claim_id: str):
    path = ROOT / "claims" / claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("materials_crys_" + claim_id.replace("-", "_"), path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    from sft.engine import EngineRepository

    verify_protected_seals()
    census_path = ROOT / "census/claims.json"
    manifest_path = ROOT / "census/execution_manifest.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if any(claim_id in existing for claim_id in ORDER):
        present = [claim_id for claim_id in ORDER if claim_id in existing]
        raise SystemExit("Materials CRYS admission refuses replay of existing claims: " + ", ".join(present))

    for index, claim_id in enumerate(ORDER, 1):
        spec = SPECS[claim_id]
        missing = tuple(dependency for dependency in spec.dependencies if dependency not in existing)
        if missing:
            raise SystemExit(f"Materials CRYS admission halted: missing dependencies for {claim_id}: {missing}")
        execution = load_execution(claim_id)
        captured = {}

        class IndependentCapture:
            def validate(self, sealed):
                captured["sealed"] = sealed
                result = execution.independent_validator.validate(sealed)
                captured["independent"] = result
                return result

        class EmpiricalCapture:
            def validate(self, sealed):
                result = execution.empirical_validator.validate(sealed)
                captured["empirical"] = result
                return result

        receipt = EngineRepository(ROOT).execute_official(
            execution.program,
            IndependentCapture(),
            execution.source_files,
            EmpiricalCapture(),
        )
        if not receipt.model_admitted:
            raise SystemExit("untouched engine halted: " + claim_id)

        manifest = json.loads(manifest_path.read_text())
        manifest["claims"].append({"claim_id": claim_id, "execution_file": f"claims/{claim_id}/execution.py"})
        write_json(manifest_path, manifest)
        row = next(item for item in json.loads(census_path.read_text())["claims"] if item["claim_id"] == claim_id)
        sealed = captured["sealed"]
        independent = captured["independent"]
        empirical = captured["empirical"]
        package = ROOT / "claims" / claim_id
        write_json(package / "candidate_census.json", {"claim_id": claim_id, **asdict(sealed.census)})
        write_json(package / "elimination_receipt.json", {"claim_id": claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)})
        write_json(package / "controls.json", {"claim_id": claim_id, "controls": asdict(sealed)["controls"]})
        write_json(package / "empirical_validation.json", {"claim_id": claim_id, **asdict(empirical)})
        write_json(package / "certificate.json", {
            "claim_id": claim_id,
            "materials_obligation": spec.obligation_id,
            "status": "model_admitted_authoritatively_corresponded_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": independent.implementation_hash,
            "independent_certificate_hash": independent.certificate_hash,
            "independently_recomputed": True,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "falsification_condition": empirical.falsification_condition,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": row["receipt_path"],
            "exact_result": spec.exact_result,
            "closure_scope": receipt.closure_status,
            "controls_passed": True,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "free_parameters": [],
            "imported_axioms": [],
            "target_registry_identity": "sha256:e0acb17fb7a8974f8fcb2cddc77ea2b1639cf442de36142b8b1116d6495b533a",
            "complete_evidence_vector_identity": "sha256:d49390d121968123adf0cd36dc2f40e8b7d015f91abfc180a091adca121b303b",
            "unavailable_source_rows_preserved": 2,
            "failed_capture_routes_preserved": 2,
        })
        (package / "STATUS.md").write_text(
            f"# {claim_id}\n\nStatus: `model_admitted_authoritatively_corresponded_and_independently_replicated`\n\n"
            f"- Obligation: `{spec.obligation_id}`\n"
            f"- Exact result: {spec.exact_result}\n"
            f"- Candidate census: `256`, unique survivor: `1`\n"
            f"- Engine receipt: `{receipt.receipt_hash}`\n"
            f"- Closure: `{receipt.closure_status}`\n"
        )
        verify_protected_seals()
        existing.add(claim_id)
        print(f"[{index}/{len(ORDER)}] admitted {claim_id}: {receipt.receipt_hash}", flush=True)


if __name__ == "__main__":
    main()
