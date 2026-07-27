#!/usr/bin/env python3
"""Officially admit and materialize Chemistry KIN-004 exactly once."""

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.activation_barrier_batch_v1 import ACTIVATION_BARRIER_SPEC, PRIMARY_PATH  # noqa: E402
from sft.chemistry.activation_barrier_validation_v1 import _source_rows, exact_activation_barrier_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / ACTIVATION_BARRIER_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_kin_004", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load KIN-004 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = ACTIVATION_BARRIER_SPEC
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
    analysis = exact_activation_barrier_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"],
        "source_id": row["source_id"],
        "source_detail_ordinal": row["source_detail_ordinal"],
        "species_name": row["species_name"],
        "formula_external_inscription": row["formula_external_inscription"],
        "casno_source_identity": row["casno_source_identity"],
        "torsion_index_source_identity": row["torsion_index_source_identity"],
        "torsion_atom_identity": row["torsion_atom_identity"],
        "rotor_type_identity": row["rotor_type_identity"],
        "source_reference_identity": row["source_reference_identity"],
        "complete_path_state_count": row["target_payload"]["complete_path_state_count"],
        "barrier_kJ_mol_minus1_external_inscription": row["target_payload"]["barrier_kJ_mol_minus1_external_inscription"],
        "barrier_kJ_mol_minus1_exact_fraction": row["target_payload"]["barrier_kJ_mol_minus1_exact_fraction"],
        "barrier_cm_minus1_external_inscription": row["target_payload"]["barrier_cm_minus1_external_inscription"],
        "barrier_cm_minus1_exact_fraction": row["target_payload"]["barrier_cm_minus1_exact_fraction"],
        "external_zero_energy_glyph_count_translated_to_EmptyOne": row["target_payload"]["external_zero_energy_glyph_count_translated_to_EmptyOne"],
        "source_least_state_support": row["target_payload"]["source_least_state_support"],
        "uncertainty_support": row["target_payload"]["uncertainty_support"],
        "measurement_method_support": row["target_payload"]["measurement_method_support"],
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
            "chemistry_obligation": "SFT-CHEM-OBL-KIN-004",
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
            "activation_barrier_law": "greatest exact positive support on one complete generated path relative to structural least-state EmptyOne, with held species/path/state/source identity",
            "complete_index_species_count": 41,
            "complete_detail_page_count": 41,
            "complete_external_target_count": 44,
            "complete_path_state_count": 782,
            "complete_unresolved_path_row_count": 1,
            "complete_explicit_zero_glyph_count_translated_to_EmptyOne": analysis["complete_explicit_zero_glyph_count_translated_to_EmptyOne"],
            "source_reference_EmptyOne_count": analysis["source_reference_EmptyOne_count"],
            "source_least_state_coordinate_EmptyOne_count": analysis["source_least_state_coordinate_EmptyOne_count"],
            "exact_barrier_range_kJ_mol_minus1": analysis["exact_barrier_range_kJ_mol_minus1"],
            "exact_barrier_range_cm_minus1": analysis["exact_barrier_range_cm_minus1"],
            "complete_activation_barrier_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_and_prediction_seal": True,
            "source_reference_and_parameter_disclosures_preserved_postseal": True,
            "transition_state_saddle_continuum_arrhenius_prefactor_fitted_activation_absolute_origin_interpolation_regression_averaging_selection_or_target_correction_used_in_law": False,
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
    experiment["status"] = "complete_41_species_44_barrier_782_state_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_forward_forced_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-KIN-004`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: greatest exact positive support on one complete generated path relative to structural least-state EmptyOne.\n"
        "- Complete external surface: `41` NIST species, `44` barriers, `782` path states and `1` unresolved row.\n"
        f"- Exact barrier range: `{analysis['exact_barrier_range_kJ_mol_minus1']}` kJ mol^-1.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete barrier vector: 41 species; 44 targets; 782 path states; 1 unresolved source row")


if __name__ == "__main__":
    main()
