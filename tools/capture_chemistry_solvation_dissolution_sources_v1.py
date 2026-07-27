#!/usr/bin/env python3
"""Capture the complete authoritative THERMO-015 solvation/dissolution surfaces."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/solvation_dissolution_capture_spec_v1.json"
SPEC_HASH = "sha256:448f6a2812536b41cc673acb3d86af85cd25a685e0d6e8aadc0dfbdd47a70541"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-015-solvation-dissolution-v1"
PRIMARY_PATH = SNAPSHOT_ROOT / "solvation-dissolution-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/solvation_dissolution_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/solvation_dissolution_withheld_targets_v1.json"


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


def _free_solv_rows(raw: bytes) -> list[dict]:
    fields = (
        "compound_id", "smiles", "name", "experimental_hydration_free_energy_kcal_per_mol",
        "experimental_uncertainty_kcal_per_mol", "calculated_hydration_free_energy_kcal_per_mol",
        "calculated_uncertainty_kcal_per_mol", "experimental_reference", "calculated_reference", "notes",
    )
    rows = []
    for source_line_number, line in enumerate(raw.decode("utf-8").splitlines(), start=1):
        if not line.strip() or line.startswith("#"):
            continue
        values = tuple(value.strip() for value in line.split(";"))
        if len(values) != len(fields):
            raise ValueError("THERMO-015 FreeSolv row shape changed")
        row = dict(zip(fields, values))
        row["source_line_number"] = source_line_number
        rows.append(row)
    if len(rows) != 642 or len({row["compound_id"] for row in rows}) != 642:
        raise ValueError("THERMO-015 complete FreeSolv census changed")
    return rows


def _numbered(rows: list[dict], field: str) -> dict[int, dict]:
    return {int(row[field]): row for row in rows}


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-015 value-free capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-solvation-dissolution-prefetch-capture-spec/1"
        or spec.get("all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or tuple(row["source_class"] for row in spec.get("sources", ())) != ("solvation", "dissolution")
    ):
        raise ValueError("THERMO-015 prefetch boundary is not value-free and two-surface complete")

    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    identities: list[dict] = []
    targets: list[dict] = []
    source_summaries: list[dict] = []

    free_spec, thermo_spec = spec["sources"]
    free_raw = fetch(free_spec["raw_url"])
    free_landing = fetch(free_spec["landing_url"])
    free_raw_path = SNAPSHOT_ROOT / "freesolv-0.52-database.txt"
    free_landing_path = SNAPSHOT_ROOT / "freesolv-0.52-commit.html"
    free_raw_path.write_bytes(free_raw)
    free_landing_path.write_bytes(free_landing)
    free_rows = _free_solv_rows(free_raw)
    for ordinal, row in enumerate(free_rows, start=1):
        target_id = f"SFT-CHEM-THERMO-015-SOLVATION-{ordinal:04d}"
        identities.append({
            "target_id": target_id, "source_id": free_spec["source_id"], "source_class": "solvation",
            "source_row_ordinal": ordinal,
            "all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent": True,
        })
        targets.append({
            "target_id": target_id, "source_id": free_spec["source_id"], "source_class": "solvation",
            "source_row_ordinal": ordinal, "source_line_number": row["source_line_number"],
            "solute_compound_id": row["compound_id"], "solute_smiles": row["smiles"], "solute_name": row["name"],
            "solvent_identity": "water", "source_state": "isolated-gas-reference", "destination_state": "aqueous-hydrated-reference",
            "experimental_hydration_free_energy_kcal_per_mol_external_inscription": row["experimental_hydration_free_energy_kcal_per_mol"],
            "experimental_uncertainty_kcal_per_mol_external_inscription": row["experimental_uncertainty_kcal_per_mol"],
            "experimental_reference": row["experimental_reference"],
            "calculated_companion_fields_excluded_from_measurement": {
                "calculated_hydration_free_energy_kcal_per_mol": row["calculated_hydration_free_energy_kcal_per_mol"],
                "calculated_uncertainty_kcal_per_mol": row["calculated_uncertainty_kcal_per_mol"],
                "calculated_reference": row["calculated_reference"],
            },
            "complete_source_row": row,
        })
    source_summaries.append({
        "source_id": free_spec["source_id"], "source_class": "solvation",
        "raw_path": str(free_raw_path.relative_to(ROOT)), "raw_hash": sha_file(free_raw_path),
        "landing_path": str(free_landing_path.relative_to(ROOT)), "landing_hash": sha_file(free_landing_path),
        "complete_row_count": len(free_rows), "immutable_revision": free_spec["immutable_revision"],
        "all_experimental_and_calculated_companion_fields_preserved": True,
        "calculated_companion_fields_excluded_from_measurements": True,
    })

    thermo_raw = fetch(thermo_spec["json_url"])
    thermo_landing = fetch(thermo_spec["landing_url"])
    thermo_raw_path = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2016-61-1470-1476.json"
    thermo_landing_path = SNAPSHOT_ROOT / "nist-trc-thermoml-jced-2016-61-1470-1476.html"
    thermo_raw_path.write_bytes(thermo_raw)
    thermo_landing_path.write_bytes(thermo_landing)
    source = json.loads(thermo_raw.decode("utf-8"), parse_float=str, parse_int=str)
    if source.get("Citation", {}).get("sDOI") != thermo_spec["doi"]:
        raise ValueError("THERMO-015 NIST DOI changed")
    compounds = {int(row["RegNum"]["nOrgNum"]): row for row in source["Compound"]}
    target_ordinal = 1
    dataset_summaries = []
    for dataset in source["PureOrMixtureData"]:
        dataset_ordinal = int(dataset["nPureOrMixtureDataNumber"])
        if len(dataset.get("Property", ())) != 1:
            raise ValueError("THERMO-015 solubility property count changed")
        metadata = dataset["Property"][0]
        group = metadata["Property-MethodID"]["PropertyGroup"].get("CompositionAtPhaseEquilibrium", {})
        if metadata.get("ePresentation") != "Direct value, X" or group.get("ePropName") != "Mole fraction" or group.get("sMethodName") != "visual":
            raise ValueError("THERMO-015 non-direct or non-solubility dataset encountered")
        solute_orgnum = int(metadata["Property-MethodID"]["RegNum"]["nOrgNum"])
        components = tuple(int(row["RegNum"]["nOrgNum"]) for row in dataset["Component"])
        if solute_orgnum not in components or len(components) not in (2, 3):
            raise ValueError("THERMO-015 solute/solvent component carrier changed")
        solvent_orgnums = tuple(
            int(row["nOrgNum"]) for row in metadata.get("Solvent", {}).get("RegNum", ())
        ) or tuple(number for number in components if number != solute_orgnum)
        variables = _numbered(dataset["Variable"], "nVarNumber")
        dataset_target_ids = []
        for point_ordinal, point in enumerate(dataset["NumValues"], start=1):
            property_values = _numbered(point["PropertyValue"], "nPropNumber")
            variable_values = _numbered(point["VariableValue"], "nVarNumber")
            if set(property_values) != {1} or set(variable_values) != set(variables):
                raise ValueError("THERMO-015 incomplete direct solubility point")
            target_id = f"SFT-CHEM-THERMO-015-DISSOLUTION-{target_ordinal:04d}"
            identities.append({
                "target_id": target_id, "source_id": thermo_spec["source_id"], "source_class": "dissolution",
                "dataset_ordinal": dataset_ordinal, "source_point_ordinal": point_ordinal,
                "all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent": True,
            })
            targets.append({
                "target_id": target_id, "source_id": thermo_spec["source_id"], "source_class": "dissolution",
                "dataset_ordinal": dataset_ordinal, "source_point_ordinal": point_ordinal,
                "component_orgnums": list(components), "solute_orgnum": solute_orgnum, "solvent_orgnums": list(solvent_orgnums),
                "complete_component_records": [compounds[number] for number in components],
                "source_state": "separated-solute-and-solvent", "destination_state": "condition-bound-saturated-liquid-solution",
                "solubility_mole_fraction_external_inscription": property_values[1]["nPropValue"],
                "solubility_uncertainty_external_inscription": property_values[1].get("CombinedUncertainty", {}).get("nCombExpandUncertValue"),
                "variable_external_inscriptions": {str(number): value["nVarValue"] for number, value in variable_values.items()},
                "pressure_constraint_external_inscription": dataset["Constraint"][0]["nConstraintValue"],
                "complete_point_record": point, "complete_property_metadata": dataset["Property"],
                "complete_variable_metadata": dataset["Variable"], "complete_constraint_metadata": dataset["Constraint"],
                "complete_phase_metadata": dataset["PhaseID"],
            })
            dataset_target_ids.append(target_id)
            target_ordinal += 1
        dataset_summaries.append({
            "dataset_ordinal": dataset_ordinal, "component_orgnums": list(components),
            "solute_orgnum": solute_orgnum, "solvent_orgnums": list(solvent_orgnums),
            "point_count": len(dataset_target_ids), "target_ids_in_source_order": dataset_target_ids,
        })
    dissolution_count = target_ordinal - 1
    if len(source["Compound"]) != 7 or len(source["PureOrMixtureData"]) != 7 or dissolution_count != 157:
        raise ValueError("THERMO-015 complete NIST solubility census changed")
    source_summaries.append({
        "source_id": thermo_spec["source_id"], "source_class": "dissolution", "doi": thermo_spec["doi"],
        "raw_path": str(thermo_raw_path.relative_to(ROOT)), "raw_hash": sha_file(thermo_raw_path),
        "landing_path": str(thermo_landing_path.relative_to(ROOT)), "landing_hash": sha_file(thermo_landing_path),
        "complete_compound_count": len(source["Compound"]), "complete_dataset_count": len(source["PureOrMixtureData"]),
        "complete_point_count": dissolution_count, "dataset_summaries": dataset_summaries,
        "all_direct_rows_and_complete_source_preserved": True,
        "reported_correlation_or_model_values_excluded_from_measurements": True,
    })

    class_counts = {name: sum(row["source_class"] == name for row in targets) for name in ("solvation", "dissolution")}
    if class_counts != {"solvation": 642, "dissolution": 157} or len(targets) != 799:
        raise ValueError("THERMO-015 complete two-surface target census changed")
    identity_doc = {
        "schema": "sft-v3-solvation-dissolution-target-identities/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities), "source_class_counts": class_counts,
        "all_compound_solute_solvent_state_condition_value_uncertainty_reference_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-solvation-dissolution-withheld-targets/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash, "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets), "source_class_counts": class_counts, "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-solvation-dissolution-primary-records/1",
        "prefetch_capture_spec_hash_before_executable_law_registration": SPEC_HASH,
        "observational_source_research_disclosed": True, "capture_rule": spec["capture_rule"],
        "complete_source_count": 2, "complete_target_count": len(targets), "source_class_counts": class_counts,
        "source_summaries": source_summaries, "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_642_FreeSolv_and_157_direct_NIST_rows_preserved": True,
        "calculated_or_correlated_companion_fields_used_as_measurements": False,
        "force_field_continuum_solvent_partition_activity_solubility_product_logarithm_correlation_regression_fit_selection_or_target_correction_used": False,
        "external_values_used_as_proof_parameters": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH, "class_counts": class_counts, "complete_target_count": len(targets),
        "identity_hash": identity_hash, "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH), "primary_hash": sha_file(PRIMARY_PATH),
        "source_hashes": [row["raw_hash"] for row in source_summaries],
        "landing_hashes": [row["landing_hash"] for row in source_summaries],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
