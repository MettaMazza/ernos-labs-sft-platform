#!/usr/bin/env python3
"""Capture the complete NIST ThermoML real-gas equilibrium surface for THERMO-010."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/real_gas_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:9935f5e2e67e62329bb976c7f22e196b9f3e48d61c6c9681ebf8b539eb0bb66e"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-010-real-gas-equilibrium-v1"
RAW_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-fpe-2019-485-145-152.json"
LANDING_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-fpe-2019-485-145-152.html"
PRIMARY_PATH = SNAPSHOT_ROOT / "real-gas-equilibrium-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/real_gas_equilibrium_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/real_gas_equilibrium_withheld_targets_v1.json"


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


def property_group(dataset: dict) -> tuple[str, dict]:
    group = dataset["Property"][0]["Property-MethodID"]["PropertyGroup"]
    names = tuple(name for name in group if name != "tml_elements")
    if len(names) != 1:
        raise ValueError("ThermoML property group is not singular")
    return names[0], group[names[0]]


def component_tuple(dataset: dict) -> tuple[str, ...]:
    return tuple(row["RegNum"]["nOrgNum"] for row in dataset["Component"])


def variable_semantics(dataset: dict) -> dict[str, tuple[str, str | None]]:
    result = {}
    for variable in dataset.get("Variable", ()):
        variable_number = variable["nVarNumber"]
        variable_type = variable["VariableID"]["VariableType"]
        names = tuple(name for name in variable_type if name != "tml_elements")
        if len(names) != 1:
            raise ValueError("ThermoML variable type is not singular")
        name = names[0]
        component = variable["VariableID"].get("RegNum", {}).get("nOrgNum")
        if name == "eTemperature":
            semantic = "temperature_K"
        elif name == "eComponentComposition" and variable_type[name] == "Mole fraction" and component:
            semantic = f"liquid_mole_fraction_component_{component}"
        else:
            raise ValueError("unregistered real-gas equilibrium variable")
        result[variable_number] = (semantic, component)
    return result


def point_coordinates(dataset: dict, point: dict) -> dict[str, dict]:
    semantics = variable_semantics(dataset)
    values = {row["nVarNumber"]: row for row in point["VariableValue"]}
    if set(semantics) != set(values):
        raise ValueError("real-gas point does not preserve every variable")
    result = {}
    for number, (semantic, component) in semantics.items():
        result[semantic] = {
            "external_inscription": values[number]["nVarValue"],
            "component_orgnum": component,
            "complete_variable_value": values[number],
        }
    for constraint in dataset.get("Constraint", ()):
        constraint_type = constraint["ConstraintID"]["ConstraintType"]
        if constraint_type.get("eTemperature") == "Temperature, K":
            result["temperature_K"] = {
                "external_inscription": constraint["nConstraintValue"],
                "component_orgnum": None,
                "complete_constraint": constraint,
            }
        else:
            raise ValueError("unregistered real-gas equilibrium constraint")
    return result


def coordinate_key(coordinates: dict[str, dict]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((name, row["external_inscription"]) for name, row in coordinates.items()))


def property_value(point: dict) -> tuple[str, dict]:
    values = point["PropertyValue"]
    if len(values) != 1:
        raise ValueError("real-gas source point has non-singular property")
    return values[0]["nPropValue"], values[0]


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-010 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-real-gas-equilibrium-prefetch-capture-spec/1"
        or spec.get("all_compound_temperature_pressure_composition_phase_equilibrium_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
    ):
        raise ValueError("THERMO-010 prefetch boundary is not value-free")
    raw = fetch(spec["source"]["json_url"])
    landing = fetch(spec["source"]["landing_url"])
    source = json.loads(raw, parse_float=str, parse_int=str)
    if source.get("Citation", {}).get("sDOI") != spec["source"]["doi"]:
        raise ValueError("captured ThermoML DOI changed")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    LANDING_PATH.write_bytes(landing)
    compounds = {row["RegNum"]["nOrgNum"]: row for row in source["Compound"]}
    pressure_sets = []
    composition_sets = []
    companion_dataset_ordinals = []
    for dataset in source["PureOrMixtureData"]:
        group_name, group = property_group(dataset)
        components = component_tuple(dataset)
        if len(components) == 2 and group_name == "VaporPBoilingTAzeotropTandP" and group.get("ePropName") == "Vapor or sublimation pressure, kPa":
            pressure_sets.append(dataset)
        elif len(components) == 2 and group_name == "CompositionAtPhaseEquilibrium" and group.get("ePropName") == "Mole fraction" and dataset["Property"][0].get("PropPhaseID", {}).get("ePropPhase") == "Gas":
            composition_sets.append(dataset)
        else:
            companion_dataset_ordinals.append(dataset["nPureOrMixtureDataNumber"])
    if len(pressure_sets) != 7 or len(composition_sets) != 3:
        raise ValueError("THERMO-010 equilibrium dataset surface changed")
    composition_indexes = {}
    for dataset in composition_sets:
        rows = {}
        for ordinal, point in enumerate(dataset["NumValues"], start=1):
            key = coordinate_key(point_coordinates(dataset, point))
            if key in rows:
                raise ValueError("duplicate composition-state coordinate")
            rows[key] = (ordinal, point)
        composition_indexes[dataset["nPureOrMixtureDataNumber"]] = rows
    identities = []
    targets = []
    dataset_summaries = []
    target_ordinal = 1
    absent_coordinate_count = 0
    matched_count = 0
    unmatched_count = 0
    used_composition_datasets = set()
    for pressure_set in pressure_sets:
        pressure_rows = []
        for ordinal, point in enumerate(pressure_set["NumValues"], start=1):
            coordinates = point_coordinates(pressure_set, point)
            key = coordinate_key(coordinates)
            pressure_rows.append((ordinal, point, coordinates, key))
        candidates = []
        for composition_set in composition_sets:
            if component_tuple(composition_set) != component_tuple(pressure_set):
                continue
            index = composition_indexes[composition_set["nPureOrMixtureDataNumber"]]
            if set(row[3] for row in pressure_rows) == set(index):
                candidates.append(composition_set)
        if len(candidates) > 1:
            raise ValueError("pressure dataset has multiple composition companions")
        composition_set = candidates[0] if candidates else None
        if composition_set is not None:
            used_composition_datasets.add(composition_set["nPureOrMixtureDataNumber"])
        dataset_matched = 0
        for point_ordinal, pressure_point, coordinates, key in pressure_rows:
            pressure_inscription, pressure_value_record = property_value(pressure_point)
            pressure = Fraction(pressure_inscription)
            if pressure.numerator <= 0:
                raise ValueError("real-gas equilibrium pressure is not exact positive")
            gas_composition = None
            composition_point_ordinal = None
            complete_composition_point = None
            composition_property_metadata = None
            if composition_set is not None:
                composition_point_ordinal, complete_composition_point = composition_indexes[
                    composition_set["nPureOrMixtureDataNumber"]
                ][key]
                gas_composition, gas_property_record = property_value(complete_composition_point)
                gas_fraction = Fraction(gas_composition)
                if gas_fraction.numerator < 0 or gas_fraction > 1:
                    raise ValueError("gas composition is outside the external phase part boundary")
                composition_property_metadata = composition_set["Property"]
                dataset_matched += 1
                matched_count += 1
            else:
                gas_property_record = None
                unmatched_count += 1
            interface_coordinates = []
            for name, coordinate in sorted(coordinates.items()):
                inscription = coordinate["external_inscription"]
                is_composition = name.startswith("liquid_mole_fraction_component_")
                is_absence = is_composition and Fraction(inscription).numerator == 0
                if is_absence:
                    absent_coordinate_count += 1
                interface_coordinates.append(
                    {
                        "coordinate_name": name,
                        "component_orgnum": coordinate["component_orgnum"],
                        "external_inscription": inscription,
                        "sft_interface_state": "EmptyOne" if is_absence else "exact-positive-coordinate",
                        "complete_source_coordinate": coordinate,
                    }
                )
            target_id = f"SFT-CHEM-THERMO-010-REAL-GAS-{target_ordinal:04d}"
            identity = {
                "target_id": target_id,
                "doi": spec["source"]["doi"],
                "source_id": spec["source"]["source_id"],
                "pressure_dataset_ordinal": pressure_set["nPureOrMixtureDataNumber"],
                "pressure_point_ordinal": point_ordinal,
                "composition_companion_class": "present" if composition_set is not None else "EmptyOne",
                "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_absent": True,
            }
            target = {
                "target_id": target_id,
                "ordered_component_orgnums": list(component_tuple(pressure_set)),
                "complete_component_records": [compounds[number] for number in component_tuple(pressure_set)],
                "pressure_dataset_ordinal": pressure_set["nPureOrMixtureDataNumber"],
                "pressure_point_ordinal": point_ordinal,
                "composition_dataset_ordinal": composition_set["nPureOrMixtureDataNumber"] if composition_set is not None else None,
                "composition_point_ordinal": composition_point_ordinal,
                "pressure_kPa_external_inscription": pressure_inscription,
                "gas_component_mole_fraction_external_inscription": gas_composition,
                "gas_composition_interface_state": "exact-phase-part" if gas_composition is not None and Fraction(gas_composition).numerator > 0 else "EmptyOne" if gas_composition is not None else "unreported",
                "condition_and_liquid_composition_coordinates": interface_coordinates,
                "complete_pressure_point": pressure_point,
                "complete_gas_composition_point": complete_composition_point,
                "complete_pressure_property_metadata": pressure_set["Property"],
                "complete_composition_property_metadata": composition_property_metadata,
                "pressure_uncertainty": dict(pressure_value_record.get("CombinedUncertainty", {})),
                "gas_composition_uncertainty": dict(gas_property_record.get("CombinedUncertainty", {})) if gas_property_record else None,
                "external_phase_classification": "binary-real-gas-vapor-liquid-equilibrium",
            }
            identities.append(identity)
            targets.append(target)
            target_ordinal += 1
        dataset_summaries.append(
            {
                "pressure_dataset_ordinal": pressure_set["nPureOrMixtureDataNumber"],
                "ordered_component_orgnums": list(component_tuple(pressure_set)),
                "pressure_point_count": len(pressure_rows),
                "composition_companion_dataset_ordinal": composition_set["nPureOrMixtureDataNumber"] if composition_set is not None else None,
                "matched_composition_point_count": dataset_matched,
            }
        )
    if used_composition_datasets != set(composition_indexes):
        raise ValueError("a direct gas-composition dataset was not retained")
    if len(targets) != 94 or matched_count != 59 or unmatched_count != 35:
        raise ValueError("THERMO-010 complete equilibrium state surface changed")
    identity_doc = {
        "schema": "sft-v3-real-gas-equilibrium-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "all_compound_temperature_pressure_composition_phase_equilibrium_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-real-gas-equilibrium-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-real-gas-equilibrium-primary-records/1",
        "prefetch_capture_spec_hash_before_http_fetch": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": spec["source"]["source_id"],
        "doi": spec["source"]["doi"],
        "raw_json_snapshot_path": str(RAW_PATH.relative_to(ROOT)),
        "raw_json_snapshot_hash": sha_file(RAW_PATH),
        "landing_snapshot_path": str(LANDING_PATH.relative_to(ROOT)),
        "landing_snapshot_hash": sha_file(LANDING_PATH),
        "complete_compound_count": len(compounds),
        "complete_source_dataset_count": len(source["PureOrMixtureData"]),
        "complete_source_point_count": sum(len(row["NumValues"]) for row in source["PureOrMixtureData"]),
        "complete_equilibrium_pressure_dataset_count": len(pressure_sets),
        "complete_gas_composition_dataset_count": len(composition_sets),
        "complete_equilibrium_state_count": len(targets),
        "matched_gas_composition_state_count": matched_count,
        "pressure_only_equilibrium_state_count": unmatched_count,
        "external_absence_glyph_coordinate_count": absent_coordinate_count,
        "companion_dataset_ordinals": companion_dataset_ordinals,
        "dataset_summaries": dataset_summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_equilibrium_states_and_complete_raw_source_preserved": True,
        "correlated_regressed_or_model_calculated_values_used_as_measurements": False,
        "equation_of_state_fugacity_or_compressibility_fit_imported": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(
        json.dumps(
            {
                "prefetch_spec_hash": SPEC_HASH,
                "raw_hash": sha_file(RAW_PATH),
                "landing_hash": sha_file(LANDING_PATH),
                "source_datasets": len(source["PureOrMixtureData"]),
                "source_points": sum(len(row["NumValues"]) for row in source["PureOrMixtureData"]),
                "equilibrium_states": len(targets),
                "matched_states": matched_count,
                "pressure_only_states": unmatched_count,
                "absence_coordinates": absent_coordinate_count,
                "identity_hash": identity_hash,
                "identity_file_hash": sha_file(IDENTITY_PATH),
                "target_hash": sha_file(TARGET_PATH),
                "primary_hash": sha_file(PRIMARY_PATH),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
