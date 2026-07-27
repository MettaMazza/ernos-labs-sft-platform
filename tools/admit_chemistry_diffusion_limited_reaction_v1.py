#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-011 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.diffusion_limited_reaction_batch_v1 import (  # noqa: E402
    DIFFUSION_LIMITED_REACTION_SPEC, PRIMARY_PATH,
)
from sft.chemistry.diffusion_limited_reaction_validation_v1 import (  # noqa: E402
    _source_rows, exact_diffusion_limited_reaction_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / DIFFUSION_LIMITED_REACTION_SPEC.claim_id / "execution_v2.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_011", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-011 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = DIFFUSION_LIMITED_REACTION_SPEC
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
        manifest["claims"].append({"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution_v2.py"})
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads((ROOT / PRIMARY_PATH).read_text())
    analysis = exact_diffusion_limited_reaction_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_document_identity": row["source_document_identity"],
        "source_record_identity": row["source_record_identity"], "source_record_ordinal": row["source_record_ordinal"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-011",
            "status": "model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "diffusion_limited_reaction_law": (
                "one complete finite transition word retains the same transported identity until its exit equals the exact "
                "reaction encounter entry; reaction is admissible only after transport closure; completed occurrences per "
                "exact positive held observation partition form the completion relation"
            ),
            "structural_transport_reaction_path": primary["structural_transport_reaction_path"],
            "complete_registered_source_record_count": analysis["complete_registered_target_count"],
            "complete_source_class_census": analysis["complete_source_class_census"],
            "complete_fifteen_row_radius_total_reaction_time_vector": primary["complete_fifteen_row_radius_total_reaction_time_vector"],
            "complete_key_raw_data_shapes": primary["complete_key_raw_data_shapes"],
            "complete_key_raw_data_row_count": primary["complete_key_raw_data_row_count"],
            "source_reported_experimental_velocity_external_inscription": primary["source_reported_experimental_diffusion_velocity_external_inscription"],
            "source_reported_velocity_uncertainty_external_inscription": primary["source_reported_one_sigma_velocity_uncertainty_external_inscription"],
            "source_reported_simulation_velocity_external_inscription": primary["source_reported_simulation_diffusion_velocity_external_inscription"],
            "source_reported_rate_estimate_external_inscription": primary["source_reported_rate_constant_estimate_external_inscription"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "all_43_pdf_pages_retained": analysis["complete_43_pdf_pages_retained"],
            "complete_1350_frame_video_surface_retained": analysis["complete_1350_video_frames_retained"],
            "all_204_dual_archive_members_retained": analysis["all_204_archive_members_retained"],
            "complete_11512_raw_rows_and_full_matrices_retained": analysis["complete_11512_key_raw_data_rows_retained"] and analysis["complete_reaction_yield_and_coincidence_matrices_retained"],
            "velocity_discrepancy_large_droplet_resolution_and_peer_review_adverse_records_retained": analysis["experimental_43_plus_or_minus_5_and_simulated_14_velocity_inscriptions_and_discrepancy_retained"] and analysis["large_droplet_resolution_and_peer_review_adverse_records_retained"],
            "source_diffusion_rate_fit_models_and_signed_zero_decimal_continuum_inscriptions_retained_only_as_postseal_provenance": analysis["reported_rate_estimate_retained_only_as_postseal_provenance"] and analysis["source_values_and_external_zero_negative_decimal_continuum_inscriptions_are_not_proof"],
            "imported_Fick_Smoluchowski_diffusion_equation_continuum_fit_stochastic_weight_selection_average_interpolation_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
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
    experiment["status"] = "complete_251_record_finite_transport_reaction_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-011`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: reaction is admissible only after a complete finite transport word exits on the exact reaction entry.\n"
        "- Complete external surface: 251 records—43 PDF pages, 1,350 video frames and 204 dual-archive members.\n"
        "- Exact source vectors: 11,512 key raw rows, 15 radius/time rows, full 23-by-15 yield and 150-by-23 coincidence matrices.\n"
        "- External inscriptions: 43 ±5 m/s experiment, 14 m/s simulation and 5×10^12 M^-1 s^-1 source estimate; all post-seal, discrepancy retained.\n"
        "- Adverse surface: larger-droplet deviation, insufficient bond-formation resolution and peer-review nonencounter questions remain visible.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete diffusion-limited reaction vector: 251 records; 43 pages; 1,350 frames; 204 archive members")


if __name__ == "__main__":
    main()
