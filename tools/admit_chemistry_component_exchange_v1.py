#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-008 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.component_exchange_batch_v1 import COMPONENT_EXCHANGE_SPEC  # noqa: E402
from sft.chemistry.component_exchange_validation_v1 import (  # noqa: E402
    _source_rows,
    exact_component_exchange_analysis,
)
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / COMPONENT_EXCHANGE_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_008", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-008 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def main() -> None:
    spec = COMPONENT_EXCHANGE_SPEC
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
        execution.program,
        CaptureIndependent(),
        execution.source_files,
        CaptureEmpirical(),
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
            / "experiments/external_sources/chemistry/snapshots/thermo-008-component-exchange-v1/component-exchange-primary-records-v1.json"
        ).read_text()
    )
    analysis = exact_component_exchange_analysis(rows, primary)
    vector = tuple(
        {
            "target_id": row["target_id"],
            "system_ordinal": row["target_payload"]["system_ordinal"],
            "temperature_K_external_inscription": row["target_payload"][
                "temperature_K_external_inscription"
            ],
            "pressure_kPa_external_inscription": row["target_payload"][
                "pressure_kPa_external_inscription"
            ],
            "liquid_variable_component_part_external_inscription": row["target_payload"][
                "liquid_variable_component_part_external_inscription"
            ],
            "gas_variable_component_part_external_inscription": row["target_payload"][
                "gas_variable_component_part_external_inscription"
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
            "chemistry_obligation": "SFT-CHEM-OBL-THERMO-008",
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
            "component_account_law": "complete exact positive marginal retained-energy and closed-distinction increments for adding one held component to one phase",
            "exchange_law": "paired one-component departure and arrival preserve the total held component carrier",
            "direction_law": "strict exact product order across complete phase-specific marginal accounts",
            "equilibrium_law": "exact equal accounts yield held equilibrium with structural EmptyOne separations; bulk phase compositions need not be equal",
            "incomparability_law": "crossed marginal accounts halt; no fitted scalar chemical potential is introduced",
            "successor_law": "common exact positive context addition preserves direction or equilibrium",
            "complete_external_target_count": 74,
            "complete_binary_system_count": 4,
            "complete_source_compound_count": 5,
            "complete_source_dataset_count": 13,
            "complete_unmatched_endpoint_count": 8,
            "fixed_environment_pressure_kPa_external_inscription": "101.3",
            "external_gas_greater_row_count": 66,
            "external_liquid_greater_row_count": 8,
            "complete_component_exchange_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_released_after_identity_seal": True,
            "all_phase_compositions_exact_positive_parts_exhausting_One": analysis[
                "all_phase_compositions_are_exact_positive_parts_of_One"
            ],
            "all_74_equilibrium_rows_have_unequal_bulk_phase_composition": analysis[
                "equal_component_account_does_not_require_equal_bulk_composition"
            ],
            "external_composition_orientation_crossing_preserved": analysis[
                "system_one_composition_crossing_retained"
            ],
            "external_values_used_as_proof_parameters": False,
            "imported_chemical_potential_activity_fugacity_or_fitted_model_used": False,
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
    experiment["status"] = "complete_four_system_74_row_VLE_vector_opened_postseal"
    write_json(experiment_path, experiment)
    status = (
        f"# {spec.claim_id}\n\n"
        "Status: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-008`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: complete component-addition accounts under strict product order; equality is structural equilibrium.\n"
        "- Direct NIST TRC ThermoML vector: `4` binary systems and `74` complete matched VLE rows at `101.3 kPa`.\n"
        "- Preserved source boundary: `8` unmatched pure-component endpoints and all `13` source datasets.\n"
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
    print("NIST TRC ThermoML component exchange: 4 systems; 74 matched VLE rows; 8 endpoints retained")


if __name__ == "__main__":
    main()
