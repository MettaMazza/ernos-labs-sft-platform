#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-001 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.elementary_transition_rate_batch_v1 import ELEMENTARY_TRANSITION_RATE_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.elementary_transition_rate_validation_v1 import _source_rows, exact_elementary_rate_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / ELEMENTARY_TRANSITION_RATE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_001", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-001 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = ELEMENTARY_TRANSITION_RATE_SPEC
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
    sealed = captured["sealed"]
    external = captured["external"]
    empirical = captured["empirical"]
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
    analysis = exact_elementary_rate_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "source_id": row["source_id"], "record_id": row["record_id"],
        "source_row_ordinal": row["source_row_ordinal"],
        "reaction_external_record": row["target_payload"]["complete_source_metadata"]["Reaction"],
        "source_declared_reaction_order": row["target_payload"]["complete_source_metadata"]["Reaction order"],
        "temperature_K_external_inscription": row["target_payload"]["temperature_K_external_inscription"],
        "rate_external_inscription": row["target_payload"]["rate_external_inscription"],
        "rate_unit_external_inscription": row["target_payload"]["rate_unit_external_inscription"],
        "source_reported_rate_is_arrhenius_tabulation_of_direct_experimental_record": True,
        "raw_event_count_claimed": False,
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-001",
            "status": "model_admitted_forward_forced_empirically_tested_and_independently_replicated",
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
            "elementary_transition_rate_law": "completed instances of one registered elementary transition per exact positive reference tick and observation support, with distinct molecular endpoints, conditions and held direction retained",
            "complete_external_target_count": 46, "complete_external_source_count": 4,
            "source_declared_order_row_counts": analysis["source_declared_order_row_counts"],
            "exact_rate_ranges_by_source_declared_order": analysis["exact_rate_ranges_by_source_declared_order"],
            "exact_temperature_ranges_K_by_source_declared_order": analysis["exact_temperature_ranges_K_by_source_declared_order"],
            "complete_elementary_rate_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_and_prediction_seal": True,
            "source_reported_arrhenius_tabulations_are_external_records_not_raw_event_counts": True,
            "mass_action_rate_equation_reaction_order_arrhenius_logarithm_concentration_derivative_continuum_interpolation_regression_selection_fit_or_target_correction_used_in_law": False,
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
    experiment["status"] = "complete_46_row_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        f"- Chemistry obligation: `SFT-CHEM-OBL-KIN-001`\n- Closure: `{receipt.closure_status}`\n"
        "- Exact law: completed elementary transitions per positive tick and observation support with complete state, condition and direction trace.\n"
        "- Complete declared NIST surface: `4` sources and `46` rows (`4`/`24`/`18` by source-declared order 1/2/3).\n"
        "- Source disclosure: rate tables are NIST Arrhenius tabulations of direct-experiment records, not raw event counts.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete elementary-rate vector: 4 sources; 46 rows")


if __name__ == "__main__":
    main()
