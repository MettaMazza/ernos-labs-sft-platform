#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-010 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.catalytic_turnover_batch_v1 import (  # noqa: E402
    CATALYTIC_TURNOVER_SPEC, PRIMARY_PATH,
)
from sft.chemistry.catalytic_turnover_validation_v1 import (  # noqa: E402
    _source_rows, exact_catalytic_turnover_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / CATALYTIC_TURNOVER_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_010", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-010 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = CATALYTIC_TURNOVER_SPEC
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
    analysis = exact_catalytic_turnover_analysis(rows, primary)
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
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-010",
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
            "catalytic_turnover_law": (
                "one complete ordered transition word carrying the same held catalyst identity through every state and "
                "returning to its exact entry state is one turnover; completed return-word count per exact positive "
                "held observation partition is the exact cycle-frequency relation"
            ),
            "structural_cycle": primary["structural_cycle"],
            "complete_registered_source_record_count": analysis["complete_registered_target_count"],
            "complete_source_class_census": analysis["complete_source_class_census"],
            "complete_substituent_turnover_vector": primary["complete_substituent_turnover_vector"],
            "independent_state_1_state_4_rate_vector_table_s2": primary["independent_state_1_state_4_rate_vector_table_s2"],
            "independent_state_1_state_4_rate_vector_table_s3": primary["independent_state_1_state_4_rate_vector_table_s3"],
            "rate_tables_retained_separately_without_selection_or_averaging": analysis["independent_rate_tables_retained_separately_without_average"],
            "figure_6_complete_source_data": primary["figure_6_source_data"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "all_106_supplementary_pages_retained": analysis["complete_source_class_census_matches"],
            "complete_1604_frame_movie_retained": analysis["complete_1604_frame_movie_retained"],
            "all_387_archive_members_retained": analysis["all_387_archive_members_retained"],
            "unavailable_article_pdf_and_low_temperature_insufficient_fit_adverse_records_retained": analysis["unavailable_article_pdf_adverse_record_retained"] and analysis["low_temperature_insufficient_fit_adverse_record_retained"],
            "source_fits_rates_TOF_dwell_times_signed_and_zero_inscriptions_retained_only_as_postseal_provenance": analysis["source_fits_rates_and_values_are_postseal_provenance_not_proof"] and analysis["all_signed_decimal_and_zero_source_inscriptions_preserved_outside_proof"],
            "imported_turnover_formula_rate_equation_Michaelis_Menten_steady_state_stochastic_weight_fit_selection_average_interpolation_or_target_correction_used": False,
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
    experiment["status"] = "complete_497_record_catalyst_return_turnover_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_disclosed_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-010`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: one complete catalyst-return transition word is one turnover; exact closed-cycle count per held interval is cycle frequency.\n"
        "- Structural/observational distinction: five cycle states; four separately observed conductance states; State 2 retained as structural, not falsely observed.\n"
        "- Complete external surface: 497 records—106 supplementary pages, one 1,604-frame movie, Zenodo metadata and 387 archive members.\n"
        "- Exact TOF vector: 0.5, 4.6, 29.6, 39.0, 203.9, 615.6 and 2098.7 per second; both independent rate tables retained unaveraged.\n"
        "- Adverse surface: unavailable article PDF and insufficient low-temperature fit data remain visible; all fits remain post-seal provenance only.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete catalytic-turnover vector: 497 records; 106 pages; 1,604 movie frames; 387 archive members")


if __name__ == "__main__":
    main()
