#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-009 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.solution_activity_batch_v1 import SOLUTION_ACTIVITY_SPEC  # noqa: E402
from sft.chemistry.solution_activity_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_solution_activity_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / SOLUTION_ACTIVITY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_009", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-009 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = SOLUTION_ACTIVITY_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing:
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
        manifest["claims"].append(
            {"claim_id": spec.claim_id, "execution_file": f"claims/{spec.claim_id}/execution.py"}
        )
        write_json(manifest_path, manifest)
    census = json.loads(census_path.read_text())
    census_row = next(row for row in census["claims"] if row["claim_id"] == spec.claim_id)
    package = ROOT / "claims" / spec.claim_id
    rows = _source_rows(ROOT)
    primary = json.loads(
        (
            ROOT
            / "experiments/external_sources/chemistry/snapshots/thermo-009-solution-activity-v1/solution-activity-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_solution_activity_analysis(rows, primary)
    vector = tuple(
        {
            "target_id": row["target_id"],
            "dataset_ordinal": row["target_payload"]["dataset_ordinal"],
            "source_point_ordinal": row["target_payload"]["source_point_ordinal"],
            "temperature_K_external_inscription": row["target_payload"]["temperature_K_external_inscription"],
            "relative_water_activity_external_inscription": row["target_payload"][
                "relative_water_activity_external_inscription"
            ],
            "composition_interface_entries": row["target_payload"]["composition_interface_entries"],
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
            "chemistry_obligation": "SFT-CHEM-OBL-THERMO-009",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
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
            "activity_law": "exact positive accessible component-exchange support count over held reference support count at complete composition and condition",
            "nonideal_law": "exact joint accessible support versus independently composed support relation",
            "absence_law": "external zero glyph maps only to structural EmptyOne",
            "successor_law": "common exact support replication preserves activity and non-ideal relation",
            "complete_external_target_count": 204,
            "complete_source_compound_count": 6,
            "complete_binary_dataset_count": 5,
            "complete_ternary_dataset_count": 4,
            "complete_absence_boundary_count": 68,
            "fixed_environment_temperature_K_external_inscription": "298.15",
            "minimum_activity_external_inscription": analysis["minimum_activity"],
            "maximum_activity_external_inscription": analysis["maximum_activity"],
            "distinct_activity_count": analysis["distinct_activity_count"],
            "complete_solution_activity_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_released_after_identity_seal": True,
            "all_activity_values_exact_positive_parts_of_One": analysis[
                "all_activities_exact_positive_parts_of_One"
            ],
            "all_absence_rows_translated_to_EmptyOne": analysis[
                "all_68_absence_rows_and_coordinates_translated_to_EmptyOne"
            ],
            "correlated_or_fitted_model_value_used": False,
            "external_values_used_as_proof_parameters": False,
            "imported_activity_coefficient_fugacity_or_ideal_mixture_model_used": False,
            "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True,
            "falsification_condition": empirical.falsification_condition,
        },
    }
    for name, payload in payloads.items():
        write_json(package / name, payload)
    registration_path = package / "registration.json"
    registration = json.loads(registration_path.read_text())
    registration["status"] = "empirically_tested"
    write_json(registration_path, registration)
    experiment_path = ROOT / "experiments/chemistry" / spec.experiment_id / "registration.json"
    experiment = json.loads(experiment_path.read_text())
    experiment["status"] = "complete_nine_dataset_204_row_activity_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-009`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: accessible/reference support ratio and joint-versus-independent support relation.\n"
        "- Direct NIST TRC ThermoML vector: `9` datasets and `204` direct activity rows at `298.15 K`.\n"
        "- Preserved absence boundary: `68` external zero-glyph rows translated only to structural `EmptyOne`.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n"
        f"- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n"
        f"- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    (package / "STATUS.md").write_text(status)
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(
        f"candidates: {len(sealed.census.candidates)}; survivors: "
        f"{sum(decision.survives for decision in sealed.decisions)}"
    )
    print("NIST TRC ThermoML activity: 9 datasets; 204 rows; 68 EmptyOne boundaries")


if __name__ == "__main__":
    main()
