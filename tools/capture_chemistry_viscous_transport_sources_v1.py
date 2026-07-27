#!/usr/bin/env python3
"""Capture complete authoritative viscosity surfaces for THERMO-017."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/viscous_transport_capture_spec_v1.json"
SPEC_HASH = "sha256:4f104a72d58f72540f07fdd73ce993945cedd35dc6f638bb647d4195cb1dfc50"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-017-viscous-transport-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "viscous-transport-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/viscous_transport_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/viscous_transport_withheld_targets_v1.json"


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


def transport_property(metadata: dict) -> tuple[str, str]:
    record = metadata.get("Property-MethodID", {}).get("PropertyGroup", {}).get("TransportProp", {})
    return str(record.get("ePropName", "")), str(record.get("sMethodName") or record.get("eMethodName") or "")


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-017 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-viscous-transport-prefetch-capture-spec/1"
        or spec.get("admissible_viscosity_property_name") != "Viscosity, Pa*s"
        or spec.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 3
    ):
        raise ValueError("THERMO-017 prefetch boundary is not value-free and complete")
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
        raw_path.write_bytes(raw); landing_path.write_bytes(landing)
        source = json.loads(raw.decode("utf-8"), parse_float=str, parse_int=str)
        if source.get("Citation", {}).get("sDOI") != source_spec["doi"]:
            raise ValueError("THERMO-017 source DOI changed")
        compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
        viscosity_summaries = []
        companion_summaries = []
        for dataset in source["PureOrMixtureData"]:
            dataset_ordinal = int(dataset["nPureOrMixtureDataNumber"])
            if len(dataset.get("Property", ())) != 1:
                raise ValueError("THERMO-017 property count changed")
            metadata = dataset["Property"][0]
            property_name, method = transport_property(metadata)
            if metadata.get("ePresentation") != "Direct value, X" or property_name != "Viscosity, Pa*s":
                companion_summaries.append({
                    "dataset_ordinal": dataset_ordinal, "point_count": len(dataset.get("NumValues", ())),
                    "complete_property_metadata": dataset.get("Property", ()), "excluded_from_viscosity_measurements": True,
                })
                continue
            components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset["Component"])
            if not components or len(set(components)) != len(components) or any(number not in compounds for number in components):
                raise ValueError("THERMO-017 component carrier changed")
            variables = numbered(dataset.get("Variable", ()), "nVarNumber")
            properties = numbered(dataset["Property"], "nPropNumber")
            dataset_target_ids = []
            for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
                property_values = numbered(point.get("PropertyValue", ()), "nPropNumber")
                variable_values = numbered(point.get("VariableValue", ()), "nVarNumber")
                if set(property_values) != set(properties) or set(variable_values) != set(variables):
                    raise ValueError("THERMO-017 direct viscosity point is incomplete")
                target_id = f"SFT-CHEM-THERMO-017-VISCOSITY-{target_ordinal:04d}"
                identity = {
                    "target_id": target_id, "source_id": source_spec["source_id"],
                    "dataset_ordinal": dataset_ordinal, "source_point_ordinal": point_ordinal,
                    "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
                }
                target = {
                    "target_id": target_id, "source_id": source_spec["source_id"], "doi": source_spec["doi"],
                    "dataset_ordinal": dataset_ordinal, "source_point_ordinal": point_ordinal,
                    "component_orgnums": list(components), "complete_component_records": [compounds[number] for number in components],
                    "mixture_class": {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component"),
                    "property_name": property_name, "measurement_method": method,
                    "viscosity_Pa_s_external_inscription": property_values[1]["nPropValue"],
                    "viscosity_uncertainty_external_record": property_values[1].get("CombinedUncertainty", {}),
                    "variable_external_inscriptions": {str(number): value["nVarValue"] for number, value in variable_values.items()},
                    "complete_point_record": point, "complete_property_metadata": dataset["Property"],
                    "complete_variable_metadata": dataset.get("Variable", ()),
                    "complete_constraint_metadata": dataset.get("Constraint", ()),
                    "complete_phase_metadata": dataset.get("PhaseID", ()),
                }
                identities.append(identity); targets.append(target); dataset_target_ids.append(target_id); target_ordinal += 1
            viscosity_summaries.append({
                "dataset_ordinal": dataset_ordinal, "component_orgnums": list(components),
                "mixture_class": {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component"),
                "measurement_method": method, "point_count": len(dataset_target_ids),
                "target_ids_in_source_order": dataset_target_ids,
            })
        source_summaries.append({
            "source_id": source_spec["source_id"], "doi": source_spec["doi"],
            "raw_path": str(raw_path.relative_to(ROOT)), "raw_hash": sha_file(raw_path),
            "landing_path": str(landing_path.relative_to(ROOT)), "landing_hash": sha_file(landing_path),
            "complete_compound_count": len(source["Compound"]),
            "complete_dataset_count": len(source["PureOrMixtureData"]),
            "complete_all_property_point_count": sum(len(row.get("NumValues", ())) for row in source["PureOrMixtureData"]),
            "viscosity_dataset_count": len(viscosity_summaries),
            "viscosity_point_count": sum(row["point_count"] for row in viscosity_summaries),
            "viscosity_dataset_summaries": viscosity_summaries, "companion_dataset_summaries": companion_summaries,
            "complete_source_and_all_companion_datasets_preserved": True,
            "non_viscosity_companion_datasets_excluded_from_measurements": True,
        })
    mixture_counts = {name: sum(row["mixture_class"] == name for row in targets) for name in ("pure", "binary", "ternary")}
    if mixture_counts != {"pure": 11, "binary": 364, "ternary": 50} or len(targets) != 425:
        raise ValueError("THERMO-017 complete pure/binary/ternary viscosity census changed")
    identity_doc = {
        "schema": "sft-v3-viscous-transport-target-identities/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities), "mixture_class_counts": mixture_counts,
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc)); identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-viscous-transport-withheld-targets/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash, "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets), "mixture_class_counts": mixture_counts, "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc); write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-viscous-transport-primary-records/1", "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"], "complete_source_count": len(source_summaries),
        "complete_compound_record_count_across_sources": sum(row["complete_compound_count"] for row in source_summaries),
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
        "complete_viscosity_dataset_count": sum(row["viscosity_dataset_count"] for row in source_summaries),
        "complete_target_count": len(targets), "mixture_class_counts": mixture_counts,
        "source_summaries": source_summaries, "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_viscosity_rows_and_complete_sources_preserved": True,
        "non_viscosity_companion_datasets_used_as_viscosity_measurements": False,
        "Newtonian_constitutive_velocity_gradient_Arrhenius_WLF_VFT_logarithm_continuum_interpolation_regression_selection_or_target_correction_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH, "mixture_counts": mixture_counts, "complete_target_count": len(targets),
        "identity_hash": identity_hash, "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH), "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
