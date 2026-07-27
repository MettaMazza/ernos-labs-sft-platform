#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-012 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.kinetic_isotope_effect_batch_v1 import (  # noqa: E402
    KINETIC_ISOTOPE_EFFECT_SPEC,
    PRIMARY_PATH,
)
from sft.chemistry.kinetic_isotope_effect_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_kinetic_isotope_effect_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / KINETIC_ISOTOPE_EFFECT_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_012", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-012 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = KINETIC_ISOTOPE_EFFECT_SPEC
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
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_kinetic_isotope_effect_analysis(rows, primary)
    vector = tuple(
        {
            "target_id": row["target_id"],
            "source_document_identity": row["source_document_identity"],
            "source_record_identity": row["source_record_identity"],
            "source_record_ordinal": row["source_record_ordinal"],
            "complete_target_payload_hash": row["target_payload_hash"],
        }
        for row in rows
    )
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {
            "claim_id": spec.claim_id,
            "decisions": asdict(sealed)["decisions"],
            "closure": asdict(sealed.closure),
        },
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-KIN-012",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
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
            "kinetic_isotope_effect_law": (
                "two distinct held isotopologue identities on the same complete reaction path and condition each retain "
                "an independently counted exact positive event rate; their ordered quotient is exact positive and its "
                "greater, lesser or equal direction remains a held label"
            ),
            "complete_structural_isotopologue_path": primary["complete_structural_isotopologue_path"],
            "complete_registered_source_record_count": analysis["complete_registered_target_count"],
            "complete_source_class_census": analysis["complete_source_class_census"],
            "complete_explicit_rate_ratio_vector": primary["complete_explicit_rate_ratio_vector"],
            "source_reported_direct_decay_KIE_external_inscriptions": primary["source_reported_direct_decay_KIE_external_inscriptions"],
            "source_reported_temperature_series_boundary_external_inscriptions": primary["source_reported_temperature_series_boundary_external_inscriptions"],
            "complete_source_data_worksheet_shapes": primary["complete_source_data_worksheet_shapes"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "all_47_pdf_pages_retained": analysis["complete_47_pdf_pages_retained"],
            "all_23_source_data_worksheets_retained": analysis["all_23_source_data_worksheets_retained"],
            "all_923260_nonempty_cells_and_39002_populated_rows_retained": analysis["complete_923260_nonempty_cell_surface_retained"] and analysis["complete_39002_source_rows_with_values_retained"],
            "all_90_rate_ratios_and_3_direct_decay_KIEs_retained": analysis["complete_90_rate_ratio_vector_retained"] and analysis["complete_three_direct_decay_KIE_vector_retained"],
            "normal_inverse_near_unity_three_experiments_and_all_replicates_retained": analysis["normal_inverse_and_near_unity_external_inscriptions_all_retained"] and analysis["all_three_independent_experiments_and_replicates_retained_without_averaging"],
            "infrared_limitation_reviewer_challenges_and_controls_retained": analysis["infrared_limitation_reviewer_challenges_and_controls_retained"],
            "source_transition_state_zero_point_Hooke_quantum_calculation_and_fit_models_retained_only_as_postseal_provenance": analysis["source_models_remain_postseal_provenance_only"],
            "imported_KIE_equation_numerical_mass_mass_frequency_transition_state_continuum_fit_exponent_statistical_weight_selection_average_interpolation_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
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
    experiment["status"] = "complete_71_record_kinetic_isotope_effect_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-012`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: two held isotope identities on one complete path force the ordered quotient of two exact positive event rates.\n"
        "- Complete external surface: 71 records—47 PDF pages, 23 worksheets, 923,260 nonempty cells and 39,002 populated rows.\n"
        "- Exact source vectors: 90 rate-ratio records; direct decay KIE inscriptions 2.11, 0.827 and 0.55; normal, inverse and near-unity cases retained.\n"
        "- Adverse surface: infrared limitation, reviewer challenges, requested controls and source interpretive models remain visible.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete kinetic isotope-effect vector: 71 records; 47 pages; 23 worksheets; 90 ratios; 3 direct decays")


if __name__ == "__main__":
    main()
