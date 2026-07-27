#!/usr/bin/env python3
"""Capture the complete NIST CCCBDB molecular experimental-EA surface for PROP-008."""

from __future__ import annotations

from fractions import Fraction
import hashlib
from html import unescape
import json
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/prop-008-molecular-electron-affinity-v1"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_withheld_targets_v1.json"
PAGE_MANIFEST_PATH = ROOT / "experiments/external_sources/chemistry/molecular_electron_affinity_source_page_manifest_v1.json"
LIST_URL = "https://cccbdb.nist.gov/elecaff1x.asp"
GUIDE_URL = "https://webbook.nist.gov/chemistry/ion/"
DETAIL_URL = "https://cccbdb.nist.gov/elecaff2x.asp?casno={casno}"


ROW_PATTERN = re.compile(
    r"<tr>\s*<td>(.*?)</td>\s*<td><a\s+href=[\"']elecaff2x\.asp\?casno=([0-9]+)[\"']>(.*?)</a></td>\s*</tr>",
    re.IGNORECASE | re.DOTALL,
)
VALUE_PATTERN = re.compile(
    r"Experimental Electron Affinity is\s*([+-]?)([0-9]+(?:\.[0-9]+)?)"
    r"(?:\s*(?:&plusmn;|±)\s*([0-9]+(?:\.[0-9]+)?))?\s*eV",
    re.IGNORECASE,
)
TAG_PATTERN = re.compile(r"<[^>]+>")


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-custodian/1"})
    last: Exception | None = None
    for attempt in range(1, 7):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last = exc
            if attempt < 6:
                if isinstance(exc, HTTPError) and exc.code == 429:
                    retry_after = exc.headers.get("Retry-After")
                    declared = int(retry_after) if retry_after and retry_after.isdigit() else 60
                    delay = max(declared, 60)
                    time.sleep(min(delay, 60))
                else:
                    time.sleep(min(2 * attempt, 10))
    raise RuntimeError(f"unable to capture authoritative source {url}: {last}")


def clean_html(fragment: str) -> str:
    fragment = re.sub(r"<sub>(.*?)</sub>", r"\1", fragment, flags=re.IGNORECASE | re.DOTALL)
    return " ".join(unescape(TAG_PATTERN.sub("", fragment)).split())


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return text or "species"


def is_atomic_formula(formula: str) -> bool:
    """A single element carrier is atomic; every multi-atom formula is molecular."""

    return re.fullmatch(r"(?:[A-Z][a-z]?|D|T)", formula) is not None


def decimal_pair(inscription: str) -> dict[str, int]:
    value = Fraction(inscription)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def display_enclosure(inscription: str) -> tuple[dict[str, int], dict[str, int]]:
    value = Fraction(inscription)
    places = len(inscription.partition(".")[2])
    half_unit = Fraction(1, 2 * (10 ** places))
    lower, upper = value - half_unit, value + half_unit
    if lower <= 0:
        raise ValueError("positive displayed magnitude did not admit a positive rounding enclosure")
    return (
        {"numerator": lower.numerator, "denominator": lower.denominator},
        {"numerator": upper.numerator, "denominator": upper.denominator},
    )


def main() -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    list_path = SNAPSHOT_DIR / "nist-cccbdb-electron-affinity-catalog.html"
    guide_path = SNAPSHOT_DIR / "nist-webbook-gas-phase-ion-thermochemistry.html"
    list_bytes = list_path.read_bytes() if list_path.is_file() else fetch(LIST_URL)
    guide_bytes = guide_path.read_bytes() if guide_path.is_file() else fetch(GUIDE_URL)
    list_path.write_bytes(list_bytes)
    guide_path.write_bytes(guide_bytes)
    list_text = list_bytes.decode("utf-8", errors="replace")
    catalog = []
    for ordinal, match in enumerate(ROW_PATTERN.finditer(list_text), start=1):
        formula, casno, name = clean_html(match.group(1)), match.group(2), clean_html(match.group(3))
        catalog.append({
            "catalog_ordinal": ordinal,
            "formula": formula,
            "casno": casno,
            "name": name,
            "atomic_carrier": is_atomic_formula(formula),
        })
    if len(catalog) != 192 or len({row["casno"] for row in catalog}) != len(catalog):
        raise RuntimeError("NIST CCCBDB electron-affinity catalog boundary changed")

    molecular_catalog = [row for row in catalog if not row["atomic_carrier"]]
    measured_rows = []
    molecular_pages = []
    for source_ordinal, row in enumerate(molecular_catalog, start=1):
        page_url = DETAIL_URL.format(casno=row["casno"])
        filename = f"{source_ordinal:03d}-{slug(row['formula'])}-{row['casno']}.html"
        page_path = SNAPSHOT_DIR / filename
        if page_path.is_file():
            page_bytes = page_path.read_bytes()
        else:
            prior_snapshots = tuple(SNAPSHOT_DIR.glob(f"[0-9][0-9][0-9]-*-{row['casno']}.html"))
            page_bytes = prior_snapshots[0].read_bytes() if len(prior_snapshots) == 1 else fetch(page_url)
            page_path.write_bytes(page_bytes)
            if not prior_snapshots:
                time.sleep(3)
        molecular_pages.append({
            "source_catalog_ordinal": row["catalog_ordinal"],
            "molecular_catalog_ordinal": source_ordinal,
            "formula": row["formula"],
            "name": row["name"],
            "casno": row["casno"],
            "snapshot_path": page_path.relative_to(ROOT).as_posix(),
            "snapshot_hash": sha256_file(page_path),
            "snapshot_url": page_url,
        })
        page_text = unescape(page_bytes.decode("utf-8", errors="replace"))
        match = VALUE_PATTERN.search(page_text)
        if match is None:
            continue
        sign, magnitude_inscription, uncertainty_inscription = match.groups()
        if Fraction(magnitude_inscription) <= 0:
            raise RuntimeError(f"source boundary contains a numerical-null EA inscription: {row['casno']}")
        orientation = (
            "anion-above-neutral-unbound-autodetachment"
            if sign == "-"
            else "anion-below-neutral-bound-attachment"
        )
        lower, upper = display_enclosure(magnitude_inscription)
        target_id = f"NIST-CCCBDB-PROP-008-{row['casno']}-EA"
        measured_rows.append({
            "target_id": target_id,
            "source_id": "NIST-CCCBDB-EXPERIMENTAL-ELECTRON-AFFINITY",
            "source_locator": f"CCCBDB Calculated Electron Affinity page; Experimental Electron Affinity line; CAS {row['casno']}",
            "source_catalog_ordinal": row["catalog_ordinal"],
            "molecular_catalog_ordinal": source_ordinal,
            "measured_vector_ordinal": len(measured_rows) + 1,
            "formula": row["formula"],
            "name": row["name"],
            "casno": row["casno"],
            "initial_molecular_state": "source-identified-neutral-lowest-retained-state",
            "resulting_anion_state": "source-identified-anion-lowest-retained-state",
            "gained_carrier": "one-held-electron-distinction",
            "gain_path": "adiabatic-complete-state-relaxation",
            "condition": "gas-phase-zero-temperature-electron-attachment-definition",
            "units": "electronvolt",
            "source_orientation_glyph": "minus" if sign == "-" else "plus-or-unmarked",
            "fold_state_order_orientation": orientation,
            "magnitude_inscription": magnitude_inscription,
            "exact_positive_magnitude": decimal_pair(magnitude_inscription),
            "uncertainty_inscription": uncertainty_inscription,
            "exact_positive_uncertainty": decimal_pair(uncertainty_inscription) if uncertainty_inscription else None,
            "display_magnitude_lower": lower,
            "display_magnitude_upper": upper,
            "snapshot_path": page_path.relative_to(ROOT).as_posix(),
            "snapshot_url": page_url,
        })

    if not measured_rows:
        raise RuntimeError("NIST CCCBDB molecular electron-affinity vector is empty")
    if len({row["target_id"] for row in measured_rows}) != len(measured_rows):
        raise RuntimeError("NIST CCCBDB molecular electron-affinity vector duplicated a target")
    identities = []
    for row in measured_rows:
        identities.append({
            key: row[key]
            for key in (
                "target_id", "source_id", "source_locator", "source_catalog_ordinal",
                "molecular_catalog_ordinal", "measured_vector_ordinal", "formula", "name", "casno",
                "initial_molecular_state", "resulting_anion_state", "gained_carrier", "gain_path",
                "condition", "units", "snapshot_path", "snapshot_url",
            )
        })
        identities[-1]["target_value_and_orientation_absent"] = True

    primary = {
        "schema": "sft-v3-nist-cccbdb-molecular-electron-affinity-primary-records/1",
        "source_url": LIST_URL,
        "catalog_row_count": len(catalog),
        "atomic_rows_excluded_by_value_free_formula_structure": sum(row["atomic_carrier"] for row in catalog),
        "molecular_catalog_row_count": len(molecular_catalog),
        "molecular_rows_with_explicit_experimental_ea": len(measured_rows),
        "all_catalog_pages_preserved": True,
        "selection_rule": "all non-atomic CCCBDB catalog rows whose individual official page contains an explicit Experimental Electron Affinity line, in catalog order",
        "molecular_pages": molecular_pages,
        "rows": measured_rows,
    }
    identity = {
        "schema": "sft-v3-molecular-electron-affinity-identities/1",
        "complete_row_count": len(identities),
        "all_values_and_state_order_orientations_absent": True,
        "selection_rule": primary["selection_rule"],
        "rows": identities,
    }
    targets = {
        "schema": "sft-v3-molecular-electron-affinity-withheld-measurements/1",
        "complete_row_count": len(measured_rows),
        "release_requires_prediction_seal": True,
        "all_rows_preserved": True,
        "source_negative_glyphs_are_held_state_order_orientations_not_negative_sft_numbers": True,
        "rows": measured_rows,
    }
    page_manifest = {
        "schema": "sft-v3-molecular-electron-affinity-source-page-manifest/1",
        "catalog_row_count": len(catalog),
        "atomic_rows_excluded": sum(row["atomic_carrier"] for row in catalog),
        "molecular_page_count": len(molecular_pages),
        "all_measurement_values_and_orientations_absent": True,
        "pages": molecular_pages,
    }
    primary_path = SNAPSHOT_DIR / "molecular-electron-affinity-primary-records-v1.json"
    primary_path.write_text(json.dumps(primary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    IDENTITY_PATH.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGET_PATH.write_text(json.dumps(targets, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PAGE_MANIFEST_PATH.write_text(json.dumps(page_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "catalog_rows": len(catalog),
        "atomic_rows_excluded": sum(row["atomic_carrier"] for row in catalog),
        "molecular_catalog_rows": len(molecular_catalog),
        "measured_molecular_rows": len(measured_rows),
        "bound_orientation_rows": sum(row["fold_state_order_orientation"].startswith("anion-below") for row in measured_rows),
        "unbound_orientation_rows": sum(row["fold_state_order_orientation"].startswith("anion-above") for row in measured_rows),
        "explicit_uncertainty_rows": sum(row["uncertainty_inscription"] is not None for row in measured_rows),
        "primary_path": primary_path.relative_to(ROOT).as_posix(),
        "identity_path": IDENTITY_PATH.relative_to(ROOT).as_posix(),
        "target_path": TARGET_PATH.relative_to(ROOT).as_posix(),
        "page_manifest_path": PAGE_MANIFEST_PATH.relative_to(ROOT).as_posix(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"PROP-008 source capture halted: {exc}", file=sys.stderr)
        raise
