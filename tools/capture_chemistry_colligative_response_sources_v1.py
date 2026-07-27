#!/usr/bin/env python3
"""Capture complete boiling, freezing and osmotic response surfaces for THERMO-014."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/colligative_response_capture_spec_v1.json"
SPEC_HASH = "sha256:f4b45418ce4fd5b961e457c8ac7ce9d9bbc001bbacfb11a9d0c61395f945e0c5"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-014-colligative-response-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "colligative-response-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/colligative_response_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/colligative_response_withheld_targets_v1.json"


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


def single_property(dataset: dict) -> tuple[dict, dict]:
    if len(dataset.get("Property", ())) != 1 or dataset["Property"][0].get("ePresentation") != "Direct value, X":
        raise ValueError("THERMO-014 property is not a singular direct measurement")
    metadata = dataset["Property"][0]
    return metadata, metadata["Property-MethodID"]["PropertyGroup"]


def numbered(rows: list[dict], field: str) -> dict[int, dict]:
    return {int(row[field]): row for row in rows}


def constraints_by_type(dataset: dict) -> dict[str, dict]:
    result = {}
    for row in dataset.get("Constraint", ()):
        types = row["ConstraintID"]["ConstraintType"]
        names = tuple(name for name in types if name != "tml_elements")
        if len(names) != 1:
            raise ValueError("THERMO-014 constraint type changed")
        result[names[0]] = row
    return result


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-014 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-colligative-response-prefetch-capture-spec/1"
        or spec.get("all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or tuple(row["response_class"] for row in spec.get("sources", ())) != ("boiling", "freezing", "osmotic")
    ):
        raise ValueError("THERMO-014 prefetch boundary is not value-free and three-class complete")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    identities: list[dict] = []
    targets: list[dict] = []
    source_summaries: list[dict] = []
    target_ordinal = 1
    for source_spec in spec["sources"]:
        response_class = source_spec["response_class"]
        raw = fetch(source_spec["json_url"])
        landing = fetch(source_spec["landing_url"])
        stem = source_spec["source_id"].lower()
        raw_path = SNAPSHOT_ROOT / f"{stem}.json"
        landing_path = SNAPSHOT_ROOT / f"{stem}.html"
        raw_path.write_bytes(raw)
        landing_path.write_bytes(landing)
        source = json.loads(raw.decode("utf-8"), parse_float=str, parse_int=str)
        if source.get("Citation", {}).get("sDOI") != source_spec["doi"]:
            raise ValueError("THERMO-014 source DOI changed")
        compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
        dataset_summaries = []
        for dataset in source["PureOrMixtureData"]:
            metadata, group = single_property(dataset)
            if response_class == "boiling":
                property_record = group.get("VaporPBoilingTAzeotropTandP", {})
                expected_name = "Boiling temperature at pressure P, K"
                expected_method = "Gas Burette"
            elif response_class == "freezing":
                property_record = group.get("PhaseTransition", {})
                expected_name = "Solid-liquid equilibrium temperature, K"
                expected_method = "VISOBS"
            else:
                property_record = group.get("ActivityFugacityOsmoticProp", {})
                expected_name = "Osmotic coefficient"
                expected_method = "vapour pressure osmometry"
            method = property_record.get("sMethodName") or property_record.get("eMethodName")
            if property_record.get("ePropName") != expected_name or method != expected_method:
                raise ValueError(f"THERMO-014 {response_class} source contains a non-target dataset")
            variables = numbered(dataset["Variable"], "nVarNumber")
            if len(variables) != 1 or variables[1]["VariableID"]["VariableType"].get("eComponentComposition") not in ("Mole fraction", "Molality, mol/kg"):
                raise ValueError("THERMO-014 composition coordinate changed")
            composition_component = int(variables[1]["VariableID"]["RegNum"]["nOrgNum"])
            constraints = constraints_by_type(dataset)
            if response_class in ("boiling", "freezing") and set(constraints) != {"ePressure"}:
                raise ValueError("THERMO-014 phase response pressure boundary changed")
            if response_class == "osmotic" and set(constraints) != {"ePressure", "eTemperature"}:
                raise ValueError("THERMO-014 osmotic environment boundary changed")
            components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset["Component"])
            if len(components) != 2 or composition_component not in components:
                raise ValueError("THERMO-014 solvent/solute support changed")
            dataset_target_ids = []
            for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
                variable_values = numbered(point["VariableValue"], "nVarNumber")
                property_values = numbered(point["PropertyValue"], "nPropNumber")
                if set(variable_values) != {1} or set(property_values) != {1}:
                    raise ValueError("THERMO-014 response point is incomplete")
                target_id = f"SFT-CHEM-THERMO-014-{response_class.upper()}-{target_ordinal:04d}"
                identity = {
                    "target_id": target_id,
                    "doi": source_spec["doi"],
                    "source_id": source_spec["source_id"],
                    "response_class": response_class,
                    "dataset_ordinal": int(dataset["nPureOrMixtureDataNumber"]),
                    "source_point_ordinal": point_ordinal,
                    "all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent": True,
                }
                target = {
                    "target_id": target_id,
                    "source_id": source_spec["source_id"],
                    "response_class": response_class,
                    "dataset_ordinal": int(dataset["nPureOrMixtureDataNumber"]),
                    "source_point_ordinal": point_ordinal,
                    "component_orgnums": list(components),
                    "complete_component_records": [compounds[number] for number in components],
                    "composition_component_orgnum": composition_component,
                    "composition_coordinate_kind": variables[1]["VariableID"]["VariableType"]["eComponentComposition"],
                    "composition_external_inscription": variable_values[1]["nVarValue"],
                    "response_external_inscription": property_values[1]["nPropValue"],
                    "pressure_kPa_external_inscription": constraints["ePressure"]["nConstraintValue"],
                    "temperature_K_external_inscription": constraints["eTemperature"]["nConstraintValue"] if response_class == "osmotic" else property_values[1]["nPropValue"],
                    "phase_ids": dataset["PhaseID"],
                    "complete_point_record": point,
                    "complete_property_metadata": dataset["Property"],
                    "complete_variable_metadata": dataset["Variable"],
                    "complete_constraint_metadata": dataset["Constraint"],
                    "complete_property_uncertainty": property_values[1].get("CombinedUncertainty", {}),
                    "external_measurement_method": method,
                }
                identities.append(identity)
                targets.append(target)
                dataset_target_ids.append(target_id)
                target_ordinal += 1
            dataset_summaries.append({
                "dataset_ordinal": int(dataset["nPureOrMixtureDataNumber"]),
                "component_orgnums": list(components),
                "point_count": len(dataset_target_ids),
                "target_ids_in_source_order": dataset_target_ids,
            })
        source_summaries.append({
            "source_id": source_spec["source_id"],
            "doi": source_spec["doi"],
            "response_class": response_class,
            "raw_path": str(raw_path.relative_to(ROOT)),
            "raw_hash": sha_file(raw_path),
            "landing_path": str(landing_path.relative_to(ROOT)),
            "landing_hash": sha_file(landing_path),
            "complete_compound_count": len(compounds),
            "complete_dataset_count": len(source["PureOrMixtureData"]),
            "complete_point_count": sum(len(row["NumValues"]) for row in source["PureOrMixtureData"]),
            "dataset_summaries": dataset_summaries,
        })
    class_counts = {name: sum(row["response_class"] == name for row in targets) for name in ("boiling", "freezing", "osmotic")}
    if class_counts != {"boiling": 144, "freezing": 37, "osmotic": 95} or len(targets) != 276:
        raise ValueError("THERMO-014 complete three-class response census changed")
    identity_doc = {
        "schema": "sft-v3-colligative-response-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "response_class_counts": class_counts,
        "all_compound_solvent_solute_phase_temperature_pressure_composition_response_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-colligative-response-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "response_class_counts": class_counts,
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-colligative-response-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "complete_source_count": len(source_summaries),
        "complete_compound_record_count_across_sources": sum(row["complete_compound_count"] for row in source_summaries),
        "complete_dataset_count": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_point_count": sum(row["complete_point_count"] for row in source_summaries),
        "complete_target_count": len(targets),
        "response_class_counts": class_counts,
        "source_summaries": source_summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_boiling_freezing_osmotic_rows_and_complete_sources_preserved": True,
        "conventional_response_equation_constant_dissociation_parameter_interpolation_regression_or_fit_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "class_counts": class_counts,
        "complete_target_count": len(targets),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
