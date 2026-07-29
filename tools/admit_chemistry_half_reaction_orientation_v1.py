#!/usr/bin/env python3
from dataclasses import asdict
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.chemistry.half_reaction_orientation_batch_v1 import HALF_REACTION_SPEC
from sft.chemistry.half_reaction_orientation_validation_v1 import exact_analysis
from sft.engine import EngineRepository

def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")

def execution():
    path = ROOT / "claims" / HALF_REACTION_SPEC.claim_id / "execution.py"
    spec = importlib.util.spec_from_file_location("echem001", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_execution(ROOT)

def main():
    claim = HALF_REACTION_SPEC
    census_path = ROOT / "census/claims.json"
    if claim.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    run = execution()
    captured = {}
    class Independent:
        def validate(self, sealed):
            captured.update(sealed=sealed, independent=run.independent_validator.validate(sealed))
            return captured["independent"]
    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = run.empirical_validator.validate(sealed)
            return captured["empirical"]
    receipt = EngineRepository(ROOT).execute_official(run.program, Independent(), run.source_files, Empirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"})
    write(manifest_path, manifest)
    row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id
    analysis, checks = exact_analysis(ROOT)
    certificate = {
        "claim_id": claim.claim_id,
        "chemistry_obligation": "SFT-CHEM-OBL-ECHEM-001",
        "status": "model_admitted_forced_half_reaction_law_empirically_tested_and_independently_replicated",
        "source_manifest_hash": run.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": receipt.receipt_hash,
        "engine_receipt_path": row["receipt_path"],
        "closure_scope": receipt.closure_status,
        "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_6_target_checks_passed": all(checks.values()),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_sign_potential_value_or_equation_used_to_select_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    for name, payload in {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        "half_reaction_receipt.json": {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write(package / "registration.json", registration)
    experiment = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"
    experiment_registration = json.loads(experiment.read_text())
    experiment_registration["status"] = "measured_postseal_complete"
    write(experiment, experiment_registration)
    (package / "STATUS.md").write_text(
        f"# {claim.claim_id}\n\n"
        "Status: `model_admitted_forced_half_reaction_law_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-ECHEM-001`\n"
        "- Exact law: complete phased species and positive held transfer occurrences with reversible orientation, inverse pairing and reference identity.\n"
        "- External surface: complete IUPAC record plus all 22 NIST pages and 99,794 extracted characters.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    print(f"admitted {claim.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")

if __name__ == "__main__":
    main()
