#!/usr/bin/env python3
"""Capture the complete official NIST CCCBDB formation-energy surface for PROP-013."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys
from http.cookiejar import CookieJar
from urllib.request import HTTPCookieProcessor, build_opener

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.capture_chemistry_rotational_constant_sources_v1 import (
    BASE_URL, CHOICE_POST_URL, FORM_POST_URL, LIST_URL, CellRows,
    choice_rows, complete_formula_query, formula_key, get, post,
)


SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-013-formation-energy-v1"
LIST_SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-species-list.html"
CHOICE_SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-formation-choice-surface.html"
SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-formation-energy-surface.html"
REFERENCE_SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-thermodynamic-reference-states.html"
PRIMARY_PATH = SNAPSHOT_DIR / "formation-energy-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/formation_energy_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/formation_energy_withheld_targets_v1.json"

FORM_URL = BASE_URL + "xp1x.asp?prop=1"
REFERENCE_URL = BASE_URL + "refstatex.asp"


def sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pair(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def formation_rows(source: bytes, preceding_molecular_rows: int = 0) -> tuple[dict[str, object], ...]:
    text = source.decode("utf-8", errors="replace")
    if "Experimental values of Enthalpy of formation" not in text or "<TH>hfg</TH>" not in text or "<TH>hfg 0K</TH>" not in text:
        raise RuntimeError("NIST formation-energy result boundary changed")
    parser = CellRows()
    parser.feed(text)
    records: list[dict[str, object]] = []
    numeric = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?")
    for row in parser.rows:
        cells = tuple(cell[0] for cell in row)
        if len(cells) != 5:
            continue
        name, charge, species, hfg_298, hfg_0 = cells
        if not name or not species or not re.fullmatch(r"-?[0-9]+", charge):
            continue
        if any(value and not numeric.fullmatch(value) for value in (hfg_298, hfg_0)):
            raise RuntimeError(f"non-exact formation-energy inscription: {cells}")
        molecular_row = preceding_molecular_rows + len(records) // 2 + 1
        for axis_ordinal, (temperature, inscription) in enumerate((("298.15-kelvin", hfg_298), ("source-0-kelvin-label", hfg_0)), start=1):
            target_id = f"NIST-CCCBDB-PROP-013-ROW-{molecular_row:04d}-REFERENCE-{axis_ordinal}"
            if inscription:
                external = Fraction(inscription)
                magnitude = abs(external)
                if external < 0:
                    orientation = "product-state-below-reference-state"
                elif external > 0:
                    orientation = "product-state-above-reference-state"
                else:
                    orientation = "product-and-reference-state-equal-structural-EmptyOne"
                native = {"structural_absence": "EmptyOne"} if magnitude == 0 else {
                    "exact_positive_magnitude_kJ_per_mol": pair(magnitude),
                    "external_state_orientation": orientation,
                }
            else:
                native = {"structural_absence": "EmptyOne", "source_measurement_absent": True}
            records.append({
                "target_id": target_id,
                "source_id": "NIST-CCCBDB-SRD-101-COMPLETE-EXPERIMENTAL-FORMATION-ENERGY",
                "source_locator": f"complete prop=1 result, displayed molecular row {molecular_row}, reference axis {axis_ordinal}",
                "displayed_molecular_row": molecular_row,
                "reference_axis_ordinal": axis_ordinal,
                "name": name,
                "species": species,
                "external_charge_inscription": charge,
                "temperature_reference_label": temperature,
                "measurement_kind": "experimental-gas-phase-enthalpy-of-formation",
                "measurement_unit": "kJ-per-mol",
                "source_value_present": bool(inscription),
                "source_value_inscription": inscription if inscription else None,
                "native_value": native,
            })
    if not records or len(records) % 2:
        raise RuntimeError("NIST formation-energy result rows are absent or incomplete")
    return tuple(records)


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    list_source = get(build_opener(), LIST_URL)
    reference_source = get(build_opener(), REFERENCE_URL)
    list_entries, query_tokens = complete_formula_query(list_source)
    batch_size = 200
    choice_archive: list[bytes] = []
    result_archive: list[bytes] = []
    all_choices: list[dict[str, str]] = []
    all_records: list[dict[str, object]] = []
    all_unreturned_query_tokens: list[str] = []
    batch_manifest: list[dict[str, object]] = []
    for start in range(0, len(query_tokens), batch_size):
        batch_number = len(batch_manifest) + 1
        tokens = query_tokens[start:start + batch_size]
        opener = build_opener(HTTPCookieProcessor(CookieJar()))
        get(opener, FORM_URL)
        choice_source = post(
            opener, FORM_POST_URL,
            (("formula", ",".join(tokens)), ("prop", "1"), ("submit1", "Submit")),
            FORM_URL,
        )
        choices = choice_rows(choice_source)
        returned_compositions = {formula_key(row["formula"])[0] for row in choices}
        missing_query_tokens = tuple(token for token in tokens if formula_key(token)[0] not in returned_compositions)
        all_unreturned_query_tokens.extend(missing_query_tokens)
        if choices:
            fields = tuple(("choice", row["cas_registry_digits"]) for row in choices) + (("submitselect", "Select"),)
            result_source = post(opener, CHOICE_POST_URL, fields, BASE_URL + "choosex.asp")
            records = formation_rows(result_source, len(all_records) // 2)
        else:
            result_source = b"<!-- NIST formation property form returned no selectable row for this batch -->\n"
            records = ()
        marker = f"<!-- SFT PROP-013 NIST RETRIEVAL BATCH {batch_number:04d} -->\n".encode("ascii")
        choice_archive.extend((marker, choice_source, b"\n"))
        result_archive.extend((marker, result_source, b"\n"))
        all_choices.extend(choices)
        all_records.extend(records)
        batch_manifest.append({
            "batch_number": batch_number,
            "query_tokens": tokens,
            "listed_composition_without_returned_choice_tokens": missing_query_tokens,
            "returned_choice_count": len(choices),
            "displayed_molecular_row_count": len(records) // 2,
        })
        print(f"batch {batch_number}: choices={len(choices)} molecular_rows={len(records)//2} missing={len(missing_query_tokens)}", flush=True)

    LIST_SNAPSHOT_PATH.write_bytes(list_source)
    CHOICE_SNAPSHOT_PATH.write_bytes(b"".join(choice_archive))
    SNAPSHOT_PATH.write_bytes(b"".join(result_archive))
    REFERENCE_SNAPSHOT_PATH.write_bytes(reference_source)
    if len(all_records) != len({row["target_id"] for row in all_records}):
        raise RuntimeError("NIST formation-energy targets are duplicated")
    present = sum(bool(row["source_value_present"]) for row in all_records)
    absent = len(all_records) - present
    product_below = sum(row["native_value"].get("external_state_orientation") == "product-state-below-reference-state" for row in all_records)
    product_above = sum(row["native_value"].get("external_state_orientation") == "product-state-above-reference-state" for row in all_records)
    equal = sum(row["native_value"].get("structural_absence") == "EmptyOne" and row["source_value_present"] for row in all_records)
    identities = [{
        key: row[key] for key in (
            "target_id", "source_id", "source_locator", "displayed_molecular_row", "reference_axis_ordinal",
            "name", "species", "external_charge_inscription", "temperature_reference_label",
            "measurement_kind", "measurement_unit",
        )
    } | {"target_value_absent": True} for row in all_records]
    targets = [{
        "target_id": row["target_id"],
        "source_value_present": row["source_value_present"],
        "source_value_inscription": row["source_value_inscription"],
        "native_value": row["native_value"],
    } for row in all_records]
    primary = {
        "schema": "sft-v3-nist-cccbdb-formation-energy-primary-records/1",
        "source_id": "NIST-CCCBDB-SRD-101-COMPLETE-EXPERIMENTAL-FORMATION-ENERGY",
        "complete_listed_species_count": len(list_entries),
        "complete_unique_formula_composition_query_count": len(query_tokens),
        "complete_returned_charge_state_choice_count": len(all_choices),
        "complete_listed_composition_without_returned_choice_count": len(all_unreturned_query_tokens),
        "complete_displayed_molecular_row_count": len(all_records) // 2,
        "complete_reference_axis_cell_count": len(all_records),
        "source_value_present_count": present,
        "source_value_absent_count": absent,
        "product_below_reference_count": product_below,
        "product_above_reference_count": product_above,
        "product_equal_reference_structural_EmptyOne_count": equal,
        "retrieval_batches": batch_manifest,
        "unreturned_query_tokens": all_unreturned_query_tokens,
        "thermodynamic_reference_state_source": {
            "source_url": REFERENCE_URL,
            "snapshot_path": str(REFERENCE_SNAPSHOT_PATH.relative_to(ROOT)),
            "snapshot_hash": sha256_bytes(reference_source),
        },
        "all_values_blanks_and_source_orientations_preserved": True,
        "rows": all_records,
    }
    write_json(PRIMARY_PATH, primary)
    write_json(IDENTITY_PATH, {
        "schema": "sft-v3-formation-energy-identities/1",
        "complete_target_count": len(identities),
        "all_formation_values_presence_flags_and_orientations_absent": True,
        "rows": identities,
    })
    write_json(TARGET_PATH, {
        "schema": "sft-v3-formation-energy-withheld-targets/1",
        "release_requires_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    })
    print(json.dumps({
        "list_hash": sha256_file(LIST_SNAPSHOT_PATH), "choice_hash": sha256_file(CHOICE_SNAPSHOT_PATH),
        "result_hash": sha256_file(SNAPSHOT_PATH), "reference_hash": sha256_file(REFERENCE_SNAPSHOT_PATH),
        "primary_hash": sha256_file(PRIMARY_PATH), "identity_hash": sha256_file(IDENTITY_PATH),
        "target_hash": sha256_file(TARGET_PATH), "molecular_rows": len(all_records)//2,
        "target_cells": len(all_records), "present": present, "absent": absent,
        "product_below": product_below, "product_above": product_above, "equal": equal,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
