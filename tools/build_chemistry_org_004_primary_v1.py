#!/usr/bin/env python3
"""Open and preserve every ORG-004 source surface after the prediction seal."""

from __future__ import annotations

from fractions import Fraction
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


IDENTITY = ROOT / "experiments/external_sources/chemistry/org_004_target_identities_v1.json"
IDENTITY_HASH = "sha256:fcc870b511bcd2da94f26b6a9c8eed77ad9c05be3fce6a15869d4c1d6e0c437d"
PREDICTION = ROOT / "experiments/sealed_predictions/chemistry_org_004_antiaromatic_nonaromatic_pre_source.json"
PREDICTION_FILE_HASH = "sha256:ec19a1a56f5ffe3dd2759f4d82fb845b1ee111cc72dda9d04e0d582507bbe768"
PREDICTION_PAYLOAD_HASH = "sha256:df89cfe1ebaf37dc299b1679799730bc40ecbf0d0ef4d27d842687b7163a0aa9"
FAMILY_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:d542adb23900f765fcd0205afae8a666813af160881bb70b0676637b090b4acc"
TARGET = ROOT / "experiments/external_sources/chemistry/org_004_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/org-004-primary-records-v1.json"


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
    start = re.search(r"<h1[^>]*>Experimental data for", raw, flags=re.I)
    if not start:
        raise ValueError("registered CCCBDB experimental-data heading absent")
    section = raw[start.start():]
    heading_match = re.search(r"<h1[^>]*>(.*?)</h1>", section, flags=re.I | re.S)
    if not heading_match:
        raise ValueError("registered CCCBDB experimental-data identity absent")
    tables = parse_tables(section)
    if not tables:
        raise ValueError("registered CCCBDB experimental-data tables absent")
    return {
        "returned_experimental_data_heading": text_only(heading_match.group(1)),
        "complete_experimental_data_tables": tables,
        "complete_table_count": len(tables),
        "complete_row_count": sum(len(table) for table in tables),
    }


def rows_with_first_cell(surface: dict, label: str) -> list[list[str]]:
    tables = surface.get("complete_experimental_data_tables") or surface.get("complete_gas_thermochemistry_tables")
    return [row for table in tables for row in table if row and row[0] == label]


def table_with_header(surface: dict, header: tuple[str, ...]) -> list[list[str]]:
    tables = surface.get("complete_experimental_data_tables") or surface.get("complete_gas_thermochemistry_tables")
    matches = [table for table in tables if table and tuple(table[0][: len(header)]) == header]
    if len(matches) != 1:
        raise ValueError(f"registered table cardinality changed: {header}")
    return matches[0]


def positive_hundredths(value: str) -> int:
    whole, part = value.split(".")
    if len(part) != 2 or not whole.isdigit() or not part.isdigit():
        raise ValueError(f"external inscription is not exact positive hundredths: {value}")
    result = int(whole) * 100 + int(part)
    if result < 1:
        raise ValueError("external magnitude must remain positive")
    return result


def exact_fraction(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    if TARGET.exists() or PRIMARY.exists():
        raise SystemExit("ORG-004 post-seal target surface already exists; preserved without replay")
    if (
        hash_file(IDENTITY) != IDENTITY_HASH
        or hash_file(PREDICTION) != PREDICTION_FILE_HASH
        or hash_file(FAMILY_INVENTORY) != FAMILY_INVENTORY_HASH
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 identity, prediction or family inventory changed")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    claimed = prediction.pop("sealed_payload_hash", None)
    if claimed != PREDICTION_PAYLOAD_HASH or sha256_identity(prediction) != PREDICTION_PAYLOAD_HASH:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 prediction seal changed")
    identity_document = json.loads(IDENTITY.read_text(encoding="utf-8"))
    identity = identity_document.get("rows", [])
    if (
        identity_document.get("complete_registered_target_count") != 5
        or identity_document.get("development_observed_target_count") != 3
        or identity_document.get("outcome_unopened_blind_target_count") != 2
        or identity_document.get(
            "target_definitions_returned_names_geometry_symmetry_tables_values_signs_uncertainties_outcomes_presence_flags_or_payload_hashes_present"
        ) is not False
        or len(identity) != 5
    ):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 identity census changed")
    forbidden = {
        "definition", "note", "table", "value", "sign", "uncertainty", "outcome",
        "source_outcome", "presence", "target_payload_hash",
    }
    if any(forbidden.intersection(row) for row in identity):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 identity boundary contains an outcome")

    released = []
    by_role = {}
    for item in identity:
        path = ROOT / item["snapshot_path"]
        expected_hash = item["snapshot_sha256"]
        if hash_file(path) != expected_hash:
            raise SystemExit(f"VOID_INVALID_HALTED: ORG-004 source changed: {path}")
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
        row = {**item, "opened_snapshot_path": item["snapshot_path"], "opened_snapshot_sha256": expected_hash}
        row["source_outcome"] = outcome
        row["target_payload_hash"] = sha256_identity((item["target_id"], item["source_record_role"], outcome))
        released.append(row)
        by_role[item["source_record_role"]] = outcome

    aromatic_term = by_role["complete-aromatic-comparative-term-record"]["complete_term_record"]
    antiaromatic_term = by_role["complete-antiaromaticity-term-record"]["complete_term_record"]
    benzene = by_role["complete-development-benzene-thermochemistry-surface"]
    cyclobutadiene = by_role["complete-blind-CAS-1120-53-2-neutral-experimental-surface"]
    cyclooctatetraene = by_role["complete-blind-CAS-629-20-9-neutral-experimental-surface"]

    aromatic_text = json.dumps(aromatic_term, sort_keys=True, ensure_ascii=False)
    antiaromatic_text = json.dumps(antiaromatic_term, sort_keys=True, ensure_ascii=False)
    benzene_hfg = [
        row for table in benzene["complete_gas_thermochemistry_tables"] for row in table
        if row and row[0] == "Δ f H° gas" and row[1] == "82.93 ± 0.50"
    ]
    cot_hfg = rows_with_first_cell(cyclooctatetraene, "Hfg(298.15K)")
    cbd_hfg = rows_with_first_cell(cyclobutadiene, "Hfg(298.15K)")
    cbd_ie = table_with_header(cyclobutadiene, ("Ionization Energy", "I.E. unc."))
    cbd_state = table_with_header(
        cyclobutadiene,
        ("State", "Config", "State description", "Conf description", "Exp. min.", "Dipole (Debye)"),
    )
    cbd_conformation = table_with_header(cyclobutadiene, ("State", "Conformation"))
    cot_conformation = table_with_header(cyclooctatetraene, ("State", "Conformation"))
    cot_geometry = table_with_header(cyclooctatetraene, ("Description", "Value", "unc.", "Connectivity"))
    cot_coordinates = table_with_header(cyclooctatetraene, ("Atom", "x (Å)", "y (Å)", "z (Å)"))
    if len(benzene_hfg) != 1 or len(cot_hfg) != 1 or len(cbd_hfg) != 0:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 registered energy presence/absence surface changed")
    if len(cot_hfg[0]) < 4 or cot_hfg[0][1:4] != ["297.60", "1.40", "kJ mol -1"]:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 cyclooctatetraene energy row changed")
    if len(cbd_ie) < 2 or cbd_ie[1][:2] != ["8.160", "0.030"]:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 cyclobutadiene energy row changed")
    if not any(row[3:5] == ["D 2h", "True"] for row in cbd_state[2:]):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 cyclobutadiene true-minimum row absent")
    if not any(row[3:5] == ["D 4h", "False"] for row in cbd_state[2:]):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 cyclobutadiene false-square control absent")
    if cbd_conformation[1][1] != "D2H" or cot_conformation[1][1] != "D2D":
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 blind conformation vector changed")
    geometry_rows = {row[0] + "-" + row[1]: row for row in cot_geometry[1:]}
    if "rCC-1.337" not in geometry_rows or "rCC-1.470" not in geometry_rows:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 bond-alternation vector absent")
    carbon_z = [row[3] for row in cot_coordinates[1:] if row[0].startswith("C")]
    if not any(value.startswith("-") for value in carbon_z) or not any(not value.startswith("-") for value in carbon_z):
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 out-of-plane coordinate vector absent")

    benzene_value = positive_hundredths("82.93")
    benzene_uncertainty = positive_hundredths("0.50")
    cot_value = positive_hundredths(cot_hfg[0][1])
    cot_uncertainty = positive_hundredths(cot_hfg[0][2])
    benzene_per_ch = Fraction(benzene_value, 6)
    cot_per_ch = Fraction(cot_value, 8)
    exact_gap = cot_per_ch - benzene_per_ch
    exact_uncertainty = Fraction(benzene_uncertainty, 6) + Fraction(cot_uncertainty, 8)
    exact_lower = exact_gap - exact_uncertainty
    if exact_gap <= exact_uncertainty or exact_lower <= 0:
        raise SystemExit("VOID_INVALID_HALTED: ORG-004 comparative repeated-unit energy relation adverse")

    analysis = {
        "complete_target_count": len(released),
        "complete_source_count": len({row["source_id"] for row in released}),
        "development_observed_target_count": sum("development-observed" in row["custody_class"] for row in released),
        "outcome_unopened_blind_target_count": sum("outcome-unopened" in row["custody_class"] for row in released),
        "aromatic_closed_cycle_and_stability_surface_present": "cyclically conjugated molecular entity" in aromatic_text and "stability" in aromatic_text,
        "antiaromatic_reduced_stability_surface_present": "reduction (in some cases, loss) of thermodynamic stability" in antiaromatic_text,
        "antiaromatic_bond_alternation_surface_present": "alternation of bond lengths" in antiaromatic_text,
        "blind_returned_species": {
            "CAS-1120-53-2": cyclobutadiene["returned_experimental_data_heading"],
            "CAS-629-20-9": cyclooctatetraene["returned_experimental_data_heading"],
        },
        "blind_conformation_external_strings": {
            "cyclobutadiene": cbd_conformation[1][1],
            "cyclooctatetraene": cot_conformation[1][1],
        },
        "blind_cyclobutadiene_true_minimum_external_string": "D 2h",
        "blind_cyclobutadiene_false_square_control_external_string": "D 4h",
        "blind_cyclooctatetraene_alternating_cc_bond_external_strings_angstrom": ["1.337", "1.470"],
        "blind_cyclooctatetraene_opposed_z_coordinate_signs_present": True,
        "blind_cyclobutadiene_hfg_298_row_count": len(cbd_hfg),
        "blind_cyclobutadiene_hfg_absence_preserved": len(cbd_hfg) == 0,
        "blind_cyclobutadiene_ionization_energy_external_strings_ev": ["8.160", "0.030"],
        "development_benzene_hfg_external_strings_kj_per_mol": ["82.93", "0.50"],
        "blind_cyclooctatetraene_hfg_external_strings_kj_per_mol": ["297.60", "1.40"],
        "exact_repeated_ch_unit_hfg_gap_hundredths_kj_per_mol": exact_fraction(exact_gap),
        "exact_repeated_ch_unit_uncertainty_hundredths_kj_per_mol": exact_fraction(exact_uncertainty),
        "exact_repeated_ch_unit_lower_gap_hundredths_kj_per_mol": exact_fraction(exact_lower),
        "exact_repeated_ch_unit_hfg_gap_kj_per_mol": exact_fraction(exact_gap / 100),
        "exact_repeated_ch_unit_uncertainty_kj_per_mol": exact_fraction(exact_uncertainty / 100),
        "exact_repeated_ch_unit_lower_gap_kj_per_mol": exact_fraction(exact_lower / 100),
        "blind_cccbdb_complete_table_counts": {
            "cyclobutadiene": cyclobutadiene["complete_table_count"],
            "cyclooctatetraene": cyclooctatetraene["complete_table_count"],
        },
        "blind_cccbdb_complete_row_counts": {
            "cyclobutadiene": cyclobutadiene["complete_row_count"],
            "cyclooctatetraene": cyclooctatetraene["complete_row_count"],
        },
        "development_webbook_complete_table_count": benzene["complete_table_count"],
        "development_webbook_complete_row_count": benzene["complete_row_count"],
        "all_signed_and_absent_external_inscriptions_preserved_downstream": True,
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "complete_target_vector_hash": sha256_identity(tuple((row["target_id"], row["source_outcome"]) for row in released)),
    }
    target = {
        "schema": "sft-v3-postseal-complete-target-vector/1",
        "claim_id": identity_document["claim_id"],
        "identity_registry": (str(IDENTITY.relative_to(ROOT)), IDENTITY_HASH),
        "prediction_seal": (str(PREDICTION.relative_to(ROOT)), PREDICTION_PAYLOAD_HASH),
        "family_source_inventory": (str(FAMILY_INVENTORY.relative_to(ROOT)), FAMILY_INVENTORY_HASH),
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(released),
        "all_favourable_adverse_absent_scope_and_unresolved_rows_preserved": True,
        "rows": released,
    }
    write_json(TARGET, target)
    primary = {
        "schema": "sft-v3-postseal-primary-analysis/1",
        "claim_id": identity_document["claim_id"],
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
