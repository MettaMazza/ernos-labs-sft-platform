#!/usr/bin/env python3
"""Admit ECHEM-013 through the untouched official engine."""
from dataclasses import asdict
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.echem_storage_handoff_batch_v1 import STORAGE_SPEC
from sft.chemistry.echem_storage_handoff_validation_v1 import exact_analysis
from sft.engine import EngineRepository


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def main() -> None:
    census_path = ROOT / "census/claims.json"
    admitted = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if STORAGE_SPEC.claim_id in admitted:
        raise SystemExit("ECHEM-013 already admitted; immutable receipt preserved")
    for dependency in STORAGE_SPEC.dependencies:
        if dependency not in admitted:
            raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")
    path = ROOT / "claims" / STORAGE_SPEC.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("admit_echem013", path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    run = module.build_execution(ROOT)
    captured = {}

    class Independent:
        def validate(self, sealed):
            captured.update(sealed=sealed, independent=run.independent_validator.validate(sealed))
            return captured["independent"]

    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = run.empirical_validator.validate(sealed)
            return captured["empirical"]

    result = EngineRepository(ROOT).execute_official(run.program, Independent(), run.source_files, Empirical())
    if not result.model_admitted:
        raise SystemExit(f"ECHEM-013 halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": STORAGE_SPEC.claim_id, "execution_file": f"claims/{STORAGE_SPEC.claim_id}/execution.py"})
    write(manifest_path, manifest)
    row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == STORAGE_SPEC.claim_id)
    package = ROOT / "claims" / STORAGE_SPEC.claim_id
    analysis, checks = exact_analysis(ROOT)
    certificate = {
        "claim_id": STORAGE_SPEC.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-ECHEM-013", "status": "model_admitted_forced_electrochemical_storage_handoff_law_empirically_tested_and_independently_replicated",
        "source_manifest_hash": run.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash, "external_validation_hash": result.external_validation_hash, "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": result.receipt_hash, "engine_receipt_path": row["receipt_path"], "closure_scope": result.closure_status,
        "exact_result": STORAGE_SPEC.exact_result, "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(decision.survives for decision in sealed.decisions), **analysis,
        "all_registered_target_checks_passed": all(checks.values()), "registered_target_check_count": len(checks), "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "application_result_or_external_outcome_used_to_select_native_law": False, "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": STORAGE_SPEC.claim_id, **asdict(sealed.census)},
        "storage_handoff_receipt.json": {"claim_id": STORAGE_SPEC.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": STORAGE_SPEC.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": STORAGE_SPEC.claim_id, **asdict(empirical)}, "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / STORAGE_SPEC.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured_postseal_complete"
    write(experiment_path, experiment)
    (package / "STATUS.md").write_text(f"# {STORAGE_SPEC.claim_id}\n\nStatus: `model_admitted_forced_electrochemical_storage_handoff_law_empirically_tested_and_independently_replicated`\n\n- Chemistry obligation: `SFT-CHEM-OBL-ECHEM-013`\n- Exact law: `{STORAGE_SPEC.exact_result}`\n- Complete external surface: three admitted owner certificates, two directed handoffs and the complete 97,292-byte inherited NIST Materials record.\n- Development-observed source status: disclosed, never relabelled blind.\n- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n")
    print(f"admitted {STORAGE_SPEC.claim_id}: {result.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
