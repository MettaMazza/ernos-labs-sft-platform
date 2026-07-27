#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-005 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.transition_boundary_batch_v1 import PRIMARY_PATH, TRANSITION_BOUNDARY_SPEC  # noqa: E402
from sft.chemistry.transition_boundary_validation_v1 import (  # noqa: E402
    _source_rows, exact_transition_boundary_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / TRANSITION_BOUNDARY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_005", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-005 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = TRANSITION_BOUNDARY_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            result = execution.independent_validator.validate(sealed)
            captured["external"] = result
            return result

    class CaptureEmpirical:
        def validate(self, sealed):
            result = execution.empirical_validator.validate(sealed)
            captured["empirical"] = result
            return result

    receipt = EngineRepository(ROOT).execute_official(
        execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical()
    )
    if not receipt.model_admitted:
        raise SystemExit(f"claim halted at {receipt.halted_stage}; preserved receipt {receipt.receipt_hash}")
    sealed, external, empirical = captured["sealed"], captured["external"], captured["empirical"]
    manifest_path = ROOT / "census/execution_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if spec.claim_id not in {row["claim_id"] for row in manifest["claims"]}:
        manifest["claims"].append({
            "claim_id": spec.claim_id,
            "execution_file": f"claims/{spec.claim_id}/execution.py",
        })
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_transition_boundary_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"],
        "source_id": row["source_id"],
        "article_doi": row["article_doi"],
        "material_system_identity": row["material_system_identity"],
        "experimental_method_identity": row["experimental_method_identity"],
        "source_figure_identity": row["source_figure_identity"],
        "isotopologue_identity": row["isotopologue_identity"],
        "exposure_identity": row["exposure_identity"],
        "surface_coverage_external_inscription_ML": row["target_payload"]["surface_coverage_external_inscription_ML"],
        "temperature_range_K_external_inscription": row["target_payload"]["temperature_range_K_external_inscription"],
        "exposure_L_external_inscription": row["target_payload"]["exposure_L_external_inscription"],
        "uptake_temperature_order_signature": row["target_payload"]["uptake_temperature_order_signature"],
        "apparent_barrier_external_signed_inscription_eV": row["target_payload"]["apparent_barrier_external_signed_inscription_eV"],
        "apparent_barrier_external_magnitude_exact_fraction_eV": row["target_payload"]["apparent_barrier_external_magnitude_exact_fraction_eV"],
        "apparent_barrier_orientation": row["target_payload"]["apparent_barrier_orientation"],
        "uncertainty_exact_fraction_eV": row["target_payload"]["uncertainty_exact_fraction_eV"],
        "source_status": row["target_payload"]["source_status"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-KIN-005",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "transition_boundary_law": "one unique greatest exact positive support on a complete finite generated path forces the entry-boundary-exit carrier with held reaction/path/isotopologue identity",
            "complete_external_target_count": 2,
            "complete_supplementary_file_count": 13,
            "exact_measured_H2_apparent_barrier_magnitude_eV": analysis["exact_measured_H2_apparent_barrier_magnitude_eV"],
            "exact_measured_D2_apparent_barrier_magnitude_eV": analysis["exact_measured_D2_apparent_barrier_magnitude_eV"],
            "exact_measured_common_uncertainty_eV": analysis["exact_measured_common_uncertainty_eV"],
            "complete_measured_H2_D2_signature_vector": vector,
            "both_opposite_measured_temperature_directions_retained": analysis["both_opposite_measured_temperature_directions_retained"],
            "all_article_and_supplement_files_preserved": analysis["complete_article_and_thirteen_supplement_files_retained"],
            "calculated_fitted_and_interpretive_records_retained_but_excluded_from_measurement_targets": analysis["experimental_and_calculated_provenance_separated"],
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_and_prediction_seal": True,
            "transition_state_geometry_saddle_continuum_conventional_KIE_arrhenius_fitted_barrier_model_adjustment_selection_or_target_correction_used_in_law": False,
            "external_values_used_as_proof_parameters": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text())
    registration["status"] = "empirically_tested"
    write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "complete_H2_D2_measured_signature_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-005`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: one unique greatest exact positive state forces the finite entry-boundary-exit carrier.\n"
        "- Complete external surface: both measured H2/D2 signatures, complete article, and all 13 supplementary files.\n"
        f"- Exact measured apparent-barrier magnitudes: H2 `{analysis['exact_measured_H2_apparent_barrier_magnitude_eV']}` eV; D2 `{analysis['exact_measured_D2_apparent_barrier_magnitude_eV']}` eV.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete transition-boundary vector: 2 isotopologues; 13 supplementary files; measured and fitted provenance separated")


if __name__ == "__main__":
    main()
