#!/usr/bin/env python3
"""Capture the complete binary/ternary coexistence surface for THERMO-013."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/multicomponent_phase_diagram_capture_spec_v1.json"
SPEC_HASH = "sha256:d020adceefee9226b8424e92e732e3161623044fab299a4987f7bae5575fe8ad"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-013-multicomponent-phase-diagram-v1"
RAW_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jct-2012-47-260-266.json"
LANDING_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jct-2012-47-260-266.html"
PRIMARY_PATH = SNAPSHOT_ROOT / "multicomponent-phase-diagram-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/multicomponent_phase_diagram_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/multicomponent_phase_diagram_withheld_targets_v1.json"
BINARY_PAIRS = ((7, 8), (9, 10), (11, 12), (13, 14), (15, 16))


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        return response.read()


def numbered(rows: list[dict], field: str) -> dict[int, dict]:
    return {int(row[field]): row for row in rows}


def pressure_constraint(dataset: dict) -> tuple[str, dict]:
    constraints = dataset.get("Constraint", ())
    if len(constraints) != 1 or constraints[0]["ConstraintID"]["ConstraintType"].get("ePressure") != "Pressure, kPa":
        raise ValueError("THERMO-013 fixed-pressure dataset changed")
    return constraints[0]["nConstraintValue"], constraints[0]


def ensure_direct(dataset: dict) -> None:
    if any(row.get("ePresentation") != "Direct value, X" for row in dataset.get("Property", ())):
        raise ValueError("THERMO-013 encountered a non-direct property")


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-013 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-multicomponent-phase-diagram-prefetch-capture-spec/1"
        or spec.get("all_compound_component_count_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
    ):
        raise ValueError("THERMO-013 prefetch boundary is not value-free")

    raw = fetch(spec["source"]["json_url"])
    landing = fetch(spec["source"]["landing_url"])
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    LANDING_PATH.write_bytes(landing)
    source = json.loads(raw.decode("utf-8"), parse_float=str, parse_int=str)
    compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
    datasets = {int(row["nPureOrMixtureDataNumber"]): row for row in source["PureOrMixtureData"]}
    if len(compounds) != 3 or len(datasets) != 17 or sum(len(row["NumValues"]) for row in datasets.values()) != 187:
        raise ValueError("THERMO-013 complete source census changed")

    identities: list[dict] = []
    targets: list[dict] = []
    summaries: list[dict] = []
    ordinal = 1
    for temperature_dataset_number, composition_dataset_number in BINARY_PAIRS:
        temperature_dataset = datasets[temperature_dataset_number]
        composition_dataset = datasets[composition_dataset_number]
        ensure_direct(temperature_dataset)
        ensure_direct(composition_dataset)
        components = tuple(int(row["RegNum"]["nOrgNum"]) for row in temperature_dataset["Component"])
        paired_components = tuple(int(row["RegNum"]["nOrgNum"]) for row in composition_dataset["Component"])
        temperature_points = temperature_dataset["NumValues"]
        composition_points = composition_dataset["NumValues"]
        if components != paired_components or len(components) != 2 or len(temperature_points) != len(composition_points):
            raise ValueError("THERMO-013 binary dataset pairing changed")
        pair_target_ids = []
        azeotrope = temperature_dataset_number in (7, 11)
        for point_ordinal, (temperature_point, composition_point) in enumerate(zip(temperature_points, composition_points), start=1):
            temperature_variables = numbered(temperature_point["VariableValue"], "nVarNumber")
            composition_variables = numbered(composition_point["VariableValue"], "nVarNumber")
            temperature_properties = numbered(temperature_point["PropertyValue"], "nPropNumber")
            composition_properties = numbered(composition_point["PropertyValue"], "nPropNumber")
            if azeotrope:
                pressure = temperature_variables[1]["nVarValue"]
                if pressure != composition_variables[1]["nVarValue"]:
                    raise ValueError("THERMO-013 azeotrope pressure pairing changed")
                temperature = temperature_properties[1]["nPropValue"]
                liquid_fraction = composition_properties[1]["nPropValue"]
                gas_fraction = liquid_fraction
                pressure_record = temperature_variables[1]
                liquid_record = composition_properties[1]
                gas_record = composition_properties[1]
                pressure_metadata = temperature_dataset["Variable"]
            else:
                pressure, pressure_record = pressure_constraint(temperature_dataset)
                paired_pressure, _ = pressure_constraint(composition_dataset)
                if pressure != paired_pressure or temperature_variables[1]["nVarValue"] != composition_variables[1]["nVarValue"]:
                    raise ValueError("THERMO-013 binary coordinate pairing changed")
                temperature = temperature_properties[1]["nPropValue"]
                liquid_fraction = temperature_variables[1]["nVarValue"]
                gas_fraction = composition_properties[1]["nPropValue"]
                liquid_record = temperature_variables[1]
                gas_record = composition_properties[1]
                pressure_metadata = temperature_dataset["Constraint"]
            target_id = f"SFT-CHEM-THERMO-013-BINARY-{ordinal:03d}"
            identity = {
                "target_id": target_id,
                "doi": spec["source"]["doi"],
                "source_id": spec["source"]["source_id"],
                "dataset_class": "binary",
                "dataset_ordinals": [temperature_dataset_number, composition_dataset_number],
                "source_point_ordinal": point_ordinal,
                "all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent": True,
            }
            target = {
                "target_id": target_id,
                "dataset_class": "binary",
                "dataset_ordinals": [temperature_dataset_number, composition_dataset_number],
                "source_point_ordinal": point_ordinal,
                "component_orgnums": list(components),
                "complete_component_records": [compounds[number] for number in components],
                "phase_ids": temperature_dataset["PhaseID"],
                "pressure_kPa_external_inscription": pressure,
                "temperature_K_external_inscription": temperature,
                "liquid_reported_component_orgnum": components[0],
                "liquid_reported_mole_fraction_external_inscription": liquid_fraction,
                "gas_reported_component_orgnum": components[0],
                "gas_reported_mole_fraction_external_inscription": gas_fraction,
                "azeotropic_by_exact_source_method": azeotrope,
                "complete_pressure_record": pressure_record,
                "complete_temperature_record": temperature_properties[1],
                "complete_liquid_composition_record": liquid_record,
                "complete_gas_composition_record": gas_record,
                "complete_pressure_metadata": pressure_metadata,
                "complete_temperature_dataset_metadata": {key: value for key, value in temperature_dataset.items() if key != "NumValues"},
                "complete_composition_dataset_metadata": {key: value for key, value in composition_dataset.items() if key != "NumValues"},
                "complete_temperature_point_record": temperature_point,
                "complete_composition_point_record": composition_point,
                "coexistence_class": "binary-liquid-gas",
            }
            identities.append(identity)
            targets.append(target)
            pair_target_ids.append(target_id)
            ordinal += 1
        summaries.append({
            "dataset_class": "binary",
            "dataset_ordinals": [temperature_dataset_number, composition_dataset_number],
            "component_orgnums": list(components),
            "point_count": len(pair_target_ids),
            "target_ids_in_source_order": pair_target_ids,
        })

    ternary_dataset = datasets[17]
    ensure_direct(ternary_dataset)
    ternary_components = tuple(int(row["RegNum"]["nOrgNum"]) for row in ternary_dataset["Component"])
    ternary_pressure, ternary_pressure_record = pressure_constraint(ternary_dataset)
    if ternary_components != (1, 2, 3) or len(ternary_dataset["NumValues"]) != 51:
        raise ValueError("THERMO-013 ternary surface changed")
    ternary_target_ids = []
    for point_ordinal, point in enumerate(ternary_dataset["NumValues"], start=1):
        variables = numbered(point["VariableValue"], "nVarNumber")
        properties = numbered(point["PropertyValue"], "nPropNumber")
        if set(variables) != {1, 2} or set(properties) != {1, 2, 3}:
            raise ValueError("THERMO-013 ternary record is incomplete")
        target_id = f"SFT-CHEM-THERMO-013-TERNARY-{ordinal:03d}"
        identity = {
            "target_id": target_id,
            "doi": spec["source"]["doi"],
            "source_id": spec["source"]["source_id"],
            "dataset_class": "ternary",
            "dataset_ordinals": [17],
            "source_point_ordinal": point_ordinal,
            "all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent": True,
        }
        target = {
            "target_id": target_id,
            "dataset_class": "ternary",
            "dataset_ordinals": [17],
            "source_point_ordinal": point_ordinal,
            "component_orgnums": list(ternary_components),
            "complete_component_records": [compounds[number] for number in ternary_components],
            "phase_ids": ternary_dataset["PhaseID"],
            "pressure_kPa_external_inscription": ternary_pressure,
            "temperature_K_external_inscription": variables[1]["nVarValue"],
            "liquid_component_1_mole_fraction_external_inscription": variables[2]["nVarValue"],
            "liquid_component_2_mole_fraction_external_inscription": properties[1]["nPropValue"],
            "gas_component_1_mole_fraction_external_inscription": properties[3]["nPropValue"],
            "gas_component_2_mole_fraction_external_inscription": properties[2]["nPropValue"],
            "complete_pressure_record": ternary_pressure_record,
            "complete_point_record": point,
            "complete_dataset_metadata": {key: value for key, value in ternary_dataset.items() if key != "NumValues"},
            "coexistence_class": "ternary-liquid-gas",
        }
        identities.append(identity)
        targets.append(target)
        ternary_target_ids.append(target_id)
        ordinal += 1
    summaries.append({
        "dataset_class": "ternary",
        "dataset_ordinals": [17],
        "component_orgnums": list(ternary_components),
        "point_count": len(ternary_target_ids),
        "target_ids_in_source_order": ternary_target_ids,
    })

    if len(identities) != 116 or len(targets) != 116:
        raise ValueError("THERMO-013 complete coexistence target census changed")
    identity_doc = {
        "schema": "sft-v3-multicomponent-phase-diagram-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "binary_target_count": 65,
        "ternary_target_count": 51,
        "all_compound_phase_temperature_pressure_composition_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-multicomponent-phase-diagram-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "binary_target_count": 65,
        "ternary_target_count": 51,
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-multicomponent-phase-diagram-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": spec["source"]["source_id"],
        "doi": spec["source"]["doi"],
        "raw_source_path": str(RAW_PATH.relative_to(ROOT)),
        "raw_source_hash": sha_file(RAW_PATH),
        "landing_path": str(LANDING_PATH.relative_to(ROOT)),
        "landing_hash": sha_file(LANDING_PATH),
        "complete_source_compound_count": len(compounds),
        "complete_source_dataset_count": len(datasets),
        "complete_source_point_count": sum(len(row["NumValues"]) for row in datasets.values()),
        "complete_companion_pure_dataset_count": 6,
        "complete_binary_dataset_count": 10,
        "complete_binary_pair_count": len(BINARY_PAIRS),
        "complete_binary_coexistence_point_count": 65,
        "complete_ternary_dataset_count": 1,
        "complete_ternary_coexistence_point_count": 51,
        "complete_coexistence_target_count": len(targets),
        "dataset_summaries": summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_binary_and_ternary_points_and_complete_source_preserved": True,
        "lever_rule_tie_line_equation_gibbs_triangle_convex_hull_eos_continuum_interpolation_regression_or_fit_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "raw_hash": sha_file(RAW_PATH),
        "landing_hash": sha_file(LANDING_PATH),
        "binary_target_count": 65,
        "ternary_target_count": 51,
        "complete_target_count": len(targets),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
