#!/usr/bin/env python3
"""Capture the complete NIST ThermoML solution-activity surface for THERMO-009."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/solution_activity_capture_spec_v1.json"
SPEC_HASH = "sha256:bcd3af58c80f7bf971a96d7c94a5f0d961c094bc2082282dc01e58f714ef431b"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-009-solution-activity-v1"
RAW_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2019-9b00694.json"
LANDING_PATH = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2019-9b00694.html"
PRIMARY_PATH = SNAPSHOT_ROOT / "solution-activity-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/solution_activity_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/solution_activity_withheld_targets_v1.json"


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


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-009 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-solution-activity-prefetch-capture-spec/1"
        or spec.get("all_activity_composition_condition_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
    ):
        raise ValueError("THERMO-009 prefetch boundary is not value-free")
    raw = fetch(spec["source"]["json_url"])
    landing = fetch(spec["source"]["landing_url"])
    source = json.loads(raw, parse_float=str, parse_int=str)
    if source.get("Citation", {}).get("sDOI") != spec["source"]["doi"]:
        raise ValueError("captured ThermoML DOI changed")
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    LANDING_PATH.write_bytes(landing)
    compounds = {row["RegNum"]["nOrgNum"]: row for row in source["Compound"]}
    if len(compounds) != 6 or "6" not in compounds:
        raise ValueError("THERMO-009 compound surface changed")
    identities: list[dict] = []
    targets: list[dict] = []
    dataset_summaries: list[dict] = []
    absent_coordinate_count = 0
    absent_row_count = 0
    target_ordinal = 1
    for dataset in source["PureOrMixtureData"]:
        dataset_ordinal = dataset["nPureOrMixtureDataNumber"]
        property_metadata = dataset["Property"][0]
        group = property_metadata["Property-MethodID"]["PropertyGroup"]
        activity = group.get("ActivityFugacityOsmoticProp", {})
        if (
            activity.get("ePropName") != "(Relative) activity"
            or activity.get("sMethodName") != "ISOPIE"
            or property_metadata["Property-MethodID"]["RegNum"].get("nOrgNum") != "6"
            or property_metadata.get("ePresentation") != "Direct value, X"
            or property_metadata.get("eStandardState") != "Pure compound"
            or property_metadata.get("PropPhaseID", {}).get("ePropPhase") != "Liquid"
        ):
            raise ValueError("THERMO-009 encountered a non-direct water-activity dataset")
        constraints = dataset.get("Constraint", ())
        if (
            len(constraints) != 1
            or constraints[0]["ConstraintID"]["ConstraintType"].get("eTemperature") != "Temperature, K"
            or constraints[0].get("nConstraintValue") != "298.15"
        ):
            raise ValueError("THERMO-009 dataset changed its fixed temperature")
        variables = {row["nVarNumber"]: row for row in dataset["Variable"]}
        if len(variables) not in {1, 2}:
            raise ValueError("THERMO-009 solution composition is not binary or ternary")
        for variable in variables.values():
            if (
                variable["VariableID"]["VariableType"].get("eComponentComposition")
                != "Molality, mol/kg"
                or variable.get("VarPhaseID", {}).get("eVarPhase") != "Liquid"
                or variable["VariableID"]["RegNum"].get("nOrgNum") == "6"
            ):
                raise ValueError("THERMO-009 variable is not a retained solute composition")
        dataset_absent_rows = 0
        for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
            variable_values = {row["nVarNumber"]: row for row in point["VariableValue"]}
            if set(variable_values) != set(variables):
                raise ValueError("THERMO-009 point does not preserve every composition variable")
            property_values = point["PropertyValue"]
            if len(property_values) != 1:
                raise ValueError("THERMO-009 activity point is not singular")
            activity_inscription = property_values[0]["nPropValue"]
            activity_part = Fraction(activity_inscription)
            if activity_part.numerator <= 0 or activity_part > 1:
                raise ValueError("THERMO-009 relative activity is not an exact positive part of the One")
            interface_entries = []
            row_has_absence = False
            for variable_number in sorted(variables, key=int):
                variable = variables[variable_number]
                value = variable_values[variable_number]
                inscription = value["nVarValue"]
                is_absence = Fraction(inscription).numerator == 0
                if is_absence:
                    absent_coordinate_count += 1
                    row_has_absence = True
                interface_entries.append(
                    {
                        "variable_number": variable_number,
                        "component_orgnum": variable["VariableID"]["RegNum"]["nOrgNum"],
                        "external_molality_inscription": inscription,
                        "sft_interface_state": "EmptyOne" if is_absence else "exact-positive-composition-coordinate",
                        "complete_variable_value": value,
                    }
                )
            if row_has_absence:
                absent_row_count += 1
                dataset_absent_rows += 1
            target_id = f"SFT-CHEM-THERMO-009-ACTIVITY-{target_ordinal:04d}"
            identity = {
                "target_id": target_id,
                "doi": spec["source"]["doi"],
                "source_id": spec["source"]["source_id"],
                "dataset_ordinal": dataset_ordinal,
                "source_point_ordinal": point_ordinal,
                "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_absent": True,
            }
            target = {
                "target_id": target_id,
                "dataset_ordinal": dataset_ordinal,
                "source_point_ordinal": point_ordinal,
                "ordered_component_orgnums": [row["RegNum"]["nOrgNum"] for row in dataset["Component"]],
                "complete_component_records": [compounds[row["RegNum"]["nOrgNum"]] for row in dataset["Component"]],
                "water_component_orgnum": "6",
                "temperature_K_external_inscription": "298.15",
                "relative_water_activity_external_inscription": activity_inscription,
                "composition_interface_entries": interface_entries,
                "complete_source_point": point,
                "complete_property_metadata": dataset["Property"],
                "complete_variable_metadata": dataset["Variable"],
                "complete_constraint_metadata": dataset["Constraint"],
                "activity_uncertainty": dict(property_values[0].get("CombinedUncertainty", {})),
                "external_measurement_method": "ISOPIE",
                "external_standard_state": "Pure compound",
            }
            identities.append(identity)
            targets.append(target)
            target_ordinal += 1
        dataset_summaries.append(
            {
                "dataset_ordinal": dataset_ordinal,
                "ordered_component_orgnums": [row["RegNum"]["nOrgNum"] for row in dataset["Component"]],
                "composition_variable_count": len(variables),
                "point_count": len(dataset["NumValues"]),
                "absent_component_row_count": dataset_absent_rows,
            }
        )
    if len(source["PureOrMixtureData"]) != 9 or len(targets) != 204:
        raise ValueError("THERMO-009 complete solution-activity surface changed")
    identity_doc = {
        "schema": "sft-v3-solution-activity-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "all_compound_temperature_composition_activity_uncertainty_absence_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-solution-activity-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-solution-activity-primary-records/1",
        "prefetch_capture_spec_hash_before_http_fetch": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": spec["source"]["source_id"],
        "doi": spec["source"]["doi"],
        "raw_json_snapshot_path": str(RAW_PATH.relative_to(ROOT)),
        "raw_json_snapshot_hash": sha_file(RAW_PATH),
        "landing_snapshot_path": str(LANDING_PATH.relative_to(ROOT)),
        "landing_snapshot_hash": sha_file(LANDING_PATH),
        "complete_compound_count": len(compounds),
        "complete_dataset_count": len(source["PureOrMixtureData"]),
        "complete_activity_row_count": len(targets),
        "complete_binary_dataset_count": sum(row["composition_variable_count"] == 1 for row in dataset_summaries),
        "complete_ternary_dataset_count": sum(row["composition_variable_count"] == 2 for row in dataset_summaries),
        "external_absence_glyph_coordinate_count": absent_coordinate_count,
        "external_absence_glyph_row_count": absent_row_count,
        "dataset_summaries": dataset_summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_activity_rows_and_absent_component_boundaries_preserved": True,
        "correlated_regressed_or_model_calculated_values_used_as_measurements": False,
        "activity_coefficient_fitted_or_imported": False,
        "external_values_used_as_proof_parameters": False,
        "external_zero_glyphs_translated_only_to_structural_EmptyOne": True,
    }
    write_json(PRIMARY_PATH, primary)
    print(
        json.dumps(
            {
                "prefetch_spec_hash": SPEC_HASH,
                "raw_hash": sha_file(RAW_PATH),
                "landing_hash": sha_file(LANDING_PATH),
                "dataset_count": len(source["PureOrMixtureData"]),
                "target_count": len(targets),
                "absent_coordinate_count": absent_coordinate_count,
                "absent_row_count": absent_row_count,
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
