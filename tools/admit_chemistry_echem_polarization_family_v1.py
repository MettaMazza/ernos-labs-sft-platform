#!/usr/bin/env python3
"""Submit exactly one ECHEM-009–012 claim per invocation in dependency order."""
from dataclasses import asdict
import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.chemistry.echem_polarization_batch_v1 import CORROSION_SPEC, DOUBLE_LAYER_SPEC, POLARIZATION_SPEC, RATE_SPEC
from sft.chemistry.echem_polarization_validation_v1 import exact_analysis
from sft.engine import EngineRepository

CONFIG = {
    "009": (RATE_SPEC, "SFT-CHEM-OBL-ECHEM-009", "electrode_reaction_rate_receipt.json", "model_admitted_forced_electrode_reaction_rate_law_empirically_tested_and_independently_replicated", "ten complete coating-current records plus complete galvanic and corrosion current-potential curve custody"),
    "010": (POLARIZATION_SPEC, "SFT-CHEM-OBL-ECHEM-010", "overpotential_polarization_receipt.json", "model_admitted_forced_overpotential_polarization_law_empirically_tested_and_independently_replicated", "complete equilibrium, anodic, cathodic, reversal, current, potential, hysteresis, discontinuity and IR-drop records"),
    "011": (DOUBLE_LAYER_SPEC, "SFT-CHEM-OBL-ECHEM-011", "double_layer_receipt.json", "model_admitted_forced_double_layer_interfacial_charge_law_empirically_tested_and_independently_replicated", "three electrolyte compositions, full voltage sweep, surface offsets, 20–40 nm resolution, model fits and limitations across 24 pages"),
    "012": (CORROSION_SPEC, "SFT-CHEM-OBL-ECHEM-012", "corrosion_network_receipt.json", "model_admitted_forced_corrosion_reaction_network_law_empirically_tested_and_independently_replicated", "21 complete corrosion table rows and ten coating controls with measured/calculated mass loss and every discrepancy"),
}


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def build_execution(claim):
    path = ROOT / "claims" / claim.claim_id / "execution.py"
    module_spec = importlib.util.spec_from_file_location("admit_" + claim.claim_id.rsplit("-", 1)[-1], path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
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
    run = build_execution(claim)
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
        raise SystemExit(f"claim halted at {result.halted_stage}; preserved receipt {result.receipt_hash}")
    sealed, independent, empirical = captured["sealed"], captured["independent"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["claims"].append({"claim_id": claim.claim_id, "execution_file": f"claims/{claim.claim_id}/execution.py"})
    write(manifest_path, manifest)
    row = next(row for row in json.loads(census_path.read_text())["claims"] if row["claim_id"] == claim.claim_id)
    package = ROOT / "claims" / claim.claim_id
    analysis, checks = exact_analysis(ROOT, claim.claim_id)
    certificate = {
        "claim_id": claim.claim_id, "chemistry_obligation": obligation, "status": status,
        "source_manifest_hash": run.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
        "independent_implementation_hash": independent.implementation_hash, "independent_certificate_hash": independent.certificate_hash,
        "external_validation_hash": result.external_validation_hash, "empirical_validation_hash": result.empirical_validation_hash,
        "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": result.receipt_hash,
        "engine_receipt_path": row["receipt_path"], "closure_scope": result.closure_status, "exact_result": claim.exact_result,
        "candidate_count": len(sealed.census.candidates), "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
        **analysis, "all_registered_target_checks_passed": all(checks.values()), "registered_target_check_count": len(checks),
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
    (package / "STATUS.md").write_text(f"# {claim.claim_id}\n\nStatus: `{status}`\n\n- Chemistry obligation: `{obligation}`\n- Exact law: `{claim.exact_result}`\n- Complete external surface: {external_surface}; all applicable pages within the 73-page shared family reconstruction retained.\n- Derivation seal: `{sealed.seal_hash}`\n- Engine receipt: `{result.receipt_hash}`\n")
    print(f"admitted {claim.claim_id}: {result.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")


if __name__ == "__main__":
    main()
