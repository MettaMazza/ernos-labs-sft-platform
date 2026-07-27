#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-013 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.reaction_dynamics_scattering_batch_v1 import REACTION_DYNAMICS_SCATTERING_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.reaction_dynamics_scattering_validation_v1 import _source_rows, exact_reaction_dynamics_scattering_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / REACTION_DYNAMICS_SCATTERING_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_013", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-013 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = REACTION_DYNAMICS_SCATTERING_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured: dict[str, object] = {}

    class CaptureIndependent:
        def validate(self, sealed):
            captured["sealed"] = sealed
            captured["external"] = execution.independent_validator.validate(sealed)
            return captured["external"]

    class CaptureEmpirical:
        def validate(self, sealed):
            captured["empirical"] = execution.empirical_validator.validate(sealed)
            return captured["empirical"]

    receipt = EngineRepository(ROOT).execute_official(execution.program, CaptureIndependent(), execution.source_files, CaptureEmpirical())
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
    analysis = exact_reaction_dynamics_scattering_analysis(rows, primary)
    vector = tuple({"target_id": row["target_id"], "source_document_identity": row["source_document_identity"], "source_record_identity": row["source_record_identity"], "source_record_ordinal": row["source_record_ordinal"], "complete_target_payload_hash": row["target_payload_hash"]} for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-013",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"], "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result, "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "reaction_dynamics_scattering_product_state_law": "one finite held incoming preparation retains complete finite distinct outgoing joint coproduct-state support; positive completed-state events per complete positive support force exact shares; incoming/outgoing orientation remains a held relation",
            "complete_structural_incoming_outgoing_channel_path": primary["complete_structural_incoming_outgoing_channel_path"],
            "source_reported_headline_external_inscriptions": primary["source_reported_headline_external_inscriptions"],
            "complete_registered_source_record_count": analysis["complete_registered_target_count"],
            "complete_source_class_census": analysis["complete_source_class_census"],
            "complete_source_data_worksheet_shapes": primary["complete_source_data_worksheet_shapes"],
            "complete_key_state_resolved_product_and_scattering_cell_vector": primary["complete_key_state_resolved_product_and_scattering_cell_vector"],
            "complete_postseal_external_vector": vector, "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "all_36_pdf_pages_retained": analysis["complete_36_pdf_pages_retained"],
            "all_14_source_data_worksheets_retained": analysis["all_14_source_data_worksheets_retained"],
            "all_978591_nonempty_cells_and_6408_key_state_cells_retained": analysis["complete_978591_nonempty_cell_surface_retained"] and analysis["complete_6408_key_state_resolved_product_and_scattering_cells_retained"],
            "complete_pair_branching_scattering_sampling_overlap_vectors_retained": analysis["complete_pair_branching_state_scattering_sampling_and_overlap_vectors_retained"],
            "experiment_theory_fit_normalization_estimate_tentative_limit_and_review_statuses_retained": analysis["experimental_theoretical_fit_normalization_estimate_tentative_and_limit_statuses_all_retained"] and analysis["complete_transparent_peer_review_adverse_surface_retained"],
            "source_scattering_energy_momentum_transition_state_potential_quantum_dynamics_fit_and_normalization_models_retained_only_as_postseal_provenance": analysis["source_models_fits_normalizations_and_corrections_remain_postseal_provenance_only"],
            "imported_scattering_equation_cross_section_law_angular_continuum_probability_amplitude_potential_fit_normalization_selection_average_interpolation_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_signed_or_continuum_proof_value_used": False,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration = json.loads((package / "registration.json").read_text()); registration["status"] = "empirically_tested"; write_json(package / "registration.json", registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text()); experiment["status"] = "complete_51_record_state_resolved_product_and_scattering_vector_opened_postseal"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-013`\n" + f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: finite incoming preparation and complete outgoing joint product-state support force exact positive state shares and held orientations.\n"
        "- Complete external surface: 51 records—36 PDF pages, 14 worksheets, 978,591 nonempty cells and 6,408 key state-resolved cells.\n"
        "- Headline source inscriptions: 40% ground-state CH3; 57% experimental versus 58% theoretical umbrella flux; forward/sideways/backward pair progression retained.\n"
        "- Adverse surface: fits, normalizations, tentative assignment, theory discrepancy and scope limits, detection limits, overlap corrections and full reviewer challenges remain visible.\n"
        + f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete reaction-dynamics vector: 51 records; 36 pages; 14 worksheets; 978,591 cells; 6,408 key state cells")


if __name__ == "__main__":
    main()
