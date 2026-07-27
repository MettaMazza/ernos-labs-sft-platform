#!/usr/bin/env python3
"""Capture the complete primary Table 1 temperature/rate evidence for KIN-003."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/temperature_dependence_capture_spec_v1.json"
SPEC_HASH = "sha256:2298cbf26d1018c3bee8515dafb8302c42b6aa5bd92b57f2e21fa3aeec6df56d"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-003-temperature-dependence-v1"
PDF_PATH = SNAPSHOT_ROOT / "jp505790m-primary-accepted-manuscript.pdf"
PRIMARY_PATH = SNAPSHOT_ROOT / "temperature-dependence-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/temperature_dependence_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/temperature_dependence_withheld_targets_v1.json"


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


def column_tokens(words: list[dict], low: float, high: float) -> list[str]:
    return [str(word["text"]) for word in sorted(words, key=lambda row: float(row["x0"])) if low <= float(word["x0"]) < high]


def exact_pair(tokens: list[str], *, allow_absence: bool = False) -> tuple[str, str] | tuple[str, str]:
    if tokens == ["-"] and allow_absence:
        return ("EmptyOne", "EmptyOne")
    if len(tokens) != 3 or tokens[1] != "±":
        raise ValueError(f"KIN-003 exact value/uncertainty pair changed: {tokens}")
    return (tokens[0], tokens[2])


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("KIN-003 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    source = spec["sources"][0]
    if (
        spec.get("schema") != "sft-v3-temperature-dependence-prefetch-capture-spec/1"
        or spec.get("all_temperature_rate_density_pressure_uncertainty_method_note_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 1
    ):
        raise ValueError("KIN-003 prefetch boundary is not value-free and complete")

    raw = fetch(source["pdf_url"])
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    PDF_PATH.write_bytes(raw)
    with pdfplumber.open(PDF_PATH) as document:
        if len(document.pages) != 27:
            raise ValueError("KIN-003 primary article page count changed")
        first_text = document.pages[0].extract_text() or ""
        table_page = document.pages[19]
        table_text = table_page.extract_text(x_tolerance=2, y_tolerance=2) or ""
        words = table_page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=False)
    if source["doi"].casefold() not in first_text.casefold() or "Table 1. Measured rate coefficients" not in table_text:
        raise ValueError("KIN-003 DOI or complete measured Table 1 identity changed")

    row_tops = sorted({
        round(float(word["top"]), 1)
        for word in words
        if 175 < float(word["top"]) < 750 and 100 <= float(word["x0"]) < 150 and str(word["text"]).isdigit()
    })
    if len(row_tops) != 14:
        raise ValueError(f"KIN-003 complete Table 1 condition-row count changed: {len(row_tops)}")

    matrix_rows: list[dict] = []
    identities: list[dict] = []
    targets: list[dict] = []
    target_ordinal = 0
    reaction_columns = (
        ("ethanol", "OH + ethanol", 285.0, 390.0),
        ("propan-2-ol", "OH + propan-2-ol", 390.0, 490.0),
    )
    for condition_ordinal, top in enumerate(row_tops, start=1):
        row_words = [word for word in words if abs(float(word["top"]) - top) <= 5.0]
        temperature, temperature_uncertainty = exact_pair(column_tokens(row_words, 100.0, 155.0))
        density, density_uncertainty = exact_pair(column_tokens(row_words, 205.0, 280.0))
        bath_tokens = column_tokens(row_words, 155.0, 205.0)
        bath_gas = "N2" if bath_tokens and bath_tokens[0] == "N" else "Ar" if bath_tokens == ["Ar"] else ""
        if not bath_gas:
            raise ValueError(f"KIN-003 bath-gas identity changed at condition row {condition_ordinal}: {bath_tokens}")
        matrix_row = {
            "source_condition_row_ordinal": condition_ordinal,
            "temperature_K_external_inscription": temperature,
            "temperature_uncertainty_K_external_inscription": temperature_uncertainty,
            "bath_gas": bath_gas,
            "total_density_1e16_molecule_cm_minus3_external_inscription": density,
            "total_density_uncertainty_1e16_molecule_cm_minus3_external_inscription": density_uncertainty,
        }
        for reaction_key, reaction_identity, low, high in reaction_columns:
            rate, rate_uncertainty = exact_pair(column_tokens(row_words, low, high), allow_absence=True)
            matrix_row[f"{reaction_key}_rate_1e_minus11_molecule_minus1_cm3_s_minus1_external_inscription"] = rate
            matrix_row[f"{reaction_key}_rate_uncertainty_1e_minus11_molecule_minus1_cm3_s_minus1_external_inscription"] = rate_uncertainty
            if rate == "EmptyOne":
                continue
            target_ordinal += 1
            target_id = f"SFT-CHEM-KIN-003-TEMPERATURE-RATE-{target_ordinal:04d}"
            identity = {
                "target_id": target_id,
                "source_id": source["source_id"],
                "table_number": "1",
                "source_condition_row_ordinal": condition_ordinal,
                "reaction_key": reaction_key,
                "all_temperature_rate_density_uncertainty_method_note_and_target_hash_values_absent": True,
            }
            target = {
                "target_id": target_id,
                "source_id": source["source_id"],
                "doi": source["doi"],
                "table_number": "1",
                "source_condition_row_ordinal": condition_ordinal,
                "reaction_key": reaction_key,
                "reaction_identity": reaction_identity,
                "measurement_method": "pulsed Laval nozzle with pulsed-laser photolysis and laser-induced-fluorescence OH detection",
                "temperature_K_external_inscription": temperature,
                "temperature_uncertainty_K_external_inscription": temperature_uncertainty,
                "bath_gas": bath_gas,
                "total_density_1e16_molecule_cm_minus3_external_inscription": density,
                "total_density_uncertainty_1e16_molecule_cm_minus3_external_inscription": density_uncertainty,
                "rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription": f"{rate}E-11",
                "rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription": f"{rate_uncertainty}E-11",
                "source_error_disclosure": "errors combine propagated 95 percent confidence limits in bimolecular rate coefficients with expansion-density errors",
                "fitted_arrhenius_prefactor_or_activation_value_used_in_fold_law": False,
            }
            identities.append(identity)
            targets.append(target)
        matrix_rows.append(matrix_row)

    if len(targets) != 19 or {row["reaction_key"] for row in targets} != {"ethanol", "propan-2-ol"}:
        raise ValueError(f"KIN-003 complete measured reaction-vector count changed: {len(targets)}")
    identity_doc = {
        "schema": "sft-v3-temperature-dependence-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_source_count": 1,
        "complete_condition_row_count": len(matrix_rows),
        "complete_target_count": len(identities),
        "all_temperature_rate_density_uncertainty_method_note_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-temperature-dependence-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_source_count": 1,
        "complete_condition_row_count": len(matrix_rows),
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-temperature-dependence-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "source_id": source["source_id"],
        "doi": source["doi"],
        "complete_pdf_path": str(PDF_PATH.relative_to(ROOT)),
        "complete_pdf_hash": sha_file(PDF_PATH),
        "complete_pdf_page_count": 27,
        "table_page_number": 20,
        "table_number": "1",
        "complete_condition_row_count": len(matrix_rows),
        "complete_target_count": len(targets),
        "complete_source_ordered_table_matrix": matrix_rows,
        "complete_normalized_table_text": table_text,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_table_1_rows_columns_uncertainties_absences_and_note_preserved": True,
        "fitted_table_2_excluded_by_prefetch_measured_table_rule": True,
        "arrhenius_exponential_logarithmic_prefactor_activation_value_continuum_derivative_selection_fit_or_target_correction_used_in_law": False,
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH,
        "complete_condition_row_count": len(matrix_rows),
        "complete_target_count": len(targets),
        "pdf_hash": sha_file(PDF_PATH),
        "identity_hash": identity_hash,
        "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH),
        "primary_hash": sha_file(PRIMARY_PATH),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
