#!/usr/bin/env python3
"""Capture complete authoritative thermal-conductivity surfaces for THERMO-018."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/thermal_conductivity_capture_spec_v1.json"
SPEC_HASH = "sha256:7dd5d45a8cc06bb2472daa4951b1297c5f73fba9ce1575526ac6dcac829d3473"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-018-thermal-conductivity-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "thermal-conductivity-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/thermal_conductivity_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/thermal_conductivity_withheld_targets_v1.json"


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


def numbered(rows: list[dict] | None, field: str) -> dict[int, dict]:
    return {int(row[field]): row for row in rows or ()}


def transport_property(metadata: dict) -> tuple[str, str]:
    record = metadata.get("Property-MethodID", {}).get("PropertyGroup", {}).get("TransportProp", {})
    return str(record.get("ePropName", "")), str(record.get("sMethodName") or record.get("eMethodName") or "")


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-018 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-thermal-conductivity-prefetch-capture-spec/1"
        or spec.get("admissible_thermal_conductivity_property_name") != "Thermal conductivity, W/m/K"
        or spec.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 3
    ):
        raise ValueError("THERMO-018 prefetch boundary is not value-free and complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    identities: list[dict] = []
    targets: list[dict] = []
    source_summaries: list[dict] = []
    target_ordinal = 1

    for source_spec in spec["sources"]:
        raw = fetch(source_spec["json_url"])
        landing = fetch(source_spec["landing_url"])
        stem = source_spec["source_id"].lower()
        raw_path = SNAPSHOT_ROOT / f"{stem}.json"
        landing_path = SNAPSHOT_ROOT / f"{stem}.html"
        raw_path.write_bytes(raw)
        landing_path.write_bytes(landing)
        source = json.loads(raw.decode("utf-8"), parse_float=str, parse_int=str)
        if source.get("Citation", {}).get("sDOI") != source_spec["doi"]:
            raise ValueError("THERMO-018 source DOI changed")

        compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
        conductivity_summaries: list[dict] = []
        companion_summaries: list[dict] = []
        for dataset in source["PureOrMixtureData"]:
            dataset_ordinal = int(dataset["nPureOrMixtureDataNumber"])
            components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset.get("Component", ()))
            if not components or len(set(components)) != len(components) or any(number not in compounds for number in components):
                raise ValueError("THERMO-018 component carrier changed")
            variables = numbered(dataset.get("Variable"), "nVarNumber")
            properties = numbered(dataset.get("Property"), "nPropNumber")
            property_value_counts: dict[int, int] = {number: 0 for number in properties}
            dataset_target_ids: list[str] = []

            for property_number, metadata in properties.items():
                property_name, method = transport_property(metadata)
                if metadata.get("ePresentation") != "Direct value, X" or property_name != "Thermal conductivity, W/m/K":
                    companion_summaries.append({
                        "dataset_ordinal": dataset_ordinal,
                        "property_number": property_number,
                        "complete_property_metadata": metadata,
                        "excluded_from_thermal_conductivity_measurements": True,
                    })
                    continue
                phase = str(metadata.get("PropPhaseID", {}).get("ePropPhase", ""))
                if not phase or not method:
                    raise ValueError("THERMO-018 phase or measurement method changed")
                for point_ordinal, point in enumerate(dataset.get("NumValues", ()), start=1):
                    property_values = numbered(point.get("PropertyValue"), "nPropNumber")
                    variable_values = numbered(point.get("VariableValue"), "nVarNumber")
                    if set(variable_values) != set(variables):
                        raise ValueError("THERMO-018 variable carrier is incomplete")
                    if property_number not in property_values:
                        continue
                    value_record = property_values[property_number]
                    property_value_counts[property_number] += 1
                    target_id = f"SFT-CHEM-THERMO-018-THERMAL-CONDUCTIVITY-{target_ordinal:04d}"
                    identity = {
                        "target_id": target_id,
                        "source_id": source_spec["source_id"],
                        "dataset_ordinal": dataset_ordinal,
                        "property_number": property_number,
                        "source_point_ordinal": point_ordinal,
                        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
                    }
                    target = {
                        "target_id": target_id,
                        "source_id": source_spec["source_id"],
                        "doi": source_spec["doi"],
                        "dataset_ordinal": dataset_ordinal,
                        "property_number": property_number,
                        "source_point_ordinal": point_ordinal,
                        "component_orgnums": list(components),
                        "complete_component_records": [compounds[number] for number in components],
                        "mixture_class": {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component"),
                        "property_name": property_name,
                        "property_phase": phase,
                        "measurement_method": method,
                        "thermal_conductivity_W_m_K_external_inscription": value_record["nPropValue"],
                        "thermal_conductivity_uncertainty_external_record": value_record.get("CombinedUncertainty", {}),
                        "variable_external_inscriptions": {str(number): value["nVarValue"] for number, value in variable_values.items()},
                        "complete_point_record": point,
                        "complete_property_metadata": metadata,
                        "complete_variable_metadata": dataset.get("Variable", ()),
                        "complete_constraint_metadata": dataset.get("Constraint", ()),
                        "complete_phase_metadata": dataset.get("PhaseID", ()),
                    }
                    identities.append(identity)
                    targets.append(target)
                    dataset_target_ids.append(target_id)
                    target_ordinal += 1
                conductivity_summaries.append({
                    "dataset_ordinal": dataset_ordinal,
                    "property_number": property_number,
                    "component_orgnums": list(components),
                    "mixture_class": target["mixture_class"] if dataset_target_ids else {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component"),
                    "property_phase": phase,
                    "measurement_method": method,
                    "point_count": property_value_counts[property_number],
                    "target_ids_in_source_order": dataset_target_ids[-property_value_counts[property_number]:],
                })

        source_summaries.append({
            "source_id": source_spec["source_id"],
            "doi": source_spec["doi"],
            "raw_path": str(raw_path.relative_to(ROOT)),
            "raw_hash": sha_file(raw_path),
            "landing_path": str(landing_path.relative_to(ROOT)),
            "landing_hash": sha_file(landing_path),
            "complete_compound_count": len(source["Compound"]),
            "complete_dataset_count": len(source["PureOrMixtureData"]),
            "complete_all_property_point_count": sum(len(row.get("NumValues", ())) for row in source["PureOrMixtureData"]),
            "thermal_conductivity_dataset_count": len(conductivity_summaries),
            "thermal_conductivity_point_count": sum(row["point_count"] for row in conductivity_summaries),
            "thermal_conductivity_dataset_summaries": conductivity_summaries,
            "companion_property_summaries": companion_summaries,
            "complete_source_and_all_companion_datasets_preserved": True,
            "non_thermal_conductivity_companions_excluded_from_measurements": True,
        })

    mixture_counts = {name: sum(row["mixture_class"] == name for row in targets) for name in ("pure", "binary", "ternary", "higher-component")}
    mixture_counts = {key: value for key, value in mixture_counts.items() if value}
    phase_counts: dict[str, int] = {}
    method_counts: dict[str, int] = {}
    for row in targets:
        phase_counts[row["property_phase"]] = phase_counts.get(row["property_phase"], 0) + 1
        method_counts[row["measurement_method"]] = method_counts.get(row["measurement_method"], 0) + 1
    if not targets or not {"pure", "binary", "ternary"}.issubset(mixture_counts) or not {"Gas", "Liquid"}.issubset(phase_counts) or not any(name.startswith("Crystal") for name in phase_counts):
        raise ValueError("THERMO-018 structural source coverage changed")

    identity_doc = {
        "schema": "sft-v3-thermal-conductivity-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "complete_source_count": len(source_summaries),
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-thermal-conductivity-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "mixture_class_counts": mixture_counts,
        "phase_counts": phase_counts,
        "measurement_method_counts": method_counts,
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-thermal-conductivity-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "complete_source_count": len(source_summaries),
        "complete_compound_record_count_across_sources": sum(row["complete_compound_count"] for row in source_summaries),
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
        "complete_thermal_conductivity_dataset_count": sum(row["thermal_conductivity_dataset_count"] for row in source_summaries),
        "complete_target_count": len(targets),
        "mixture_class_counts": mixture_counts,
        "phase_counts": phase_counts,
        "measurement_method_counts": method_counts,
        "source_summaries": source_summaries,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_thermal_conductivity_rows_and_complete_sources_preserved": True,
        "non_thermal_conductivity_companions_used_as_thermal_conductivity_measurements": False,
        "Fourier_constitutive_temperature_gradient_kinetic_theory_mixing_temperature_law_logarithm_continuum_interpolation_regression_selection_or_target_correction_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "mixture_counts": mixture_counts,
        "phase_counts": phase_counts,
        "method_counts": method_counts,
        "complete_target_count": len(targets),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
