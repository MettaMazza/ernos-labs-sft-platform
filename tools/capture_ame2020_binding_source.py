#!/usr/bin/env python3
"""Capture the authoritative AME2020 binding table and extraction record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from fractions import Fraction
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URI = "https://amdc.impcas.ac.cn/masstables/Ame2020/mass_1.mas20"
EXPECTED_RAW_SHA256 = "e8599c6d7f724fac91934e59f1b9de8fb8f63e820f4b39456b790665ed2a3307"
RAW_PATH = ROOT / "experiments/external_sources/physics/snapshots/ame2020-mass_1.mas20"
RECORD_PATH = ROOT / "experiments/external_sources/physics/snapshots/nuclear-binding-curve-successor-source-record.json"


def parse_rows(text: str) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        if len(line) < 79:
            continue
        try:
            neutron_count = int(line[4:9])
            charge_count = int(line[9:14])
            mass_number = int(line[14:19])
        except ValueError:
            continue
        element = line[20:23].strip()
        origin = line[23:27].strip()
        binding = line[54:67].strip()
        uncertainty = line[68:78].strip()
        if not binding or binding == "*" or "#" in binding:
            continue
        try:
            float(binding)
            float(uncertainty)
        except ValueError:
            continue
        rows.append({
            "mass_number": mass_number,
            "charge_count": charge_count,
            "neutron_count": neutron_count,
            "element": element,
            "origin_flag": origin,
            "binding_energy_per_nucleon_keV": binding,
            "standard_uncertainty_keV": uncertainty,
        })
    return tuple(rows)


def main() -> None:
    request = Request(SOURCE_URI, headers={"User-Agent": "Ernos-Labs-SFT-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        raw = response.read()
    identity = hashlib.sha256(raw).hexdigest()
    if identity != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"AME2020 source identity changed: {identity}")
    rows = parse_rows(raw.decode("utf-8"))
    if len(rows) != 2550:
        raise RuntimeError(f"AME2020 numeric binding row count changed: {len(rows)}")
    composite_rows = tuple(row for row in rows if row["mass_number"] >= 2)
    if len(composite_rows) != 2548:
        raise RuntimeError(f"AME2020 positive composite binding row count changed: {len(composite_rows)}")
    ranked = sorted(
        composite_rows,
        key=lambda row: Fraction(str(row["binding_energy_per_nucleon_keV"])),
        reverse=True,
    )
    if (ranked[0]["mass_number"], ranked[0]["charge_count"], ranked[0]["element"]) != (62, 28, "Ni"):
        raise RuntimeError("AME2020 binding maximum changed")
    anchors = {2, 4, 12, 16, 40, 54, 56, 58, 60, 62, 64, 120, 208, 232, 235, 238}
    registered = tuple(
        row for row in composite_rows
        if row["mass_number"] in anchors and (
            row["element"] in {"H", "He", "C", "O", "Ca", "Fe", "Ni", "Sn", "Pb", "Th", "U"}
        )
    )
    payload = {
        "source_id": "AMDC-AME2020-MASS-1-BINDING-2021",
        "classification": "observational_derivation",
        "retrieval_date": "2026-07-24",
        "source": {
            "measurement_body": "Atomic Mass Data Center, Institute of Modern Physics, Chinese Academy of Sciences",
            "source_uri": SOURCE_URI,
            "landing_uri": "https://amdc.impcas.ac.cn/web/masseval.html",
            "publication_i_uri": "https://www-nds.iaea.org/amdc/ame2020/AME2020-a.pdf",
            "publication_ii_uri": "https://www-nds.iaea.org/amdc/ame2020/AME2020-b.pdf",
            "raw_snapshot_path": str(RAW_PATH.relative_to(ROOT)),
            "raw_sha256": "sha256:" + identity,
            "table_description": "AME2020 atomic masses, including binding energy per nucleon and reported standard uncertainty",
        },
        "custody": {
            "development_targets_already_known": True,
            "protocol_classification": "observational-data-informed_target-inaccessible_sealed-prediction",
            "empirical_prediction_protocol": True,
            "target_inaccessible_during_prediction_execution": True,
            "formal_relations_contain_measurement": False,
            "measurements_select_formal_survivors": False,
            "engine_prediction_sealed_before_target_release_within_run": True,
            "complete_reported_uncertainties_retained": True,
            "no_fitted_mass_formula_coefficient": True,
            "irrational_radius_not_admitted": True,
        },
        "parser": {
            "format_from_ame_header": "a1,i3,i5,i5,i5,1x,a3,a4,1x,f14.6,f12.6,f13.5,1x,f10.5,1x,a2,f13.5,f11.5,1x,i3,1x,f13.6,f12.6",
            "binding_field_slice": "54:67",
            "binding_uncertainty_slice": "68:78",
            "estimated_hash_rows_excluded_from_measured_maximum": True,
        },
        "complete_numeric_binding_census": {
            "raw_numeric_row_count": len(rows),
            "positive_composite_row_count": len(composite_rows),
            "singleton_empty_binding_boundary_rows": tuple(row for row in rows if row["mass_number"] == 1),
            "global_top_rows": ranked[:30],
            "registered_curve_anchor_rows": registered,
        },
    }
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    RECORD_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"captured {RAW_PATH.relative_to(ROOT)} sha256:{identity}")
    print(f"wrote {RECORD_PATH.relative_to(ROOT)} with {len(composite_rows)} positive composite rows plus two retained singleton boundary rows")


if __name__ == "__main__":
    main()
