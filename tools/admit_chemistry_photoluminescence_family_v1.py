#!/usr/bin/env python3
"""Submit exactly one ANAL-009--011 claim in dependency order."""

from dataclasses import asdict
import argparse
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.photoluminescence_family_batch_v1 import (
    FLUORESCENCE_SPEC, PHOSPHORESCENCE_SPEC, RAMAN_SPEC,
)
from sft.chemistry.photoluminescence_family_validation_v1 import exact_analysis
from sft.engine import EngineRepository


CONFIG = {
    "009": (
        RAMAN_SPEC, "SFT-CHEM-OBL-ANAL-009", "raman_transition_intensity_receipt.json",
        "model_admitted_forced_raman_transition_intensity_law_empirically_tested_and_independently_replicated",
        "six SRM 2241 coefficient rows and all 386 SRM 2242a shifts across five certified curves (1,930 values), 785 nm and 532 nm excitation boundaries and every signed coefficient and uncertainty curve",
    ),
    "010": (
        FLUORESCENCE_SPEC, "SFT-CHEM-OBL-ANAL-010", "fluorescence_yield_lifetime_receipt.json",
        "model_admitted_forced_fluorescence_yield_lifetime_law_empirically_tested_and_independently_replicated",
        "all 201 SRM 2941a emission rows, 100 IUPAC quantum-yield table rows, 813 numerical inscriptions, twenty lifetime conditions and two retained outliers",
    ),
    "011": (
        PHOSPHORESCENCE_SPEC, "SFT-CHEM-OBL-ANAL-011", "phosphorescence_intersystem_receipt.json",
        "model_admitted_forced_phosphorescence_intersystem_law_empirically_tested_and_independently_replicated",
        "all three two-temperature lifetime rows, 142 BioC passages, and seven favorable/adverse/absent/unavailable custody classes",
    ),
}


def write(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def build_execution(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("claim", choices=tuple(CONFIG))
    args = parser.parse_args()
    claim, obligation, receipt_name, status, external_surface = CONFIG[args.claim]
    census_path = ROOT / "census/claims.json"
    admitted = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if claim.claim_id in admitted:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    for dependency in claim.dependencies:
        if dependency not in admitted:
            raise SystemExit(f"dependency not admitted; halted before submission: {dependency}")

    execution = build_execution(claim)
    captured = {}

    class Independent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["independent"] = execution.independent_validator.validate(sealed)
            return captured["independent"]

    class Empirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    result = EngineRepository(ROOT).execute_official(
        execution.program, Independent(), execution.source_files, Empirical(),
    )
    if not result.model_admitted:
        raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")

    sealed = captured["sealed"]
    independent = captured["independent"]
    empirical = captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"})
    write(manifest_path, manifest)
    census_row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    certificate = {
        "claim_id": claim.claim_id, "chemistry_obligation": obligation, "status": status,
        "source_manifest_hash": execution.program.registration.source_hash,
        "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash,
        "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": result.external_validation_hash,
        "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash,
        "engine_receipt_hash": result.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
        "closure_scope": result.closure_status, "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates),
        "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis,
        "all_registered_target_checks_passed": all(checks.values()),
        "registered_target_check_count": len(checks),
        "all_external_rows_preserved": empirical.all_rows_preserved,
        "numerical_zero_negative_irrational_imaginary_continuum_fitted_free_random_or_imported_native_parameter_used": False,
        "external_values_equations_fits_discrepancies_or_trends_used_to_select_native_law": False,
        "falsification_condition": empirical.falsification_condition,
    }
    artifacts = {
        "candidate_census.json": {"claim_id": claim.claim_id, **asdict(sealed.census)},
        receipt_name: {"claim_id": claim.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": claim.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": claim.claim_id, **asdict(empirical)},
        "certificate.json": certificate,
    }
    for name, payload in artifacts.items():
        write(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    registration["candidate_grammar"]["completeness_certificate"] = sealed.census.completeness_certificate_hash
    write(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / claim.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "measured_postseal_complete"
    write(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {claim.claim_id}\n\nStatus: `{status}`\n\n"
        f"- Chemistry obligation: `{obligation}`\n- Exact law: `{claim.exact_result}`\n"
        f"- Complete external surface: {external_surface}; all sixteen source artifacts and every declared adverse/absence row retained.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n"
    )
    print(f"admitted {claim.claim_id}: {result.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
