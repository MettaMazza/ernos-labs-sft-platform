#!/usr/bin/env python3
"""Capture complete authoritative coupled-transport surfaces for THERMO-019."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/coupled_transport_capture_spec_v1.json"
SPEC_HASH = "sha256:b2298b06853b284b285df81121969885b2759366abc273c7e55585145bf723e2"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-019-coupled-transport-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "coupled-transport-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/coupled_transport_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/coupled_transport_withheld_targets_v1.json"


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


def property_record(metadata: dict) -> tuple[str, str]:
    group = metadata.get("Property-MethodID", {}).get("PropertyGroup", {})
    records = tuple(value for key, value in group.items() if key != "tml_elements" and isinstance(value, dict))
    if len(records) != 1:
        return "", ""
    record = records[0]
    return str(record.get("ePropName") or record.get("sPropName") or ""), str(record.get("sMethodName") or record.get("eMethodName") or "")


def coupled_property(pair: str, name: str, method: str) -> str | None:
    if pair == "mass-heat" and name == "Binary diffusion coefficient, m2/s" and "thermal-diffusion" in method:
        return "mass-response-under-thermal-forcing"
    if pair == "mass-charge" and name == "Electrical conductivity, S/m":
        return "charge-response"
    if pair == "mass-charge" and name == "Tracer diffusion coefficient, m2/s":
        return "mass-response-under-charge-probe"
    if pair == "heat-charge" and name == "Thermal conductivity, W/m/K":
        return "heat-response"
    if pair == "heat-charge" and name == "Electrical conductivity, S/m":
        return "charge-response"
    return None


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-019 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-coupled-transport-prefetch-capture-spec/1"
        or spec.get("all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or tuple(row.get("carrier_pair") for row in spec.get("sources", ())) != ("mass-heat", "mass-charge", "heat-charge")
    ):
        raise ValueError("THERMO-019 prefetch boundary is not value-free and pair-complete")

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
            raise ValueError("THERMO-019 source DOI changed")
        compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
        coupled_summaries: list[dict] = []
        companion_summaries: list[dict] = []
        for dataset in source["PureOrMixtureData"]:
            dataset_ordinal = int(dataset["nPureOrMixtureDataNumber"])
            components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset.get("Component", ()))
            if not components or len(set(components)) != len(components) or any(number not in compounds for number in components):
                raise ValueError("THERMO-019 component carrier changed")
            variables = numbered(dataset.get("Variable"), "nVarNumber")
            properties = numbered(dataset.get("Property"), "nPropNumber")
            for property_number, metadata in properties.items():
                name, method = property_record(metadata)
                response_role = coupled_property(source_spec["carrier_pair"], name, method)
                if metadata.get("ePresentation") != "Direct value, X" or response_role is None:
                    companion_summaries.append({
                        "dataset_ordinal": dataset_ordinal, "property_number": property_number,
                        "complete_property_metadata": metadata, "excluded_from_coupled_measurements": True,
                    })
                    continue
                phase = str(metadata.get("PropPhaseID", {}).get("ePropPhase", ""))
                if not phase or not method:
                    raise ValueError("THERMO-019 phase or method changed")
                dataset_targets: list[str] = []
                for point_ordinal, point in enumerate(dataset.get("NumValues", ()), start=1):
                    property_values = numbered(point.get("PropertyValue"), "nPropNumber")
                    variable_values = numbered(point.get("VariableValue"), "nVarNumber")
                    if set(variable_values) != set(variables):
                        raise ValueError("THERMO-019 variable carrier is incomplete")
                    if property_number not in property_values:
                        continue
                    value_record = property_values[property_number]
                    target_id = f"SFT-CHEM-THERMO-019-COUPLED-{target_ordinal:04d}"
                    identity = {
                        "target_id": target_id, "source_id": source_spec["source_id"],
                        "carrier_pair": source_spec["carrier_pair"], "dataset_ordinal": dataset_ordinal,
                        "property_number": property_number, "source_point_ordinal": point_ordinal,
                        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
                    }
                    target = {
                        "target_id": target_id, "source_id": source_spec["source_id"], "doi": source_spec["doi"],
                        "carrier_pair": source_spec["carrier_pair"], "response_role": response_role,
                        "dataset_ordinal": dataset_ordinal, "property_number": property_number,
                        "source_point_ordinal": point_ordinal, "component_orgnums": list(components),
                        "complete_component_records": [compounds[number] for number in components],
                        "mixture_class": {1: "pure", 2: "binary", 3: "ternary"}.get(len(components), "higher-component"),
                        "property_name": name, "property_phase": phase, "measurement_method": method,
                        "coupled_response_external_inscription": value_record["nPropValue"],
                        "coupled_response_uncertainty_external_record": value_record.get("CombinedUncertainty", {}),
                        "variable_external_inscriptions": {str(number): value["nVarValue"] for number, value in variable_values.items()},
                        "complete_point_record": point, "complete_property_metadata": metadata,
                        "complete_variable_metadata": dataset.get("Variable", ()),
                        "complete_constraint_metadata": dataset.get("Constraint", ()),
                        "complete_phase_metadata": dataset.get("PhaseID", ()),
                    }
                    identities.append(identity)
                    targets.append(target)
                    dataset_targets.append(target_id)
                    target_ordinal += 1
                coupled_summaries.append({
                    "carrier_pair": source_spec["carrier_pair"], "response_role": response_role,
                    "dataset_ordinal": dataset_ordinal, "property_number": property_number,
                    "component_orgnums": list(components), "property_name": name, "property_phase": phase,
                    "measurement_method": method, "point_count": len(dataset_targets),
                    "target_ids_in_source_order": dataset_targets,
                })
        source_summaries.append({
            "source_id": source_spec["source_id"], "doi": source_spec["doi"],
            "carrier_pair": source_spec["carrier_pair"], "raw_path": str(raw_path.relative_to(ROOT)),
            "raw_hash": sha_file(raw_path), "landing_path": str(landing_path.relative_to(ROOT)),
            "landing_hash": sha_file(landing_path), "complete_compound_count": len(source["Compound"]),
            "complete_dataset_count": len(source["PureOrMixtureData"]),
            "complete_all_property_point_count": sum(len(row.get("NumValues", ())) for row in source["PureOrMixtureData"]),
            "coupled_dataset_count": len(coupled_summaries),
            "coupled_point_count": sum(row["point_count"] for row in coupled_summaries),
            "coupled_dataset_summaries": coupled_summaries, "companion_property_summaries": companion_summaries,
            "complete_source_and_all_companion_datasets_preserved": True,
            "companion_properties_excluded_from_coupled_measurements": True,
        })

    pair_counts = {pair: sum(row["carrier_pair"] == pair for row in targets) for pair in ("mass-heat", "mass-charge", "heat-charge")}
    role_counts: dict[str, int] = {}
    property_counts: dict[str, int] = {}
    mixture_counts: dict[str, int] = {}
    method_counts: dict[str, int] = {}
    for row in targets:
        for table, key in ((role_counts, "response_role"), (property_counts, "property_name"), (mixture_counts, "mixture_class"), (method_counts, "measurement_method")):
            table[row[key]] = table.get(row[key], 0) + 1
    if not all(pair_counts.values()) or not {"binary", "ternary"}.issubset(mixture_counts) or len(method_counts) < 5:
        raise ValueError("THERMO-019 complete pairwise carrier coverage changed")

    identity_doc = {
        "schema": "sft-v3-coupled-transport-target-identities/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities), "complete_source_count": len(source_summaries),
        "carrier_pair_counts": pair_counts,
        "all_substance_mixture_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-coupled-transport-withheld-targets/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash, "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets), "carrier_pair_counts": pair_counts,
        "response_role_counts": role_counts, "property_counts": property_counts,
        "mixture_class_counts": mixture_counts, "measurement_method_counts": method_counts, "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-coupled-transport-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH, "capture_rule": spec["capture_rule"],
        "complete_source_count": len(source_summaries),
        "complete_compound_record_count_across_sources": sum(row["complete_compound_count"] for row in source_summaries),
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
        "complete_coupled_dataset_count": sum(row["coupled_dataset_count"] for row in source_summaries),
        "complete_target_count": len(targets), "carrier_pair_counts": pair_counts,
        "response_role_counts": role_counts, "property_counts": property_counts,
        "mixture_class_counts": mixture_counts, "measurement_method_counts": method_counts,
        "source_summaries": source_summaries, "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_coupled_rows_and_complete_sources_preserved": True,
        "companion_properties_used_as_coupled_measurements": False,
        "Onsager_matrix_continuum_gradient_flux_equation_phenomenological_cross_coefficient_signed_magnitude_fit_logarithm_interpolation_regression_selection_or_target_correction_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH, "pair_counts": pair_counts, "role_counts": role_counts,
        "property_counts": property_counts, "mixture_counts": mixture_counts, "method_counts": method_counts,
        "complete_target_count": len(targets), "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH), "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH), "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
