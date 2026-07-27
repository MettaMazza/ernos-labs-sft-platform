#!/usr/bin/env python3
"""Capture complete authoritative molecular-diffusion surfaces for THERMO-016."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/molecular_diffusion_capture_spec_v1.json"
SPEC_HASH = "sha256:2e6bfea67b91d063ff050104232e3985942ede546f6698750b3ab3abd7a6c397"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-016-molecular-diffusion-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "molecular-diffusion-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_diffusion_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_diffusion_withheld_targets_v1.json"


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
        raise ValueError("THERMO-016 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    admissible = tuple(spec.get("admissible_diffusion_property_names", ()))
    if (
        spec.get("schema") != "sft-v3-molecular-diffusion-prefetch-capture-spec/1"
        or spec.get("all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or admissible != (
            "Binary diffusion coefficient, m2/s", "Self diffusion coefficient, m2/s", "Tracer diffusion coefficient, m2/s"
        )
        or len(spec.get("sources", ())) != 3
    ):
        raise ValueError("THERMO-016 prefetch boundary is not value-free and three-class complete")
    class_by_property = {
        "Binary diffusion coefficient, m2/s": "binary",
        "Self diffusion coefficient, m2/s": "self",
        "Tracer diffusion coefficient, m2/s": "tracer",
    }
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
            raise ValueError("THERMO-016 source DOI changed")
        compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
        diffusion_dataset_summaries = []
        companion_dataset_summaries = []
        for dataset in source["PureOrMixtureData"]:
            dataset_ordinal = int(dataset["nPureOrMixtureDataNumber"])
            if len(dataset.get("Property", ())) != 1:
                raise ValueError("THERMO-016 property count changed")
            metadata = dataset["Property"][0]
            property_name, method = transport_property(metadata)
            if metadata.get("ePresentation") != "Direct value, X" or property_name not in admissible:
                companion_dataset_summaries.append({
                    "dataset_ordinal": dataset_ordinal, "point_count": len(dataset.get("NumValues", ())),
                    "complete_property_metadata": dataset.get("Property", ()),
                    "excluded_from_diffusion_measurements": True,
                })
                continue
            diffusion_class = class_by_property[property_name]
            components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset["Component"])
            if not components or len(set(components)) != len(components) or any(number not in compounds for number in components):
                raise ValueError("THERMO-016 component carrier changed")
            variables = numbered(dataset.get("Variable", ()), "nVarNumber")
            properties = numbered(dataset["Property"], "nPropNumber")
            property_component = metadata.get("Property-MethodID", {}).get("RegNum", {}).get("nOrgNum")
            solvents = metadata.get("Solvent", {}).get("RegNum", ())
            solvent_orgnums = tuple(int(row["nOrgNum"]) for row in solvents)
            dataset_target_ids = []
            for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
                property_values = numbered(point.get("PropertyValue", ()), "nPropNumber")
                variable_values = numbered(point.get("VariableValue", ()), "nVarNumber")
                if set(property_values) != set(properties) or set(variable_values) != set(variables):
                    raise ValueError("THERMO-016 direct diffusion point is incomplete")
                target_id = f"SFT-CHEM-THERMO-016-{diffusion_class.upper()}-{target_ordinal:04d}"
                identity = {
                    "target_id": target_id, "source_id": source_spec["source_id"],
                    "diffusion_class": diffusion_class, "dataset_ordinal": dataset_ordinal,
                    "source_point_ordinal": point_ordinal,
                    "all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
                }
                target = {
                    "target_id": target_id, "source_id": source_spec["source_id"], "doi": source_spec["doi"],
                    "diffusion_class": diffusion_class, "dataset_ordinal": dataset_ordinal,
                    "source_point_ordinal": point_ordinal, "component_orgnums": list(components),
                    "complete_component_records": [compounds[number] for number in components],
                    "property_component_orgnum": int(property_component) if property_component is not None else None,
                    "solvent_orgnums": list(solvent_orgnums), "property_name": property_name,
                    "measurement_method": method,
                    "diffusion_coefficient_m2_per_s_external_inscription": property_values[1]["nPropValue"],
                    "diffusion_uncertainty_external_record": property_values[1].get("CombinedUncertainty", {}),
                    "variable_external_inscriptions": {str(number): value["nVarValue"] for number, value in variable_values.items()},
                    "complete_point_record": point, "complete_property_metadata": dataset["Property"],
                    "complete_variable_metadata": dataset.get("Variable", ()),
                    "complete_constraint_metadata": dataset.get("Constraint", ()),
                    "complete_phase_metadata": dataset.get("PhaseID", ()),
                }
                identities.append(identity)
                targets.append(target)
                dataset_target_ids.append(target_id)
                target_ordinal += 1
            diffusion_dataset_summaries.append({
                "dataset_ordinal": dataset_ordinal, "diffusion_class": diffusion_class,
                "component_orgnums": list(components), "property_component_orgnum": property_component,
                "solvent_orgnums": list(solvent_orgnums), "measurement_method": method,
                "point_count": len(dataset_target_ids), "target_ids_in_source_order": dataset_target_ids,
            })
        source_summaries.append({
            "source_id": source_spec["source_id"], "doi": source_spec["doi"],
            "raw_path": str(raw_path.relative_to(ROOT)), "raw_hash": sha_file(raw_path),
            "landing_path": str(landing_path.relative_to(ROOT)), "landing_hash": sha_file(landing_path),
            "complete_compound_count": len(source["Compound"]),
            "complete_dataset_count": len(source["PureOrMixtureData"]),
            "complete_all_property_point_count": sum(len(row.get("NumValues", ())) for row in source["PureOrMixtureData"]),
            "diffusion_dataset_count": len(diffusion_dataset_summaries),
            "diffusion_point_count": sum(row["point_count"] for row in diffusion_dataset_summaries),
            "diffusion_dataset_summaries": diffusion_dataset_summaries,
            "companion_dataset_summaries": companion_dataset_summaries,
            "complete_source_and_all_companion_datasets_preserved": True,
            "non_diffusion_companion_datasets_excluded_from_measurements": True,
        })
    class_counts = {name: sum(row["diffusion_class"] == name for row in targets) for name in ("binary", "self", "tracer")}
    if class_counts != {"binary": 138, "self": 4, "tracer": 22} or len(targets) != 164:
        raise ValueError("THERMO-016 complete three-class diffusion census changed")
    identity_doc = {
        "schema": "sft-v3-molecular-diffusion-target-identities/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities), "diffusion_class_counts": class_counts,
        "all_species_medium_phase_composition_temperature_pressure_method_value_uncertainty_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-molecular-diffusion-withheld-targets/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash, "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets), "diffusion_class_counts": class_counts, "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-molecular-diffusion-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH, "capture_rule": spec["capture_rule"],
        "complete_source_count": len(source_summaries),
        "complete_compound_record_count_across_sources": sum(row["complete_compound_count"] for row in source_summaries),
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
        "complete_diffusion_dataset_count": sum(row["diffusion_dataset_count"] for row in source_summaries),
        "complete_target_count": len(targets), "diffusion_class_counts": class_counts,
        "source_summaries": source_summaries, "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_direct_binary_self_and_tracer_diffusion_rows_and_complete_sources_preserved": True,
        "non_diffusion_companion_datasets_used_as_diffusion_measurements": False,
        "Fick_Brownian_random_walk_Stokes_Einstein_activation_transport_fit_logarithm_continuum_interpolation_regression_selection_or_target_correction_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH, "class_counts": class_counts, "complete_target_count": len(targets),
        "identity_hash": identity_hash, "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH), "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
        "complete_dataset_count_across_sources": sum(row["complete_dataset_count"] for row in source_summaries),
        "complete_all_property_point_count_across_sources": sum(row["complete_all_property_point_count"] for row in source_summaries),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
