#!/usr/bin/env python3
"""Capture the complete NIST H2 pair-exchange observation surface for ELEC-006."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
SNAPSHOT = ROOT / SNAPSHOT_PATH
SNAPSHOT_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/pair_exchange_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/pair_exchange_withheld_targets_v1.json"
TERM = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")
ORBITAL = re.compile(r"(?<![A-Za-z0-9])([1-9][0-9]*)([spdfgh])\s*([σπδφ])(?:\^([1-9][0-9]*))?")
ENERGY = re.compile(r"^[\[\(]*\s*~?\s*([0-9]+(?:\.[0-9_]*)?)")


class StateTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.in_row = False
        self.in_cell = False
        self.cell: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.depth += 1
        elif self.depth and tag == "tr":
            self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell = True, []
        elif self.in_cell and tag == "sup":
            self.cell.append("^")
        elif self.in_cell and tag == "sub":
            self.cell.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = False
        elif self.depth and tag == "table":
            self.depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.cell.append(data)


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def term_suffix(state: str, match: re.Match[str]) -> str:
    candidates = tuple(
        position
        for position in (
            state.find(",", match.end()),
            state.find(")", match.end()),
            state.find(" ", match.end()),
        )
        if position >= 0
    )
    return state[match.end() : min(candidates) if candidates else len(state)]


def exact_energy(inscription: str) -> Fraction:
    match = ENERGY.search(inscription)
    if match is None or "eV" in inscription:
        raise RuntimeError("H2 exchange record lacks one common-unit energy inscription")
    return Fraction(match.group(1).replace("_", ""))


def main() -> None:
    if file_hash(SNAPSHOT) != SNAPSHOT_HASH:
        raise RuntimeError("registered NIST H2 snapshot changed")
    parser = StateTableParser()
    parser.feed(SNAPSHOT.read_text(encoding="utf-8"))
    rows = tuple(row for row in parser.rows if len(row) == 13 and TERM.search(row[0]))
    if len(rows) != 46:
        raise RuntimeError("complete H2 state census must contain 46 state rows")

    identities = []
    state_targets = []
    configuration_groups: dict[tuple[int, str, str, int], list[dict[str, object]]] = {}
    for ordinal, row in enumerate(rows, start=1):
        term_matches = tuple(TERM.finditer(row[0]))
        if len(term_matches) != 1:
            raise RuntimeError("registered H2 exchange grammar requires one term assignment per row")
        term = term_matches[0]
        multiplicity = int(term.group(1))
        if multiplicity not in {1, 3}:
            raise RuntimeError("two-electron H2 term lies outside the generated singlet/triplet census")
        suffix = term_suffix(row[0], term)
        orbital = ORBITAL.search(row[0])
        configuration = None
        if orbital is not None:
            configuration = {
                "positive_radial_recurrence": int(orbital.group(1)),
                "source_family_label": orbital.group(2),
                "axis_support_symbol": orbital.group(3),
                "positive_occupancy_count": int(orbital.group(4)) if orbital.group(4) else 1,
            }
        target_id = f"H2-exchange-state-{ordinal:03d}"
        identities.append(
            {
                "target_id": target_id,
                "target_type": "state-exchange-assignment",
                "state_row_ordinal": ordinal,
                "snapshot_path": SNAPSHOT_PATH,
                "snapshot_hash": SNAPSHOT_HASH,
                "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
            }
        )
        spin_exchange = "alternating-exchange" if multiplicity == 1 else "preserving-exchange"
        spatial_exchange = "preserving-exchange" if multiplicity == 1 else "alternating-exchange"
        same_cell = (
            "same-cell-pair-recorded"
            if configuration is not None and configuration["positive_occupancy_count"] == 2
            else "no-explicit-same-cell-pair"
        )
        state_target = {
            "target_id": target_id,
            "target_type": "state-exchange-assignment",
            "state_row_ordinal": ordinal,
            "state_record": row[0],
            "term_assignment_inscription": term.group(0) + suffix,
            "positive_spin_multiplicity": multiplicity,
            "spin_exchange_class": spin_exchange,
            "spatial_exchange_class": spatial_exchange,
            "total_exchange_class": "alternating-exchange",
            "same_cell_record": same_cell,
            "configuration": configuration if configuration is not None else "absence",
            "energy_inscription": row[1],
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_hash": SNAPSHOT_HASH,
        }
        state_targets.append(state_target)
        if configuration is not None:
            key = (
                int(configuration["positive_radial_recurrence"]),
                str(configuration["source_family_label"]),
                str(configuration["axis_support_symbol"]),
                int(configuration["positive_occupancy_count"]),
            )
            configuration_groups.setdefault(key, []).append(
                {
                    "target_id": target_id,
                    "ordinal": ordinal,
                    "multiplicity": multiplicity,
                    "state_record": row[0],
                    "energy_inscription": row[1],
                    "energy": exact_energy(row[1]),
                }
            )

    pair_targets = []
    pair_ordinal = 0
    for configuration_key in sorted(configuration_groups):
        members = configuration_groups[configuration_key]
        singlets = tuple(row for row in members if row["multiplicity"] == 1)
        triplets = tuple(row for row in members if row["multiplicity"] == 3)
        for singlet in singlets:
            for triplet in triplets:
                pair_ordinal += 1
                gap = abs(singlet["energy"] - triplet["energy"])
                if gap <= 0:
                    raise RuntimeError("registered exchange-sensitive pair lacks positive measured separation")
                lower = (
                    "singlet-below-triplet"
                    if singlet["energy"] < triplet["energy"]
                    else "triplet-below-singlet"
                )
                target_id = f"H2-exchange-pair-{pair_ordinal:03d}"
                identities.append(
                    {
                        "target_id": target_id,
                        "target_type": "same-configuration-exchange-pair",
                        "singlet_state_row_ordinal": singlet["ordinal"],
                        "triplet_state_row_ordinal": triplet["ordinal"],
                        "snapshot_path": SNAPSHOT_PATH,
                        "snapshot_hash": SNAPSHOT_HASH,
                        "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
                    }
                )
                pair_targets.append(
                    {
                        "target_id": target_id,
                        "target_type": "same-configuration-exchange-pair",
                        "configuration": {
                            "positive_radial_recurrence": configuration_key[0],
                            "source_family_label": configuration_key[1],
                            "axis_support_symbol": configuration_key[2],
                            "positive_occupancy_count": configuration_key[3],
                        },
                        "singlet_state_target_id": singlet["target_id"],
                        "singlet_state_record": singlet["state_record"],
                        "singlet_energy_inscription": singlet["energy_inscription"],
                        "triplet_state_target_id": triplet["target_id"],
                        "triplet_state_record": triplet["state_record"],
                        "triplet_energy_inscription": triplet["energy_inscription"],
                        "positive_energy_separation_numerator": gap.numerator,
                        "positive_energy_separation_denominator": gap.denominator,
                        "held_energy_order": lower,
                        "snapshot_path": SNAPSHOT_PATH,
                        "snapshot_hash": SNAPSHOT_HASH,
                    }
                )

    if len(pair_targets) != 14:
        raise RuntimeError("complete H2 same-configuration exchange census must contain 14 pairs")
    if sum(row["same_cell_record"] == "same-cell-pair-recorded" for row in state_targets) != 2:
        raise RuntimeError("complete H2 census must retain both explicit same-cell pair records")
    if any(
        row["positive_spin_multiplicity"] != 1
        for row in state_targets
        if row["same_cell_record"] == "same-cell-pair-recorded"
    ):
        raise RuntimeError("an explicit same-cell pair is not in the generated singlet sector")

    source = {
        "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-EXCHANGE-2025",
        "body": "National Institute of Standards and Technology",
        "database": "NIST Chemistry WebBook SRD 69",
        "doi": "10.18434/T4D303",
        "retrieval_date": "2026-07-26",
        "species": "molecular hydrogen H2",
        "state_row_count": 46,
        "same_configuration_pair_count": 14,
    }
    IDENTITIES.write_text(
        json.dumps(
            {"schema": "sft-v3-pair-exchange-identities/1", "source": source, "rows": identities},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    TARGETS.write_text(
        json.dumps(
            {
                "schema": "sft-v3-pair-exchange-withheld-targets/1",
                "source": source,
                "state_rows": state_targets,
                "exchange_pairs": pair_targets,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("state rows:", len(state_targets))
    print("singlets:", sum(row["positive_spin_multiplicity"] == 1 for row in state_targets))
    print("triplets:", sum(row["positive_spin_multiplicity"] == 3 for row in state_targets))
    print("explicit same-cell pairs:", sum(row["same_cell_record"] == "same-cell-pair-recorded" for row in state_targets))
    print("same-configuration exchange pairs:", len(pair_targets))
    print("triplet below singlet:", sum(row["held_energy_order"] == "triplet-below-singlet" for row in pair_targets))
    print("singlet below triplet:", sum(row["held_energy_order"] == "singlet-below-triplet" for row in pair_targets))
    print("identity registry:", file_hash(IDENTITIES))
    print("withheld target registry:", file_hash(TARGETS))


if __name__ == "__main__":
    main()
