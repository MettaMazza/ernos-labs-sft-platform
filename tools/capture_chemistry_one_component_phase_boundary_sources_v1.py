#!/usr/bin/env python3
"""Capture the complete one-component coexistence-pressure surface for THERMO-012."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/one_component_phase_boundary_capture_spec_v1.json"
SPEC_HASH = "sha256:4db9cc027e04d154d05e1996cc5ed05bd27b9a9a300f5db98c1fca2ec6cfbfc3"
RAW_PATH = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1/nist-trc-thermoml-fpe-2019-485-145-152.json"
RAW_HASH = "sha256:fdaaa9d89f1a324610ae9c5d77b4b129207b6a291e586c3bc3c42c17043724dc"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-012-one-component-phase-boundary-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "one-component-phase-boundary-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/one_component_phase_boundary_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/one_component_phase_boundary_withheld_targets_v1.json"


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def property_group(dataset: dict) -> tuple[str, dict]:
    group = dataset["Property"][0]["Property-MethodID"]["PropertyGroup"]
    names = tuple(name for name in group if name != "tml_elements")
    if len(names) != 1:
        raise ValueError("ThermoML property group is not singular")
    return names[0], group[names[0]]


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-012 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-one-component-phase-boundary-prefetch-capture-spec/1"
        or spec.get("all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("parent_source", {}).get("sha256") != RAW_HASH
    ):
        raise ValueError("THERMO-012 prefetch boundary is not value-free")
    if sha_file(RAW_PATH) != RAW_HASH:
        raise ValueError("THERMO-012 parent source changed")
    source = json.loads(RAW_PATH.read_text(), parse_float=str, parse_int=str)
    compounds = {row["RegNum"]["nOrgNum"]: row for row in source["Compound"]}
    datasets = []
    for dataset in source["PureOrMixtureData"]:
        group_name, group = property_group(dataset)
        if (
            len(dataset["Component"]) == 1
            and group_name == "VaporPBoilingTAzeotropTandP"
            and group.get("ePropName") == "Vapor or sublimation pressure, kPa"
            and dataset["Property"][0].get("ePresentation") == "Direct value, X"
        ):
            datasets.append(dataset)
    if len(datasets) != 3 or sum(len(row["NumValues"]) for row in datasets) != 15:
        raise ValueError("THERMO-012 complete direct one-component surface changed")
    identities = []
    targets = []
    summaries = []
    target_ordinal = 1
    for dataset in datasets:
        component = dataset["Component"][0]["RegNum"]["nOrgNum"]
        variables = dataset.get("Variable", ())
        if (
            len(variables) != 1
            or variables[0]["VariableID"]["VariableType"].get("eTemperature") != "Temperature, K"
        ):
            raise ValueError("THERMO-012 coexistence coordinate is not direct temperature")
        dataset_rows = []
        for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
            variable_values = point.get("VariableValue", ())
            property_values = point.get("PropertyValue", ())
            if len(variable_values) != 1 or len(property_values) != 1:
                raise ValueError("THERMO-012 point is incomplete")
            temperature = variable_values[0]["nVarValue"]
            pressure = property_values[0]["nPropValue"]
            target_id = f"SFT-CHEM-THERMO-012-COEXISTENCE-{target_ordinal:03d}"
            identities.append({
                "target_id": target_id,
                "doi": spec["parent_source"]["doi"],
                "source_id": spec["parent_source"]["source_id"],
                "dataset_ordinal": dataset["nPureOrMixtureDataNumber"],
                "source_point_ordinal": point_ordinal,
                "all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent": True,
            })
            target = {
                "target_id": target_id,
                "component_orgnum": component,
                "complete_component_record": compounds[component],
                "dataset_ordinal": dataset["nPureOrMixtureDataNumber"],
                "source_point_ordinal": point_ordinal,
                "temperature_K_external_inscription": temperature,
                "pressure_kPa_external_inscription": pressure,
                "complete_temperature_record": variable_values[0],
                "complete_pressure_record": property_values[0],
                "complete_variable_metadata": dataset["Variable"],
                "complete_property_metadata": dataset["Property"],
                "pressure_uncertainty": property_values[0].get("CombinedUncertainty", {}),
                "phase_boundary_class": "one-component-liquid-vapor-coexistence",
            }
            targets.append(target)
            dataset_rows.append(target_id)
            target_ordinal += 1
        summaries.append({
            "dataset_ordinal": dataset["nPureOrMixtureDataNumber"],
            "component_orgnum": component,
            "point_count": len(dataset_rows),
            "target_ids_in_source_order": dataset_rows,
        })
    identity_doc = {
        "schema": "sft-v3-one-component-phase-boundary-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "all_compound_temperature_pressure_phase_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-one-component-phase-boundary-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-one-component-phase-boundary-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": spec["parent_source"]["source_id"],
        "doi": spec["parent_source"]["doi"],
        "parent_raw_source_path": str(RAW_PATH.relative_to(ROOT)),
        "parent_raw_source_hash": RAW_HASH,
        "complete_parent_compound_count": len(source["Compound"]),
        "complete_parent_dataset_count": len(source["PureOrMixtureData"]),
        "complete_parent_point_count": sum(len(row["NumValues"]) for row in source["PureOrMixtureData"]),
        "complete_direct_one_component_dataset_count": len(datasets),
        "complete_direct_one_component_point_count": len(targets),
        "complete_distinct_one_component_count": len({row["component_orgnum"] for row in targets}),
        "dataset_summaries": summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_one_component_points_and_complete_parent_source_preserved": True,
        "clausius_clapeyron_eos_interpolation_regression_or_model_value_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "parent_raw_hash": RAW_HASH,
        "direct_dataset_count": len(datasets),
        "direct_point_count": len(targets),
        "distinct_component_count": len({row["component_orgnum"] for row in targets}),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
