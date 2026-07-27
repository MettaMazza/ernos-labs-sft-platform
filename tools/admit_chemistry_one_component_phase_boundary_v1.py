#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-012 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.one_component_phase_boundary_batch_v1 import ONE_COMPONENT_PHASE_BOUNDARY_SPEC  # noqa: E402
from sft.chemistry.one_component_phase_boundary_validation_v1 import _source_rows, exact_phase_boundary_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / ONE_COMPONENT_PHASE_BOUNDARY_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_012", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-012 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = ONE_COMPONENT_PHASE_BOUNDARY_SPEC
    census_path = ROOT / "census/claims.json"
    existing = {row["claim_id"] for row in json.loads(census_path.read_text())["claims"]}
    if spec.claim_id in existing:
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
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-012-one-component-phase-boundary-v1/one-component-phase-boundary-primary-records-v1.json").read_text())
    analysis = exact_phase_boundary_analysis(rows, primary)
    vector = tuple({
        "target_id": row["target_id"], "component_orgnum": row["target_payload"]["component_orgnum"],
        "dataset_ordinal": row["target_payload"]["dataset_ordinal"], "source_point_ordinal": row["target_payload"]["source_point_ordinal"],
        "temperature_K_external_inscription": row["target_payload"]["temperature_K_external_inscription"],
        "pressure_kPa_external_inscription": row["target_payload"]["pressure_kPa_external_inscription"],
        "pressure_uncertainty": row["target_payload"]["pressure_uncertainty"],
        "complete_target_payload_hash": row["target_payload_hash"],
    } for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id, "chemistry_obligation": "SFT-CHEM-OBL-THERMO-012",
            "status": "model_admitted_observationally_derived_empirically_tested_and_independently_replicated",
            "source_manifest_hash": execution.program.registration.source_hash, "derivation_seal_hash": sealed.seal_hash,
            "independent_implementation_hash": external.implementation_hash, "independent_certificate_hash": external.certificate_hash,
            "external_validation_hash": receipt.external_validation_hash, "empirical_validation_hash": receipt.empirical_validation_hash,
            "measurement_receipt_hash": empirical.measurement_receipt_hash, "engine_receipt_hash": receipt.receipt_hash,
            "engine_receipt_path": census_row["receipt_path"], "closure_scope": receipt.closure_status,
            "exact_result": spec.exact_result, "candidate_count": len(sealed.census.candidates),
            "unique_survivor_count": sum(decision.survives for decision in sealed.decisions),
            "coexistence_law": "exact component exchange-support balance between two distinct held phases",
            "phase_rule_boundary": "one component and two phases retain exactly one independent held coordinate support",
            "finite_boundary_law": "complete source-ordered word of exact positive temperature-pressure coexistence points",
            "successor_law": "stable liquid-vapor successors preserve strict exact temperature-pressure co-order; common support replication preserves balance and order",
            "complete_external_target_count": 15, "complete_direct_dataset_count": 3,
            "complete_distinct_compound_count": 2, "complete_adjacent_successor_count": 12,
            "minimum_temperature_K_external_inscription": analysis["minimum_temperature_K"],
            "maximum_temperature_K_external_inscription": analysis["maximum_temperature_K"],
            "minimum_pressure_kPa_external_inscription": analysis["minimum_pressure_kPa"],
            "maximum_pressure_kPa_external_inscription": analysis["maximum_pressure_kPa"],
            "complete_one_component_coexistence_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved, "external_data_source_ids": list(empirical.data_source_ids),
            "all_compound_phase_temperature_pressure_uncertainty_values_released_after_identity_seal": True,
            "clausius_clapeyron_differential_eos_interpolation_regression_or_fit_used": False,
            "external_values_used_as_proof_parameters": False, "numerical_zero_used": False,
            "negative_irrational_imaginary_logarithmic_or_continuum_proof_value_used": False,
            "observational_development_disclosed": True, "falsification_condition": empirical.falsification_condition,
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
    experiment["status"] = "complete_three_dataset_fifteen_point_coexistence_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-012`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: finite exchange-balanced coexistence word with one independent support and exact temperature-pressure co-order.\n"
        "- Complete NIST surface: `3` direct datasets, `15` points, `2` compounds and `12` adjacent successions.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n"
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("NIST one-component coexistence: 3 datasets; 15 points; 12 ordered successions")


if __name__ == "__main__":
    main()
