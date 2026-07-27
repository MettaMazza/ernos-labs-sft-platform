#!/usr/bin/env python3
"""Officially admit and materialize Chemistry THERMO-013 exactly once."""

from __future__ import annotations

from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.multicomponent_phase_diagram_batch_v1 import MULTICOMPONENT_PHASE_DIAGRAM_SPEC  # noqa: E402
from sft.chemistry.multicomponent_phase_diagram_validation_v1 import _source_rows, exact_multicomponent_analysis  # noqa: E402
from sft.engine import EngineRepository  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_execution():
    path = ROOT / "claims" / MULTICOMPONENT_PHASE_DIAGRAM_SPEC.claim_id / "execution.py"
    definition = importlib.util.spec_from_file_location("sft_chemistry_thermo_013", path)
    if definition is None or definition.loader is None:
        raise RuntimeError("cannot load THERMO-013 execution package")
    module = importlib.util.module_from_spec(definition)
    definition.loader.exec_module(module)
    return module.build_execution(ROOT)


def compact_external_row(row: dict) -> dict:
    target = row["target_payload"]
    result = {
        "target_id": row["target_id"],
        "dataset_class": target["dataset_class"],
        "dataset_ordinals": target["dataset_ordinals"],
        "source_point_ordinal": target["source_point_ordinal"],
        "component_orgnums": target["component_orgnums"],
        "temperature_K_external_inscription": target["temperature_K_external_inscription"],
        "pressure_kPa_external_inscription": target["pressure_kPa_external_inscription"],
        "complete_target_payload_hash": row["target_payload_hash"],
    }
    if target["dataset_class"] == "binary":
        result.update({
            "liquid_reported_mole_fraction_external_inscription": target["liquid_reported_mole_fraction_external_inscription"],
            "gas_reported_mole_fraction_external_inscription": target["gas_reported_mole_fraction_external_inscription"],
            "azeotropic_by_exact_source_method": target["azeotropic_by_exact_source_method"],
        })
    else:
        result.update({
            "liquid_component_1_mole_fraction_external_inscription": target["liquid_component_1_mole_fraction_external_inscription"],
            "liquid_component_2_mole_fraction_external_inscription": target["liquid_component_2_mole_fraction_external_inscription"],
            "gas_component_1_mole_fraction_external_inscription": target["gas_component_1_mole_fraction_external_inscription"],
            "gas_component_2_mole_fraction_external_inscription": target["gas_component_2_mole_fraction_external_inscription"],
        })
    return result


def main() -> None:
    spec = MULTICOMPONENT_PHASE_DIAGRAM_SPEC
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
    primary = json.loads((ROOT / "experiments/external_sources/chemistry/snapshots/thermo-013-multicomponent-phase-diagram-v1/multicomponent-phase-diagram-primary-records-v1.json").read_text())
    analysis = exact_multicomponent_analysis(rows, primary)
    vector = tuple(compact_external_row(row) for row in rows)
    payloads = {
        "candidate_census.json": {"claim_id": spec.claim_id, **asdict(sealed.census)},
        "elimination_receipt.json": {"claim_id": spec.claim_id, "decisions": asdict(sealed)["decisions"], "closure": asdict(sealed.closure)},
        "controls.json": {"claim_id": spec.claim_id, "controls": asdict(sealed)["controls"]},
        "empirical_validation.json": {"claim_id": spec.claim_id, **asdict(empirical)},
        "certificate.json": {
            "claim_id": spec.claim_id,
            "chemistry_obligation": "SFT-CHEM-OBL-THERMO-013",
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
            "composition_law": "each held phase retains every component coordinate and closes exactly to the One",
            "coexistence_law": "two distinct held phase words preserve componentwise exact exchange-support balance",
            "phase_rule_law": "two-phase degree support is the exact component-count carrier word",
            "absence_law": "all exact absent phase coordinates are structural EmptyOne; source zero glyphs remain provenance only",
            "finite_diagram_law": "complete source-ordered word of binary and ternary coexistence records without interpolation",
            "successor_law": "complete point append and common component-exchange replication preserve the law at every finite depth",
            "complete_external_target_count": 116,
            "complete_binary_target_count": 65,
            "complete_ternary_target_count": 51,
            "complete_composition_coordinate_count": 566,
            "structural_EmptyOne_coordinate_count": 12,
            "complete_binary_dataset_pair_count": 5,
            "complete_companion_pure_dataset_count": 6,
            "complete_parent_dataset_count": 17,
            "complete_parent_point_count": 187,
            "minimum_temperature_K_external_inscription": analysis["minimum_temperature_K"],
            "maximum_temperature_K_external_inscription": analysis["maximum_temperature_K"],
            "pressure_kPa_external_inscription": analysis["minimum_pressure_kPa"],
            "complete_binary_and_ternary_coexistence_vector": vector,
            "all_external_rows_preserved": empirical.all_rows_preserved,
            "external_data_source_ids": list(empirical.data_source_ids),
            "all_compound_phase_temperature_pressure_composition_uncertainty_values_released_after_identity_seal": True,
            "lever_rule_tie_line_gibbs_triangle_convex_hull_eos_continuum_interpolation_regression_or_fit_used": False,
            "external_values_used_as_proof_parameters": False,
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
    experiment["status"] = "complete_65_binary_51_ternary_116_record_vector_opened_postseal"
    write_json(experiment_path, experiment)
    (package / "STATUS.md").write_text(
        f"# {spec.claim_id}\n\nStatus: `model_admitted_observationally_derived_empirically_tested_and_independently_replicated`\n\n"
        "- Chemistry obligation: `SFT-CHEM-OBL-THERMO-013`\n"
        f"- Closure: `{receipt.closure_status}`\n"
        "- Exact law: complete binary/ternary phase words closing to the One with componentwise exchange balance and exact phase-rule rank.\n"
        "- Complete NIST surface: `65` binary plus `51` ternary records; `566` phase coordinates; `12` EmptyOne boundaries.\n"
        f"- Derivation seal: `{sealed.seal_hash}`\n- Independent validation: `{receipt.external_validation_hash}`\n"
        f"- Empirical validation: `{receipt.empirical_validation_hash}`\n- Engine receipt: `{receipt.receipt_hash}`\n",
        encoding="utf-8",
    )
    print(f"admitted {spec.claim_id}: {receipt.receipt_hash}")
    print(f"derivation seal: {sealed.seal_hash}")
    print(f"candidates: {len(sealed.census.candidates)}; survivors: {sum(decision.survives for decision in sealed.decisions)}")
    print("NIST multicomponent coexistence: 65 binary; 51 ternary; 116 complete records")


if __name__ == "__main__":
    main()
