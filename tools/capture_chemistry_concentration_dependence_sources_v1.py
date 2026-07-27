#!/usr/bin/env python3
"""Capture complete primary Table 2 concentration/rate evidence for KIN-002."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/concentration_dependence_capture_spec_v1.json"
SPEC_HASH = "sha256:d80a5a54d5191df6ef702a8818c49b5cd964140b9106da6516aa4043792cde0d"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-002-concentration-dependence-v1"
PDF_PATH = SNAPSHOT_ROOT / "c3cp54664k-primary-article.pdf"
PRIMARY_PATH = SNAPSHOT_ROOT / "concentration-dependence-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/concentration_dependence_target_identities_v1.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/concentration_dependence_withheld_targets_v1.json"


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


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("KIN-002 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    source = spec["sources"][0]
    if (
        spec.get("schema") != "sft-v3-concentration-dependence-prefetch-capture-spec/1"
        or spec.get("all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("selection_fit_or_correction_permitted") is not False
        or len(spec.get("sources", ())) != 1
    ):
        raise ValueError("KIN-002 prefetch boundary is not value-free and complete")
    raw = fetch(source["pdf_url"])
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    PDF_PATH.write_bytes(raw)
    with pdfplumber.open(PDF_PATH) as document:
        if len(document.pages) != 13:
            raise ValueError("KIN-002 primary article page count changed")
        metadata_text = "\n".join((document.pages[index].extract_text() or "") for index in (0, 5))
        table_text = document.pages[5].crop((295, 20, 590, 335)).extract_text(x_tolerance=2, y_tolerance=2) or ""
    if source["doi"].casefold() not in metadata_text.casefold() or "Table2" not in table_text or "OH+DME" not in table_text:
        raise ValueError("KIN-002 DOI or complete Table 2 identity changed")
    normalized = table_text.replace("(cid:2)", "±").replace("(cid:3)", "×").replace("(cid:4)", "−")
    pattern = re.compile(
        r"^(\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?) (\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?) "
        r"\((\d+(?:\.\d+)?) ± (\d+(?:\.\d+)?)\) × 10−(\d+)([a-z,]*)$"
    )
    parsed = []
    for line in normalized.splitlines():
        match = pattern.match(line.strip())
        if match:
            parsed.append(match.groups())
    if len(parsed) != 9:
        raise ValueError(f"KIN-002 complete Table 2 row count changed: {len(parsed)}")
    identities = []
    targets = []
    for ordinal, row in enumerate(parsed, start=1):
        temperature, temperature_uncertainty, density, density_uncertainty, rate, rate_uncertainty, exponent, notes = row
        target_id = f"SFT-CHEM-KIN-002-CONCENTRATION-RATE-{ordinal:04d}"
        identities.append({
            "target_id": target_id, "source_id": source["source_id"], "table_number": source["table_number"],
            "source_row_ordinal": ordinal,
            "all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent": True,
        })
        targets.append({
            "target_id": target_id, "source_id": source["source_id"], "doi": source["doi"],
            "table_number": source["table_number"], "source_row_ordinal": ordinal,
            "reaction_identity": "OH + dimethyl ether",
            "measurement_method": "pulsed Laval nozzle with pulsed-laser photolysis and laser-induced-fluorescence OH detection",
            "temperature_K_external_inscription": temperature,
            "temperature_uncertainty_K_external_inscription": temperature_uncertainty,
            "flow_density_1e16_molecule_cm_minus3_external_inscription": density,
            "flow_density_uncertainty_1e16_molecule_cm_minus3_external_inscription": density_uncertainty,
            "rate_coefficient_molecule_minus1_cm3_s_minus1_external_inscription": f"{rate}E-{exponent}",
            "rate_uncertainty_molecule_minus1_cm3_s_minus1_external_inscription": f"{rate_uncertainty}E-{exponent}",
            "source_note_markers": notes,
            "source_table_fit_disclosure": "95 percent confidence intervals in linear fits of pseudo-first-order coefficients versus reagent density, together with systematic errors",
            "fitted_exponent_or_coefficient_used_in_fold_law": False,
        })
    identity_doc = {
        "schema": "sft-v3-concentration-dependence-target-identities/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_source_count": 1, "complete_target_count": len(identities),
        "all_species_temperature_density_rate_uncertainty_method_note_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-concentration-dependence-withheld-targets/1", "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash, "release_requires_complete_identity_prediction_seal": True,
        "complete_source_count": 1, "complete_target_count": len(targets), "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    write_json(PRIMARY_PATH, {
        "schema": "sft-v3-concentration-dependence-primary-records/1",
        "prefetch_capture_spec_hash_before_source_open": SPEC_HASH, "capture_rule": spec["capture_rule"],
        "source_id": source["source_id"], "doi": source["doi"], "complete_pdf_path": str(PDF_PATH.relative_to(ROOT)),
        "complete_pdf_hash": sha_file(PDF_PATH), "complete_pdf_page_count": 13, "table_page_number": 6,
        "table_number": source["table_number"], "complete_target_count": len(targets),
        "complete_normalized_table_text": normalized,
        "identity_registry_canonical_hash": identity_hash, "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_table_2_rows_uncertainties_and_notes_preserved": True,
        "mass_action_power_law_reaction_order_fitted_exponent_coefficient_logarithm_continuum_derivative_selection_or_target_correction_used_in_law": False,
        "external_values_used_as_proof_parameters": False,
    })
    print(json.dumps({
        "prefetch_spec_hash": SPEC_HASH, "complete_target_count": len(targets), "pdf_hash": sha_file(PDF_PATH),
        "identity_hash": identity_hash, "identity_file_hash": sha_file(IDENTITY_PATH),
        "target_hash": sha_file(TARGET_PATH), "primary_hash": sha_file(PRIMARY_PATH),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
