#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-015 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.solvation_dissolution_batch_v1 import SOLVATION_DISSOLUTION_SPEC  # noqa: E402
from sft.chemistry.solvation_dissolution_law_v1 import external_order_as_fold_relation  # noqa: E402
from sft.chemistry.solvation_dissolution_validation_v1 import _source_rows, exact_solvation_dissolution_analysis  # noqa: E402
from sft.claim_evidence import EmptyOne  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SOLVATION_DISSOLUTION_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_015", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-015 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = SOLVATION_DISSOLUTION_SPEC
    census_path = ROOT / "census/claims.json"
    if spec.claim_id in {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}:
        raise SystemExit("claim already admitted; immutable receipt preserved")
    execution = load_execution()
    captured = {}

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
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-015-solvation-dissolution-v1/solvation-dissolution-primary-records-v1.json").read_text())
    analysis = exact_solvation_dissolution_analysis(rows, primary)
    vector = []
    for row in rows:
        target = row["target_payload"]
        if row["source_class"] == "solvation":
            relation = external_order_as_fold_relation(
                target["experimental_hydration_free_energy_kcal_per_mol_external_inscription"]
            )
            vector.append({
                "target_id": row["target_id"], "source_id": row["source_id"], "source_class": "solvation",
                "source_row_ordinal": row["source_row_ordinal"], "solute_compound_id": target["solute_compound_id"],
                "solute_name": target["solute_name"], "solvent_identity": target["solvent_identity"],
                "source_state": target["source_state"], "destination_state": target["destination_state"],
                "held_free_order_orientation": relation.orientation.label,
                "exact_positive_magnitude_or_EmptyOne": "EmptyOne" if isinstance(relation.magnitude, EmptyOne) else str(relation.magnitude.fraction),
                "experimental_hydration_free_energy_external_inscription": target["experimental_hydration_free_energy_kcal_per_mol_external_inscription"],
                "experimental_uncertainty_external_inscription": target["experimental_uncertainty_kcal_per_mol_external_inscription"],
                "experimental_reference": target["experimental_reference"],
                "complete_target_payload_hash": row["target_payload_hash"],
            })
        else:
            vector.append({
                "target_id": row["target_id"], "source_id": row["source_id"], "source_class": "dissolution",
                "dataset_ordinal": row["dataset_ordinal"], "source_point_ordinal": row["source_point_ordinal"],
                "component_orgnums": target["component_orgnums"], "solute_orgnum": target["solute_orgnum"],
                "solvent_orgnums": target["solvent_orgnums"], "source_state": target["source_state"],
                "destination_state": target["destination_state"],
                "solubility_mole_fraction_external_inscription": target["solubility_mole_fraction_external_inscription"],
                "solubility_uncertainty_external_inscription": target["solubility_uncertainty_external_inscription"],
                "variable_external_inscriptions": target["variable_external_inscriptions"],
                "pressure_constraint_external_inscription": target["pressure_constraint_external_inscription"],
                "complete_target_payload_hash": row["target_payload_hash"],
            })
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-015",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash,
            "derivation_seal_hash": sealed.seal_hash, "independent_implementation_hash": external.implementation_hash,
            "independent_certificate_hash": external.certificate_hash, "external_validation_hash": receipt.external_validation_hash,
            "empirical_validation_hash": receipt.empirical_validation_hash, "measurement_receipt_hash": empirical.measurement_receipt_hash,
            "engine_receipt_hash": receipt.receipt_hash, "engine_receipt_path": census_row["receipt_path"],
            "closure_scope": receipt.closure_status, "exact_result": spec.exact_result,
            "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "carrier_law": "solute, every solvent, source state, destination state and exact condition remain held",
            "free_order_law": "external sign becomes held state orientation plus exact positive magnitude; coincident external glyph becomes EmptyOne",
            "dissolution_law": "solubility is exact positive condition-bound composition capacity",
            "complete_external_target_count": 799, "complete_solvation_target_count": 642,
            "complete_dissolution_target_count": 157, "complete_dissolution_dataset_count": 7,
            "complete_mixed_solvent_target_count": 93,
            "solvation_orientation_counts": analysis["solvation_orientation_counts"],
            "structural_EmptyOne_condition_coordinate_count": analysis["structural_EmptyOne_condition_coordinate_count"],
            "exact_external_ranges": analysis["exact_ranges"], "complete_solvation_dissolution_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_values_released_after_identity_and_prediction_seal": True,
            "calculated_and_correlated_companion_fields_preserved_but_excluded_from_measurements": True,
            "force_field_continuum_partition_activity_solubility_product_logarithm_correlation_regression_fit_selection_or_target_correction_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text()); registration["status"] = "empirically_tested"; write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text()); experiment["status"] = "complete_642_solvation_157_dissolution_vector_opened_postseal"; write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-015`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: complete component/state/condition carrier with held free-order orientation, exact positive magnitude/capacity and structural EmptyOne.\n"
        "- Complete external surface: `642` FreeSolv experimental records and `157` direct NIST solubility records.\n"
        "- Orientation census: `556` destination retained, `84` source retained, `2` coincident/EmptyOne.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("complete sources: 642 FreeSolv solvation; 157 NIST dissolution; 799 total")


if __name__ == "__main__":
    main()
