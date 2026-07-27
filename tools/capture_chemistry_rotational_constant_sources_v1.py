#!/usr/bin/env python3
"""Capture the complete official NIST CCCBDB rotational-constant surface for PROP-010."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from html.parser import HTMLParser
from http.cookiejar import CookieJar
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-010-rotational-constant-v1"
LIST_SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-species-list.html"
CHOICE_SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-rotational-choice-surface.html"
SNAPSHOT_PATH = SNAPSHOT_DIR / "nist-cccbdb-complete-rotational-constant-surface.html"
PRIMARY_PATH = SNAPSHOT_DIR / "rotational-constant-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/rotational_constant_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/rotational_constant_withheld_targets_v1.json"

BASE_URL = "https://cccbdb.nist.gov/"
LIST_URL = BASE_URL + "listallx.asp"
FORM_URL = BASE_URL + "xp1x.asp?prop=5"
FORM_POST_URL = BASE_URL + "getformx.asp"
CHOICE_POST_URL = BASE_URL + "fixchoicex.asp"
USER_AGENT = "Ernos-Labs-SFT-v3-source-custodian/1"


class CellRows(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_cell = False
        self.cell_parts: list[str] = []
        self.cell_link = ""
        self.current: list[tuple[str, str]] = []
        self.rows: list[tuple[tuple[str, str], ...]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        lowered = tag.casefold()
        if lowered == "td":
            self.in_cell = True
            self.cell_parts = []
            self.cell_link = ""
        elif lowered == "a" and self.in_cell:
            self.cell_link = dict(attrs).get("href", "")
        elif lowered == "input" and self.in_cell:
            attributes = dict(attrs)
            if attributes.get("name", "").casefold() == "choice":
                self.cell_link = "choice:" + attributes.get("value", "")

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.casefold()
        if lowered == "td" and self.in_cell:
            self.current.append((" ".join("".join(self.cell_parts).split()), self.cell_link))
            self.in_cell = False
        elif lowered == "tr":
            if self.current:
                self.rows.append(tuple(self.current))
            self.current = []


def open_bytes(opener, request: Request, timeout: int) -> bytes:
    for attempt in range(3):
        try:
            with opener.open(request, timeout=timeout) as response:
                return response.read()
        except HTTPError as exc:
            if exc.code != 429 or attempt == 2:
                raise
            time.sleep(20 * (attempt + 1))
    raise RuntimeError("unreachable source-retry boundary")


def get(opener, url: str, referer: str | None = None) -> bytes:
    headers = {"User-Agent": USER_AGENT}
    if referer:
        headers["Referer"] = referer
    return open_bytes(opener, Request(url, headers=headers), 120)


def post(opener, url: str, fields: tuple[tuple[str, str], ...], referer: str) -> bytes:
    request = Request(
        url,
        data=urlencode(fields).encode("ascii"),
        headers={"User-Agent": USER_AGENT, "Referer": referer, "Content-Type": "application/x-www-form-urlencoded"},
    )
    return open_bytes(opener, request, 240)


def formula_key(formula: str) -> tuple[tuple[tuple[str, int], ...], int]:
    match = re.fullmatch(r"(.*?)([+-]*)", formula)
    if match is None:
        raise RuntimeError(f"unreadable NIST formula: {formula}")
    body, suffix = match.groups()
    charge = suffix.count("+") - suffix.count("-")
    body = body.replace("=", "")
    # The official list contains one literal ``CHFCHClz`` cis-marker typo;
    # the paired E/Z entries share composition and the query returns both.
    if body == "CHFCHClz":
        body = "CHFCHCl"
    tokens = re.findall(r"[A-Z][a-z]?|[()]|[0-9]+", body)
    if "".join(tokens) != body:
        raise RuntimeError(f"unsupported NIST formula grammar: {formula}")
    stack: list[dict[str, int]] = [{}]
    ordinal = 0
    while ordinal < len(tokens):
        token = tokens[ordinal]
        if token == "(":
            stack.append({})
            ordinal += 1
            continue
        if token == ")":
            if len(stack) == 1:
                raise RuntimeError(f"unbalanced NIST formula: {formula}")
            group = stack.pop()
            ordinal += 1
            has_multiplier = ordinal < len(tokens) and tokens[ordinal].isdigit()
            multiplier = int(tokens[ordinal]) if has_multiplier else 1
            if has_multiplier:
                ordinal += 1
            for element, count in group.items():
                stack[-1][element] = stack[-1].get(element, 0) + count * multiplier
            continue
        if token.isdigit():
            raise RuntimeError(f"detached count in NIST formula: {formula}")
        ordinal += 1
        has_multiplier = ordinal < len(tokens) and tokens[ordinal].isdigit()
        multiplier = int(tokens[ordinal]) if has_multiplier else 1
        if has_multiplier:
            ordinal += 1
        stack[-1][token] = stack[-1].get(token, 0) + multiplier
    if len(stack) != 1 or not stack[0]:
        raise RuntimeError(f"unbalanced or empty NIST formula: {formula}")
    return tuple(sorted(stack[0].items())), charge


def query_formula(formula: str) -> str:
    match = re.fullmatch(r"(.*?)([+-]*)", formula)
    if match is None:
        raise RuntimeError(f"unreadable NIST formula query: {formula}")
    body, suffix = match.groups()
    body = body.replace("=", "")
    if body == "CHFCHClz":
        body = "CHFCHCl"
    return body + suffix


def complete_formula_query(list_source: bytes) -> tuple[tuple[dict[str, object], ...], tuple[str, ...]]:
    parser = CellRows()
    parser.feed(list_source.decode("utf-8", errors="replace"))
    entries: list[dict[str, object]] = []
    query_tokens: list[str] = []
    seen_keys: set[tuple[tuple[str, int], ...]] = set()
    for row in parser.rows:
        for ordinal, (name, link) in enumerate(row):
            if "alldata2x.asp?" not in link or ordinal == 0:
                continue
            formula = row[ordinal - 1][0]
            query = parse_qs(urlparse(link).query)
            casno = str(query.get("casno", [""])[0])
            charge_text = str(query.get("charge", [""])[0])
            if not formula or not casno.isdigit() or not re.fullmatch(r"-?[0-9]+", charge_text):
                raise RuntimeError("NIST complete species-list identity changed")
            charge = int(charge_text)
            key = formula_key(formula)
            if key[1] != charge:
                raise RuntimeError(f"NIST formula/link charge disagreement: {formula}, {charge_text}")
            token = query_formula(formula)
            entries.append({
                "species_list_ordinal": len(entries) + 1,
                "formula": formula,
                "name": name,
                "cas_registry_digits": casno,
                "external_charge_inscription": charge_text,
                "query_token": token,
                "source_locator": link,
            })
            composition_key = key[0]
            if composition_key not in seen_keys:
                seen_keys.add(composition_key)
                query_tokens.append(token)
    if len(entries) < 2000 or len({row["source_locator"] for row in entries}) != len(entries):
        raise RuntimeError(f"NIST complete species-list boundary changed: {len(entries)}")
    return tuple(entries), tuple(query_tokens)


def choice_rows(source: bytes) -> tuple[dict[str, str], ...]:
    parser = CellRows()
    parser.feed(source.decode("utf-8", errors="replace"))
    resolved: list[dict[str, str]] = []
    for row in parser.rows:
        if len(row) != 9 or not row[1][1].startswith("choice:"):
            continue
        ordinal, checkbox, formula, charge, state, configuration, name, displayed_cas, _sketch = row
        casno = checkbox[1].removeprefix("choice:")
        if (
            not ordinal[0].isdigit()
            or not casno.isdigit()
            or displayed_cas[0] != casno
            or not re.fullmatch(r"-?[0-9]+", charge[0])
        ):
            raise RuntimeError("NIST rotational choice identity changed")
        resolved.append({
            "choice_ordinal": ordinal[0],
            "cas_registry_digits": casno,
            "formula": formula[0],
            "external_charge_inscription": charge[0],
            "state_label": state[0] if state[0] else "source-absent-state-label",
            "configuration_label": configuration[0] if configuration[0] else "source-absent-configuration-label",
            "name": name[0],
        })
    return tuple(resolved)


def pair(inscription: str) -> dict[str, int]:
    value = Fraction(inscription)
    return {"numerator": value.numerator, "denominator": value.denominator}


def rotational_rows(source: bytes, preceding_molecular_rows: int = 0) -> tuple[dict[str, object], ...]:
    text = source.decode("utf-8", errors="replace")
    if "Experimental values of Rotational Constants" not in text or "<TH>A</TH>" not in text or "<TH>B</TH>" not in text or "<TH>C</TH>" not in text:
        raise RuntimeError("NIST rotational-constant result boundary changed")
    parser = CellRows()
    parser.feed(text)
    records: list[dict[str, object]] = []
    numeric = re.compile(r"[0-9]+(?:\.[0-9]+)?")
    for row in parser.rows:
        cells = tuple(cell[0] for cell in row)
        if len(cells) != 6:
            continue
        name, charge, species, axis_a, axis_b, axis_c = cells
        if not name or not species or not re.fullmatch(r"-?[0-9]+", charge):
            continue
        axes = {"A": axis_a, "B": axis_b, "C": axis_c}
        if any(value and not numeric.fullmatch(value) for value in axes.values()):
            raise RuntimeError(f"non-exact rotational-constant inscription: {cells}")
        if any(value and Fraction(value) <= 0 for value in axes.values()):
            raise RuntimeError("rotational surface contains a numerical-null or negative axis record")
        row_ordinal = preceding_molecular_rows + len(records) // 3 + 1
        for axis_name, inscription in axes.items():
            target_id = f"NIST-CCCBDB-PROP-010-ROW-{row_ordinal:04d}-AXIS-{axis_name}"
            records.append({
                "target_id": target_id,
                "source_id": "NIST-CCCBDB-COMPLETE-ROTATIONAL-CONSTANT-SURFACE",
                "source_locator": f"xp2x complete all-species result, displayed molecular row {row_ordinal}, axis {axis_name}",
                "displayed_molecular_row": row_ordinal,
                "displayed_axis_ordinal": {"A": 1, "B": 2, "C": 3}[axis_name],
                "name": name,
                "species": species,
                "external_charge_inscription": charge,
                "axis_label": axis_name,
                "measurement_kind": "experimental-molecular-rotational-constant",
                "measurement_unit": "held-axis-recurrence-count-per-centimeter",
                "measurement_present": bool(inscription),
                "rotational_constant_inscription_cm_inverse": inscription if inscription else None,
                "exact_positive_axis_recurrence_ratio_per_centimeter": pair(inscription) if inscription else None,
                "external_measurement_absence": None if inscription else "structural-EmptyOne",
                "source_row_uncertainty": None,
                "source_row_uncertainty_absent": True,
            })
    if not records or len(records) % 3:
        raise RuntimeError("NIST rotational-constant rows are absent or incomplete")
    return tuple(records)


def main() -> None:
    list_source = get(build_opener(), LIST_URL)
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
            opener,
            FORM_POST_URL,
            (("formula", ",".join(tokens)), ("prop", "5"), ("submit1", "Submit")),
            FORM_URL,
        )
        choices = choice_rows(choice_source)
        requested_compositions = {formula_key(token)[0] for token in tokens}
        returned_compositions = {formula_key(row["formula"])[0] for row in choices}
        missing_query_tokens = tuple(token for token in tokens if formula_key(token)[0] not in returned_compositions)
        all_unreturned_query_tokens.extend(missing_query_tokens)
        if choices:
            selection_fields = tuple(("choice", row["cas_registry_digits"]) for row in choices) + (("submitselect", "Select"),)
            result_source = post(opener, CHOICE_POST_URL, selection_fields, BASE_URL + "choosex.asp")
            records = rotational_rows(result_source, len(all_records) // 3)
        else:
            result_source = b"<!-- NIST rotational property form returned no selectable row for this batch -->\n"
            records = ()
        marker = f"<!-- SFT PROP-010 NIST RETRIEVAL BATCH {batch_number:04d} -->\n".encode("ascii")
        choice_archive.extend((marker, choice_source, b"\n"))
        result_archive.extend((marker, result_source, b"\n"))
        all_choices.extend(choices)
        all_records.extend(records)
        batch_manifest.append({
            "batch_number": batch_number,
            "query_tokens": tokens,
            "listed_composition_without_returned_choice_tokens": missing_query_tokens,
            "choice_count": len(choices),
            "result_molecular_row_count": len(records) // 3,
            "choice_without_returned_property_row_floor_count": max(len(choices) - len(records) // 3, 0),
            "server_expanded_charge_or_state_row_count": max(len(records) // 3 - len(choices), 0),
            "choice_response_sha256": "sha256:" + hashlib.sha256(choice_source).hexdigest(),
            "result_response_sha256": "sha256:" + hashlib.sha256(result_source).hexdigest(),
        })
        if start + batch_size < len(query_tokens):
            time.sleep(8)

    choice_identities = {
        (
            row["cas_registry_digits"], row["external_charge_inscription"], row["state_label"],
            row["configuration_label"], row["name"],
        )
        for row in all_choices
    }
    if len(choice_identities) != len(all_choices):
        raise RuntimeError("NIST batched rotational choice surface duplicated a source identity")
    records = tuple(all_records)
    choice_source = b"".join(choice_archive)
    result_source = b"".join(result_archive)

    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    LIST_SNAPSHOT_PATH.write_bytes(list_source)
    CHOICE_SNAPSHOT_PATH.write_bytes(choice_source)
    SNAPSHOT_PATH.write_bytes(result_source)

    identities = []
    for row in records:
        identities.append({
            key: row[key]
            for key in (
                "target_id", "source_id", "source_locator", "displayed_molecular_row",
                "displayed_axis_ordinal", "name", "species", "external_charge_inscription",
                "axis_label", "measurement_kind", "measurement_unit", "source_row_uncertainty_absent",
            )
        })
        identities[-1]["target_value_absent"] = True

    molecular_rows = len(records) // 3
    measured_axes = sum(row["measurement_present"] for row in records)
    absent_axes = len(records) - measured_axes
    selection_boundary = (
        "every unique elemental-composition query generated from every row of the frozen official NIST CCCBDB "
        "complete species list; every returned choice selected; every server-expanded charge/state molecular row "
        "and all three A/B/C axis cells preserved in source order"
    )
    primary = {
        "schema": "sft-v3-nist-cccbdb-rotational-constant-primary-records/1",
        "list_source_url": LIST_URL,
        "form_source_url": FORM_URL,
        "complete_listed_species_count": len(list_entries),
        "complete_unique_formula_composition_query_count": len(query_tokens),
        "complete_returned_charge_state_choice_count": len(all_choices),
        "complete_listed_composition_without_returned_choice_count": len(all_unreturned_query_tokens),
        "complete_listed_composition_without_returned_choice_tokens": all_unreturned_query_tokens,
        "complete_displayed_molecular_row_count": molecular_rows,
        "complete_displayed_axis_cell_count": len(records),
        "experimental_measurement_present_count": measured_axes,
        "experimental_measurement_absent_count": absent_axes,
        "all_rows_and_axis_absences_preserved": True,
        "selection_boundary": selection_boundary,
        "retrieval_batch_size": batch_size,
        "retrieval_batches": batch_manifest,
        "complete_species_list": list_entries,
        "rows": records,
    }
    identity = {
        "schema": "sft-v3-rotational-constant-identities/1",
        "complete_displayed_molecular_row_count": molecular_rows,
        "complete_row_count": len(records),
        "all_rotational_constant_values_absent": True,
        "selection_boundary": selection_boundary,
        "rows": identities,
    }
    targets = {
        "schema": "sft-v3-rotational-constant-withheld-measurements/1",
        "complete_displayed_molecular_row_count": molecular_rows,
        "complete_row_count": len(records),
        "release_requires_prediction_seal": True,
        "all_rows_and_axis_absences_preserved": True,
        "all_values_are_exact_positive_axis_recurrence_ratios_or_structural_absence": True,
        "rows": records,
    }
    PRIMARY_PATH.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    IDENTITY_PATH.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGET_PATH.write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "listed_species": len(list_entries),
        "unique_formula_composition_queries": len(query_tokens),
        "returned_charge_state_choices": len(all_choices),
        "listed_compositions_without_returned_choice": len(all_unreturned_query_tokens),
        "displayed_molecular_rows": molecular_rows,
        "displayed_axis_cells": len(records),
        "measurement_present_axis_cells": measured_axes,
        "measurement_absent_axis_cells": absent_axes,
        "minimum_inscription": str(min(Fraction(row["rotational_constant_inscription_cm_inverse"]) for row in records if row["measurement_present"])),
        "maximum_inscription": str(max(Fraction(row["rotational_constant_inscription_cm_inverse"]) for row in records if row["measurement_present"])),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PROP-010 source capture halted: {exc}", file=sys.stderr)
        raise
