#!/usr/bin/env python3
"""Capture NUBASE2020 and register the complete decay/half-life boundary."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SOURCE_URI = "https://amdc.impcas.ac.cn/masstables/Ame2020/nubase_4.mas20"
EXPECTED_RAW_SHA256 = "1585a5eea86c5e17e90307c7e6e786d060049c4039e392a261ff6db977df9859"
RAW_PATH = ROOT / "experiments/external_sources/physics/snapshots/nubase2020-nubase_4.mas20"
RECORD_PATH = ROOT / "experiments/external_sources/physics/snapshots/radioactive-decay-successor-source-record.json"


def mode_codes(branching_record: str) -> tuple[str, ...]:
    result: list[str] = []
    for part in branching_record.split(";"):
        match = re.match(r"([^= <~?>]+)", part.strip())
        if match and match.group(1) != "IS":
            result.append(match.group(1))
    return tuple(result)


def parse_rows(text: str) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        if line.startswith("#") or len(line) < 17:
            continue
        line = line.ljust(209)
        try:
            mass_number = int(line[0:3])
            charge_count = int(line[4:7])
        except ValueError:
            continue
        half_life = line[69:78].strip()
        unit = line[78:80].strip()
        uncertainty = line[81:88].strip()
        numeric_half_life = False
        if half_life and half_life not in {"stbl", "p-unst"} and "#" not in half_life:
            try:
                Fraction(half_life)
                numeric_half_life = True
            except (ValueError, ZeroDivisionError):
                pass
        branching = line[119:209].strip()
        rows.append({
            "mass_number": mass_number,
            "charge_count": charge_count,
            "state_index": line[7:8],
            "nuclide": line[11:17].strip(),
            "half_life": half_life,
            "half_life_unit": unit,
            "half_life_uncertainty": uncertainty,
            "numeric_positive_half_life": numeric_half_life,
            "branching_record": branching,
            "decay_mode_codes": mode_codes(branching),
        })
    return tuple(rows)


def main() -> None:
    request = Request(SOURCE_URI, headers={"User-Agent": "Ernos-Labs-SFT-source-capture/1"})
    with urlopen(request, timeout=60) as response:
        raw = response.read()
    identity = hashlib.sha256(raw).hexdigest()
    if identity != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"NUBASE2020 source identity changed: {identity}")
    rows = parse_rows(raw.decode("utf-8"))
    decay_rows = tuple(row for row in rows if row["decay_mode_codes"])
    numeric_rows = tuple(row for row in rows if row["numeric_positive_half_life"])
    modes = Counter(code for row in decay_rows for code in row["decay_mode_codes"])
    if (len(rows), len(decay_rows), sum(modes.values()), len(modes), len(numeric_rows)) != (5843, 5500, 8718, 50, 4700):
        raise RuntimeError("NUBASE2020 complete decay census changed")
    example_coordinates = {(238, 92, "0"), (14, 6, "0"), (99, 43, "1"), (7, 4, "0"), (8, 4, "0")}
    examples = tuple(
        row for row in rows
        if (row["mass_number"], row["charge_count"], row["state_index"]) in example_coordinates
    )
    payload = {
        "source_id": "AMDC-NUBASE2020-DECAY-HALFLIFE-2021",
        "classification": "observational_derivation",
        "retrieval_date": "2026-07-24",
        "source": {
            "measurement_body": "Atomic Mass Data Center, Institute of Modern Physics, Chinese Academy of Sciences",
            "source_uri": SOURCE_URI,
            "landing_uri": "https://amdc.impcas.ac.cn/web/nubase_en.html",
            "publication_uri": "https://amdc.impcas.ac.cn/masstables/Ame2020/Kondev_2021_Chinese_Phys._C_45_030001.pdf",
            "raw_snapshot_path": str(RAW_PATH.relative_to(ROOT)),
            "raw_sha256": "sha256:" + identity,
            "table_description": "NUBASE2020 nuclear properties including half-life, uncertainty, decay modes and intensities",
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
            "all_named_modes_must_map_or_halt": True,
            "alpha_beta_gamma_are_representatives_not_only_named_codes": True,
            "no_ontic_randomness_imported": True,
        },
        "parser": {
            "mass_slice": "0:3",
            "charge_slice": "4:7",
            "state_index_slice": "7:8",
            "half_life_slice": "69:78",
            "unit_slice": "78:80",
            "uncertainty_slice": "81:88",
            "branching_slice": "119:209",
            "isotopic_abundance_is_not_a_decay_mode": True,
        },
        "complete_decay_census": {
            "all_nuclear_state_rows": len(rows),
            "rows_with_decay_modes": len(decay_rows),
            "decay_mode_entry_count": sum(modes.values()),
            "distinct_decay_mode_code_count": len(modes),
            "numeric_positive_half_life_row_count": len(numeric_rows),
            "mode_code_counts": dict(sorted(modes.items())),
            "registered_example_rows": examples,
        },
    }
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PATH.write_bytes(raw)
    RECORD_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"captured {RAW_PATH.relative_to(ROOT)} sha256:{identity}")
    print("wrote complete NUBASE2020 boundary: 5,500 decay rows; 8,718 mode entries; 50 codes; 4,700 positive numeric half-lives")


if __name__ == "__main__":
    main()
