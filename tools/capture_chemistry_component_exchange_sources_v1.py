#!/usr/bin/env python3
"""Capture the complete fixed-environment NIST ThermoML VLE surface for THERMO-008."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/component_exchange_capture_spec_v2.json"
SPEC_HASH = "sha256:f6ae8d2c1e45da5b1ff25d19933dbf7f14afb5508ab51bd042807d3635abf864"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-008-component-exchange-v1"
RAW_JSON_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2019-9b00414.json"
LANDING_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2019-9b00414.html"
PRIMARY_PATH = SNAPSHOT_ROOT / "component-exchange-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/component_exchange_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/component_exchange_withheld_targets_v1.json"


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
    request = Request(
        url,
        headers={"User-Agent": "Ernos-Labs-SFT-Empirical-Capture/1.0 (Maria.Smith.Sftoe@gmail.com)"},
    )
    with urlopen(request, timeout=60) as response:
        return response.read()


def _property_group(dataset: dict) -> tuple[str, dict]:
    group = dataset["Property"][0]["Property-MethodID"]["PropertyGroup"]
    names = tuple(name for name in group if name != "tml_elements")
    if len(names) != 1:
        raise ValueError("ThermoML property group is not singular")
    return names[0], group[names[0]]


def _components(dataset: dict) -> tuple[str, ...]:
    return tuple(component["RegNum"]["nOrgNum"] for component in dataset["Component"])


def _variable_component(dataset: dict) -> str:
    variable = dataset["Variable"][0]
    if variable["VariableID"]["VariableType"].get("eComponentComposition") != "Mole fraction":
        raise ValueError("dataset variable is not a component mole fraction")
    if variable["VarPhaseID"].get("eVarPhase") != "Liquid":
        raise ValueError("component variable is not a liquid-phase inscription")
    return variable["VariableID"]["RegNum"]["nOrgNum"]


def _pressure(dataset: dict) -> str:
    constraints = dataset.get("Constraint", ())
    if len(constraints) != 1:
        raise ValueError("equilibrium dataset does not have exactly one fixed environment")
    constraint = constraints[0]
    if constraint["ConstraintID"]["ConstraintType"].get("ePressure") != "Pressure, kPa":
        raise ValueError("held constraint is not pressure")
    return constraint["nConstraintValue"]


def _point_value(point: dict, field: str) -> str:
    values = point[field]
    if len(values) != 1:
        raise ValueError("source point has non-singular value record")
    key = "nVarValue" if field == "VariableValue" else "nPropValue"
    return values[0][key]


def _point_uncertainty(point: dict) -> dict:
    values = point["PropertyValue"]
    return dict(values[0].get("CombinedUncertainty", {}))


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-008 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-component-exchange-prefetch-capture-spec/2"
        or spec.get("all_equilibrium_composition_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
    ):
        raise ValueError("THERMO-008 prefetch boundary is not value-free")

    raw_json = fetch(spec["source"]["json_url"])
    landing = fetch(spec["source"]["landing_url"])
    source = json.loads(raw_json, parse_float=str, parse_int=str)
    if source.get("Citation", {}).get("sDOI") != spec["source"]["doi"]:
        raise ValueError("captured ThermoML DOI changed")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_JSON_PATH.write_bytes(raw_json)
    LANDING_PATH.write_bytes(landing)

    compounds = {row["RegNum"]["nOrgNum"]: row for row in source["Compound"]}
    datasets = {row["nPureOrMixtureDataNumber"]: row for row in source["PureOrMixtureData"]}
    temperature_sets: dict[tuple[str, ...], dict] = {}
    composition_sets: dict[tuple[str, ...], dict] = {}
    pure_or_other_dataset_ordinals: list[str] = []
    for dataset in source["PureOrMixtureData"]:
        group_name, group = _property_group(dataset)
        components = _components(dataset)
        if len(components) != 2:
            pure_or_other_dataset_ordinals.append(dataset["nPureOrMixtureDataNumber"])
            continue
        if (
            group_name == "VaporPBoilingTAzeotropTandP"
            and group.get("ePropName") == "Boiling temperature at pressure P, K"
            and dataset["Property"][0]["PropPhaseID"].get("ePropPhase") == "Liquid"
        ):
            temperature_sets[components] = dataset
        elif (
            group_name == "CompositionAtPhaseEquilibrium"
            and group.get("ePropName") == "Mole fraction"
            and dataset["Property"][0]["PropPhaseID"].get("ePropPhase") == "Gas"
        ):
            composition_sets[components] = dataset
        else:
            pure_or_other_dataset_ordinals.append(dataset["nPureOrMixtureDataNumber"])

    if set(temperature_sets) != set(composition_sets) or len(temperature_sets) != 4:
        raise ValueError("complete fixed-pressure binary VLE system surface changed")

    identities: list[dict] = []
    targets: list[dict] = []
    unmatched: list[dict] = []
    system_summaries: list[dict] = []
    target_ordinal = 1
    for system_ordinal, components in enumerate(temperature_sets, start=1):
        temperature_set = temperature_sets[components]
        composition_set = composition_sets[components]
        if _pressure(temperature_set) != _pressure(composition_set):
            raise ValueError("paired VLE datasets do not share the declared pressure")
        if _variable_component(temperature_set) != _variable_component(composition_set):
            raise ValueError("paired VLE datasets do not share the variable component")
        temperature_points: dict[str, tuple[int, dict]] = {}
        for point_ordinal, point in enumerate(temperature_set["NumValues"], start=1):
            liquid = _point_value(point, "VariableValue")
            if liquid in temperature_points:
                raise ValueError("duplicate liquid composition in temperature dataset")
            temperature_points[liquid] = (point_ordinal, point)
        composition_points: dict[str, tuple[int, dict]] = {}
        for point_ordinal, point in enumerate(composition_set["NumValues"], start=1):
            liquid = _point_value(point, "VariableValue")
            if liquid in composition_points:
                raise ValueError("duplicate liquid composition in gas-composition dataset")
            composition_points[liquid] = (point_ordinal, point)
        common = tuple(value for value in temperature_points if value in composition_points)
        if len(common) != len(composition_points):
            raise ValueError("a measured gas-composition point lacks its temperature record")
        for liquid in temperature_points:
            if liquid not in composition_points:
                point_ordinal, point = temperature_points[liquid]
                unmatched.append(
                    {
                        "system_ordinal": system_ordinal,
                        "temperature_dataset_ordinal": temperature_set["nPureOrMixtureDataNumber"],
                        "temperature_point_ordinal": point_ordinal,
                        "complete_unmatched_point": point,
                        "reason": "source temperature endpoint has no gas-composition companion",
                    }
                )
        variable_component = _variable_component(temperature_set)
        other_components = tuple(component for component in components if component != variable_component)
        if len(other_components) != 1:
            raise ValueError("binary system does not have one complementary component")
        system_summaries.append(
            {
                "system_ordinal": system_ordinal,
                "ordered_component_orgnums": list(components),
                "variable_component_orgnum": variable_component,
                "temperature_dataset_ordinal": temperature_set["nPureOrMixtureDataNumber"],
                "composition_dataset_ordinal": composition_set["nPureOrMixtureDataNumber"],
                "matched_point_count": len(common),
                "unmatched_temperature_point_count": len(temperature_points) - len(common),
            }
        )
        for common_ordinal, liquid in enumerate(common, start=1):
            temperature_point_ordinal, temperature_point = temperature_points[liquid]
            composition_point_ordinal, composition_point = composition_points[liquid]
            target_id = f"SFT-CHEM-THERMO-008-VLE-{target_ordinal:04d}"
            identity = {
                "target_id": target_id,
                "doi": spec["source"]["doi"],
                "source_id": spec["source"]["source_id"],
                "system_ordinal": system_ordinal,
                "temperature_dataset_ordinal": temperature_set["nPureOrMixtureDataNumber"],
                "composition_dataset_ordinal": composition_set["nPureOrMixtureDataNumber"],
                "common_interior_point_ordinal": common_ordinal,
                "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_absent": True,
            }
            liquid_fraction = Fraction(liquid)
            gas = _point_value(composition_point, "PropertyValue")
            gas_fraction = Fraction(gas)
            if not (Fraction(0) < liquid_fraction < Fraction(1)) or not (
                Fraction(0) < gas_fraction < Fraction(1)
            ):
                raise ValueError("multicomponent target row is not interior in both phases")
            target = {
                "target_id": target_id,
                "system_ordinal": system_ordinal,
                "ordered_component_orgnums": list(components),
                "complete_component_records": [compounds[component] for component in components],
                "variable_component_orgnum": variable_component,
                "complementary_component_orgnum": other_components[0],
                "temperature_dataset_ordinal": temperature_set["nPureOrMixtureDataNumber"],
                "temperature_point_ordinal": temperature_point_ordinal,
                "composition_dataset_ordinal": composition_set["nPureOrMixtureDataNumber"],
                "composition_point_ordinal": composition_point_ordinal,
                "pressure_kPa_external_inscription": _pressure(temperature_set),
                "temperature_K_external_inscription": _point_value(temperature_point, "PropertyValue"),
                "liquid_variable_component_part_external_inscription": liquid,
                "liquid_complement_component_part_external_inscription": str(Fraction(1) - liquid_fraction),
                "gas_variable_component_part_external_inscription": gas,
                "gas_complement_component_part_external_inscription": str(Fraction(1) - gas_fraction),
                "complete_temperature_point": temperature_point,
                "complete_gas_composition_point": composition_point,
                "temperature_property_metadata": temperature_set["Property"],
                "gas_composition_property_metadata": composition_set["Property"],
                "temperature_variable_metadata": temperature_set["Variable"],
                "gas_composition_variable_metadata": composition_set["Variable"],
                "temperature_constraint_metadata": temperature_set["Constraint"],
                "gas_composition_constraint_metadata": composition_set["Constraint"],
                "temperature_uncertainty": _point_uncertainty(temperature_point),
                "gas_composition_uncertainty": _point_uncertainty(composition_point),
                "external_phase_classification": "binary-vapor-liquid-equilibrium",
            }
            identities.append(identity)
            targets.append(target)
            target_ordinal += 1

    identity_doc = {
        "schema": "sft-v3-component-exchange-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "all_compound_temperature_pressure_composition_equilibrium_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-component-exchange-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary_doc = {
        "schema": "sft-v3-component-exchange-primary-records/1",
        "prefetch_capture_spec_hash_before_http_fetch": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": spec["source"]["source_id"],
        "doi": spec["source"]["doi"],
        "landing_url": spec["source"]["landing_url"],
        "json_url": spec["source"]["json_url"],
        "raw_json_snapshot_path": str(RAW_JSON_PATH.relative_to(ROOT)),
        "raw_json_snapshot_hash": sha_file(RAW_JSON_PATH),
        "landing_snapshot_path": str(LANDING_PATH.relative_to(ROOT)),
        "landing_snapshot_hash": sha_file(LANDING_PATH),
        "complete_source_compound_count": len(source["Compound"]),
        "complete_source_dataset_count": len(source["PureOrMixtureData"]),
        "complete_binary_system_count": len(system_summaries),
        "complete_matched_multicomponent_target_count": len(targets),
        "complete_unmatched_temperature_endpoint_count": len(unmatched),
        "pure_or_other_dataset_ordinals": pure_or_other_dataset_ordinals,
        "system_summaries": system_summaries,
        "unmatched_temperature_endpoints": unmatched,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_equilibrium_rows_and_unpaired_source_endpoints_preserved": True,
        "correlated_regressed_or_model_calculated_values_used_as_measurements": False,
        "external_values_used_as_proof_parameters": False,
        "external_zero_negative_or_decimal_glyphs_are_source_inscriptions_not_SFT_proof_values": True,
    }
    write_json(PRIMARY_PATH, primary_doc)
    print(
        json.dumps(
            {
                "prefetch_spec_hash": SPEC_HASH,
                "raw_json_hash": sha_file(RAW_JSON_PATH),
                "landing_hash": sha_file(LANDING_PATH),
                "binary_systems": len(system_summaries),
                "matched_targets": len(targets),
                "unmatched_temperature_endpoints": len(unmatched),
                "identity_hash": identity_hash,
                "target_hash": sha_file(TARGET_PATH),
                "primary_hash": sha_file(PRIMARY_PATH),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
