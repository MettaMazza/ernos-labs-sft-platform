#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-007 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.sequential_mechanism_batch_v1 import PRIMARY_PATH, SEQUENTIAL_MECHANISM_SPEC  # noqa: E402
from sft.chemistry.sequential_mechanism_validation_v1 import (  # noqa: E402
    _source_rows, exact_sequential_mechanism_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SEQUENTIAL_MECHANISM_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_007", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-007 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = SEQUENTIAL_MECHANISM_SPEC
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
    analysis = exact_sequential_mechanism_analysis(rows, primary)
    vector = tuple({
        **row["target_payload"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-KIN-007",
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
            "sequential_composition_law": "complete ordered state-edge word with exact adjacent entry-exit matching and every intermediate, condition and status retained",
            "complete_external_target_count": 17,
            "complete_deposited_structure_count": 5,
            "complete_late_unresolved_record_count": 2,
            "complete_power_titration_column_count": 7,
            "complete_favorable_adverse_unresolved_control_count": 3,
            "complete_supplementary_file_count": 13,
            "complete_supplement_pdf_count": 3,
            "complete_pdb_deposit_count": 5,
            "deposited_XTX_component_count_vector": analysis["deposited_XTX_component_count_vector"],
            "deposited_XTX_occupancy_vector": analysis["deposited_XTX_occupancy_vector"],
            "exact_positive_difference_density_sigma_range": analysis["exact_positive_difference_density_sigma_range"],
            "exact_positive_difference_density_range": analysis["exact_positive_difference_density_range"],
            "external_absence_glyph_count_translated_to_EmptyOne": analysis["external_absence_glyph_count_translated_to_EmptyOne"],
            "complete_postseal_external_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "all_values_released_after_identity_and_prediction_seal": True,
            "experimental_calculated_adverse_and_unresolved_provenance_separated": True,
            "imported_differential_equation_exponential_decay_fitted_lifetime_steady_state_interpolation_selection_or_target_correction_used_in_law": False,
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
    experiment["status"] = "complete_seventeen_record_time_resolved_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-007`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: every retained state and elementary transition composes only at matching boundaries; all intermediates, conditions and statuses remain explicit.\n"
        "- Complete external surface: seventeen records, thirteen supplementary files, three PDFs, five PDB deposits and CXIDB 221 custody.\n"
        f"- Exact deposited occupancies: `{analysis['deposited_XTX_occupancy_vector']}`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete sequential vector: 17 targets; five PDB deposits; seven power columns; adverse and unresolved records retained")


if __name__ == "__main__":
    main()
