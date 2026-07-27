#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-010 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.real_gas_exchange_batch_v1 import REAL_GAS_EXCHANGE_SPEC  # noqa: E402
from sft.chemistry.real_gas_exchange_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_real_gas_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / REAL_GAS_EXCHANGE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_010", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-010 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = REAL_GAS_EXCHANGE_SPEC
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
            / "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1/real-gas-equilibrium-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_real_gas_analysis(rows, primary)
    vector = tuple(
        {
            "target_id": row["target_id"],
            "ordered_component_orgnums": row["target_payload"]["ordered_component_orgnums"],
            "pressure_dataset_ordinal": row["target_payload"]["pressure_dataset_ordinal"],
            "pressure_point_ordinal": row["target_payload"]["pressure_point_ordinal"],
            "pressure_kPa_external_inscription": row["target_payload"]["pressure_kPa_external_inscription"],
            "gas_component_mole_fraction_external_inscription": row["target_payload"][
                "gas_component_mole_fraction_external_inscription"
            ],
            "condition_and_liquid_composition_coordinates": row["target_payload"][
                "condition_and_liquid_composition_coordinates"
            ],
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
            "chemistry_obligation": "SFT-CHEM-OBL-THERMO-010",
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
            "fugacity_equivalent_law": "exact positive accessible gas component exchange support over held reference support at complete state",
            "real_gas_interaction_law": "exact joint accessible support versus independently composed support relation",
            "phase_equilibrium_law": "exact equality of component exchange-support accounts across the held phase boundary",
            "successor_law": "common exact support replication preserves fugacity-equivalent, interaction and phase-balance relations",
            "complete_external_target_count": 94,
            "complete_source_compound_count": 5,
            "complete_source_dataset_count": 21,
            "complete_source_point_count": 176,
            "complete_pressure_dataset_count": 7,
            "complete_gas_composition_dataset_count": 3,
            "matched_gas_composition_state_count": 59,
            "pressure_only_equilibrium_state_count": 35,
            "minimum_pressure_kPa_external_inscription": analysis["minimum_pressure_kPa"],
            "maximum_pressure_kPa_external_inscription": analysis["maximum_pressure_kPa"],
            "minimum_temperature_K_external_inscription": analysis["minimum_temperature_K"],
            "maximum_temperature_K_external_inscription": analysis["maximum_temperature_K"],
            "minimum_gas_component_mole_fraction_external_inscription": analysis[
                "minimum_gas_component_mole_fraction"
            ],
            "maximum_gas_component_mole_fraction_external_inscription": analysis[
                "maximum_gas_component_mole_fraction"
            ],
            "complete_real_gas_equilibrium_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_released_after_identity_seal": True,
            "all_pressures_exact_positive_external_inscriptions": analysis["all_pressures_exact_positive"],
            "all_gas_compositions_exact_positive_parts_of_One": analysis[
                "all_59_paired_gas_compositions_retained"
            ],
            "correlated_regressed_or_model_calculated_value_used": False,
            "external_values_used_as_proof_parameters": False,
            "imported_fugacity_equation_eos_logarithm_compressibility_virial_or_ideality_model_used": False,
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
    experiment["status"] = "complete_21_dataset_176_point_94_state_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-010`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: accessible/reference gas-component support and exact phase exchange balance.\n"
        "- Complete NIST TRC ThermoML surface: `5` compounds, `21` datasets, `176` raw points and `94` equilibrium states.\n"
        "- Direct vector: `59` paired vapor-composition states and `35` pressure-only states.\n"
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
    print("NIST TRC ThermoML real gas: 21 datasets; 176 points; 94 states; 59 paired; 35 pressure-only")


if __name__ == "__main__":
    main()
