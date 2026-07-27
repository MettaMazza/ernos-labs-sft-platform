#!/usr/bin/env python3
"""Open and preserve every ORG-003 source surface after the prediction seal."""

from __future__ import annotations

import html
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_003_target_identities_v1.json"
IDENTITY_HASH = "sha256:c4ad884ce29b88a63362ac2c32aac3f267f1b3c66626460f5572f851c7057cf7"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_003_aromatic_recurrence_stability_pre_source.json"
PREDICTION_PAYLOAD_HASH = "sha256:eb06a1bd1cf7b4555eb08dc6c7c81dd27c5795fe035a24a53d5b282a4fef9038"
BLIND_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-003-blind-cccbdb-v1/source-inventory-v1.json"
BLIND_INVENTORY_HASH = "sha256:75d18e740c853cbaa6d28445bd49b127f023b2f836c1e8afc75a426899542ab7"
TARGET = ROOT / "experiments/external_sources/chemistry/org_003_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-003-primary-records-v1.json"


def text_only(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def parse_tables(raw: str) -> list[list[list[str]]]:
    tables = []
    for table in re.findall(r"<table\b[^>]*>(.*?)</table>", raw, flags=re.I | re.S):
        rows = []
        for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", table, flags=re.I | re.S):
            cells = [
                text_only(cell)
                for cell in re.findall(r"<(?:td|th)\b[^>]*>(.*?)</(?:td|th)>", row, flags=re.I | re.S)
            ]
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def webbook_surface(raw: str) -> dict:
    start = re.search(r'<h2\s+id="Thermo-Gas"[^>]*>', raw, flags=re.I)
    if not start:
        raise ValueError("registered WebBook gas thermochemistry section absent")
    remainder = raw[start.start():]
    end = re.search(r"<hr\b", remainder, flags=re.I)
    section = remainder[: end.start()] if end else remainder
    tables = parse_tables(section)
    if not tables:
        raise ValueError("registered WebBook gas thermochemistry tables absent")
    return {
        "complete_gas_thermochemistry_tables": tables,
        "complete_table_count": len(tables),
        "complete_row_count": sum(len(table) for table in tables),
    }


def cccbdb_surface(raw: str) -> dict:
    start = re.search(r"<h1>Experimental data for", raw, flags=re.I)
    if not start:
        raise ValueError("registered CCCBDB experimental-data heading absent")
    section = raw[start.start():]
    tables = parse_tables(section)
    if not tables:
        raise ValueError("registered CCCBDB experimental-data tables absent")
    return {
        "complete_experimental_data_tables": tables,
        "complete_table_count": len(tables),
        "complete_row_count": sum(len(table) for table in tables),
    }


def find_property(surface: dict, property_label: str) -> tuple[str, str, str]:
    matches = []
    for table in surface["complete_experimental_data_tables"]:
        for row in table:
            if row and row[0] == property_label:
                matches.append(row)
    if len(matches) != 1 or len(matches[0]) < 4:
        raise ValueError(f"registered CCCBDB property cardinality changed: {property_label}")
    row = matches[0]
    return row[1], row[2], row[3]


def directed_hundredths(value: str) -> tuple[str, int]:
    stripped = value.strip()
    direction = "below-reference" if stripped.startswith("-") else "above-reference"
    magnitude = stripped[1:] if stripped.startswith("-") else stripped
    whole, part = magnitude.split(".")
    if len(part) != 2 or not whole.isdigit() or not part.isdigit():
        raise ValueError(f"external magnitude is not an exact hundredth inscription: {value}")
    numerator = int(whole) * 100 + int(part)
    if numerator < 1:
        raise ValueError("external magnitude must be positive")
    return direction, numerator


def hundredths_string(numerator: int) -> str:
    if numerator < 1:
        raise ValueError("derived external magnitude must remain positive")
    return f"{numerator // 100}.{numerator % 100:02d}"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if TARGET.exists() or PRIMARY.exists():
        raise SystemExit("ORG-003 post-seal target surface already exists; preserved without replay")
    if hash_file(IDENTITY) != IDENTITY_HASH or hash_file(BLIND_INVENTORY) != BLIND_INVENTORY_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 identity or blind inventory changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 prediction seal changed")
    identity = json.loads(IDENTITY.read_text(encoding="utf-8"))
    rows = identity.get("rows", [])
    if (
        identity.get("complete_registered_target_count") != 9
        or identity.get("outcome_unopened_blind_target_count") != 3
        or identity.get(
            "target_definitions_notes_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
        )
        is not False
        or len(rows) != 9
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 identity census changed")
    blind_inventory = json.loads(BLIND_INVENTORY.read_text(encoding="utf-8"))
    blind_by_id = {row["source_id"]: row for row in blind_inventory["rows"]}
    released = []
    by_role = {}
    for item in rows:
        if "snapshot_path" in item:
            path = ROOT / item["snapshot_path"]
            expected_hash = item["snapshot_sha256"]
        else:
            captured = blind_by_id.get(item["source_id"])
            if captured is None:
                raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind source missing")
            path = ROOT / captured["snapshot_path"]
            expected_hash = captured["snapshot_sha256"]
        if hash_file(path) != expected_hash:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-003 source changed: {path}")
        if item["authority"] == "IUPAC":
            outcome = {"complete_term_record": json.loads(path.read_text(encoding="utf-8"))["term"]}
        else:
            raw = path.read_text(encoding="utf-8", errors="replace")
            outcome = webbook_surface(raw) if "WEBBOOK" in item["source_id"] else cccbdb_surface(raw)
            outcome.update(
                {
                    "complete_snapshot_sha256": expected_hash,
                    "complete_snapshot_byte_count": path.stat().st_size,
                }
            )
        row = {**item, "opened_snapshot_path": str(path.relative_to(ROOT)), "opened_snapshot_sha256": expected_hash}
        row["source_outcome"] = outcome
        row["target_payload_hash"] = sha256_identity(
            (item["target_id"], item["source_record_role"], outcome)
        )
        released.append(row)
        by_role[item["source_record_role"]] = outcome

    blind_roles = (
        "complete-cccbdb-benzene-experimental-data-surface",
        "complete-cccbdb-cyclohexene-experimental-data-surface",
        "complete-cccbdb-cyclohexane-experimental-data-surface",
    )
    blind_values = {
        role: find_property(by_role[role], "Hfg(298.15K)") for role in blind_roles
    }
    benzene_direction, benzene = directed_hundredths(blind_values[blind_roles[0]][0])
    cyclohexene_direction, cyclohexene = directed_hundredths(blind_values[blind_roles[1]][0])
    cyclohexane_direction, cyclohexane = directed_hundredths(blind_values[blind_roles[2]][0])
    if (
        benzene_direction != "above-reference"
        or cyclohexene_direction != "below-reference"
        or cyclohexane_direction != "below-reference"
        or cyclohexane <= cyclohexene
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind directed magnitude relation adverse")
    isolated_hydrogenation = cyclohexane - cyclohexene
    cyclic_hydrogenation = cyclohexane + benzene
    localized_threefold = 3 * isolated_hydrogenation
    if localized_threefold <= cyclic_hydrogenation:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind recurrence stability relation adverse")
    stability_excess = localized_threefold - cyclic_hydrogenation
    uncertainty_values = {}
    for role, (_, uncertainty, _) in blind_values.items():
        _, uncertainty_values[role] = directed_hundredths(uncertainty)
    conservative_uncertainty = (
        3 * (uncertainty_values[blind_roles[1]] + uncertainty_values[blind_roles[2]])
        + uncertainty_values[blind_roles[0]]
        + uncertainty_values[blind_roles[2]]
    )
    if stability_excess <= conservative_uncertainty:
        raise SystemExit("VOID_INVALID_HALTED: ORG-003 blind stability excess does not clear uncertainty envelope")
    term_text = {
        role: json.dumps(by_role[role]["complete_term_record"], sort_keys=True, ensure_ascii=False)
        for role in (
            "complete-aromatic-term-record",
            "complete-aromaticity-term-record",
            "complete-resonance-energy-term-record",
        )
    }
    analysis = {
        "complete_target_count": len(released),
        "complete_source_count": len({row["source_id"] for row in released}),
        "development_observed_target_count": sum(
            row["custody_class"] == "family-development-observed-before-ORG-003-seal" for row in released
        ),
        "outcome_unopened_blind_target_count": sum(
            row["custody_class"].startswith("identity-only-outcome-unopened") for row in released
        ),
        "aromatic_cycle_stability_surface_present": "cyclically conjugated molecular entity" in term_text["complete-aromatic-term-record"] and "stability" in term_text["complete-aromatic-term-record"],
        "cyclic_delocalization_and_thermodynamic_stability_surface_present": "cyclic electron delocalization" in term_text["complete-aromaticity-term-record"] and "thermodynamic stability" in term_text["complete-aromaticity-term-record"],
        "resonance_energy_unobservable_estimate_boundary_present": "cannot be measured, but only estimated" in term_text["complete-resonance-energy-term-record"],
        "blind_hfg_298_external_strings": {
            "benzene": blind_values[blind_roles[0]][0],
            "cyclohexene": blind_values[blind_roles[1]][0],
            "cyclohexane": blind_values[blind_roles[2]][0],
        },
        "blind_hfg_298_uncertainty_external_strings": {
            "benzene": blind_values[blind_roles[0]][1],
            "cyclohexene": blind_values[blind_roles[1]][1],
            "cyclohexane": blind_values[blind_roles[2]][1],
        },
        "blind_hfg_298_unit_external_strings": {
            "benzene": blind_values[blind_roles[0]][2],
            "cyclohexene": blind_values[blind_roles[1]][2],
            "cyclohexane": blind_values[blind_roles[2]][2],
        },
        "blind_single_isolated_hydrogenation_magnitude_kj_per_mol": hundredths_string(isolated_hydrogenation),
        "blind_cyclic_threefold_hydrogenation_magnitude_kj_per_mol": hundredths_string(cyclic_hydrogenation),
        "blind_localized_threefold_reference_magnitude_kj_per_mol": hundredths_string(localized_threefold),
        "blind_recurrence_stability_excess_magnitude_kj_per_mol": hundredths_string(stability_excess),
        "blind_conservative_uncertainty_envelope_kj_per_mol": hundredths_string(conservative_uncertainty),
        "blind_stability_excess_lower_envelope_kj_per_mol": hundredths_string(stability_excess - conservative_uncertainty),
        "blind_cccbdb_complete_table_counts": {
            role: by_role[role]["complete_table_count"] for role in blind_roles
        },
        "blind_cccbdb_complete_row_counts": {
            role: by_role[role]["complete_row_count"] for role in blind_roles
        },
        "development_webbook_complete_table_counts": {
            role: by_role[role]["complete_table_count"]
            for role in (
                "complete-webbook-benzene-thermochemistry-surface",
                "complete-webbook-cyclohexene-thermochemistry-surface",
                "complete-webbook-cyclohexane-thermochemistry-surface",
            )
        },
        "development_webbook_complete_row_counts": {
            role: by_role[role]["complete_row_count"]
            for role in (
                "complete-webbook-benzene-thermochemistry-surface",
                "complete-webbook-cyclohexene-thermochemistry-surface",
                "complete-webbook-cyclohexane-thermochemistry-surface",
            )
        },
        "all_signed_and_absent_external_inscriptions_preserved_downstream": True,
        "all_rows_preserved": True,
        "blind_source_recapture_count": blind_inventory["source_recapture_count"],
        "complete_target_vector_hash": sha256_identity(
            tuple((row["target_id"], row["source_outcome"]) for row in released)
        ),
    }
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/1",
        "claim_id": identity["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "blind_source_inventory": (str(BLIND_INVENTORY.relative_to(ROOT)), BLIND_INVENTORY_HASH),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(released),
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "rows": released,
    }
    write_json(TARGET, target)
    primary = {
        "schema": "sft-v3-postseal-primary-analysis/1",
        "claim_id": identity["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "target_registry": (str(TARGET.relative_to(ROOT)), hash_file(TARGET)),
        "exact_postseal_analysis": analysis,
    }
    write_json(PRIMARY, primary)
    print(f"{TARGET.relative_to(ROOT)} {hash_file(TARGET)}")
    print(f"{PRIMARY.relative_to(ROOT)} {hash_file(PRIMARY)}")
    print(json.dumps(analysis, sort_keys=True))


if __name__ == "__main__":
    main()
