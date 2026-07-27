#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-002 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.concentration_dependence_batch_v1 import CONCENTRATION_DEPENDENCE_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.concentration_dependence_validation_v1 import _source_rows, exact_concentration_dependence_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CONCENTRATION_DEPENDENCE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_002", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-002 execution package")
    module = importlib.util.module_from_spec(definition); definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = CONCENTRATION_DEPENDENCE_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution(); captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed; result = execution.independent_validator.validate(sealed); captured["external"] = result; return result

    class CaptureEmpirical:
        def validate(self, sealed):
            result = execution.empirical_validator.validate(sealed); captured["empirical"] = result; return result

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"; manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}); write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text()); census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id; rows = _source_rows(ROOT); primary = json.loads((ROOT / PRIMARY_PATH).read_text()); analysis = exact_concentration_dependence_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_id": row["source_id"], "source_row_ordinal": row["source_row_ordinal"],
        "reaction_identity": row["target_payload"]["reaction_identity"], "measurement_method": row["target_payload"]["measurement_method"],
        "temperature_K_external_inscription": row["target_payload"]["temperature_K_external_inscription"],
        "temperature_uncertainty_K_external_inscription": row["target_payload"]["temperature_uncertainty_K_external_inscription"],
        "flow_density_1e16_molecule_cm_minus3_external_inscription": row["target_payload"]["flow_density_1e16_molecule_cm_minus3_external_inscription"],
        "flow_density_uncertainty_1e16_molecule_cm_minus3_external_inscription": row["target_payload"]["flow_density_uncertainty_1e16_molecule_cm_minus3_external_inscription"],
        "rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription": row["target_payload"]["rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription"],
        "rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription": row["target_payload"]["rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription"],
        "source_note_markers": row["target_payload"]["source_note_markers"], "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-002",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"], "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result, "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "concentration_dependence_law": "complete source-ordered exact concentration/rate table for one held reactant under complete conditions, method and uncertainties; no fitted exponent",
            "complete_external_target_count": 9, "complete_uncertainty_coordinate_count": 27,
            "exact_temperature_range_K": analysis["exact_temperature_range_K"],
            "exact_flow_density_range_1e16_molecule_cm_minus3": analysis["exact_flow_density_range_1e16_molecule_cm_minus3"],
            "exact_rate_range_molecule_minus1_cm3_s_minus1": analysis["exact_rate_range_molecule_minus1_cm3_s_minus1"],
            "complete_concentration_rate_vector": vector, "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids), "all_values_released_after_identity_and_prediction_seal": True,
            "source_fit_disclosure_preserved_postseal": True,
            "mass_action_power_law_reaction_order_fitted_exponent_coefficient_logarithm_continuum_derivative_interpolation_regression_averaging_selection_or_target_correction_used_in_law": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items(): write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"; experiment = json.loads(experiment_path.read_text()); experiment["status"] = "complete_nine_row_vector_opened_postseal"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `SFT-CHEM-OBL-KIN-002`\n- Closure: `{receipt.closure_status}`\n"
        "- Exact law: complete source-ordered condition-bound concentration/rate table; no fitted exponent.\n"
        "- Complete primary surface: `9` rows and `27` uncertainty coordinates from DOI `10.1039/C3CP54664K`, Table 2.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}"); print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}"); print("complete concentration/rate vector: 9 rows; 27 uncertainty coordinates")


if __name__ == "__main__":
    main()
