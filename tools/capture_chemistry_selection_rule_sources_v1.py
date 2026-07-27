#!/usr/bin/env python3
"""Build the identity-only and withheld raw-observation registries for ELEC-010."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


TRANSITION_PATH = "experiments/external_sources/chemistry/state_transition_withheld_targets_v1.json"
SYMMETRY_PATH = "experiments/external_sources/chemistry/state_symmetry_withheld_targets_v1.json"
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
IDENTITY_PATH = "experiments/external_sources/chemistry/selection_rule_target_identities_v1.json"
TARGET_PATH = "experiments/external_sources/chemistry/selection_rule_withheld_targets_v1.json"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-SELECTION-SURFACE"


class CellParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.in_cell = False
        self.parts: list[str] = []
        self.row: list[str] = []
        self.rows: list[tuple[str, ...]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        if tag == "tr":
            self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.parts = True, []
        elif self.in_cell and tag == "sup":
            self.parts.append("^")
        elif self.in_cell and tag == "sub":
            self.parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.parts)).split()))
            self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = False

    def handle_data(self, data: str) -> None:
        if self.in_cell:
            self.parts.append(data)


def endpoints(inscription: str) -> list[str]:
    cleaned = inscription.strip("()")
    for arrow in ("↔", "→", "←"):
        if arrow in cleaned:
            left, right = cleaned.split(arrow, 1)
            return [left.strip().split()[0]] + right.strip().split()[0].rstrip(",").split(",")
    if inscription == "absence":
        return []
    token = cleaned.split()[0]
    if "-" in token:
        return token.split("-", 1)
    raise ValueError("unparseable H2 transition inscription: " + inscription)


def main() -> None:
    transitions = json.loads((ROOT / TRANSITION_PATH).read_text(encoding="utf-8"))["rows"]
    symmetries = json.loads((ROOT / SYMMETRY_PATH).read_text(encoding="utf-8"))["rows"]
    h2 = {row["state_record"].split()[0].strip("()"): row for row in symmetries if row["species_row_id"] == "hydrogen-neutral"}
    snapshot_hash = hash_file(ROOT / SNAPSHOT_PATH)
    rows = []
    for source in transitions:
        names = endpoints(str(source["transition_inscription"]))
        signatures = []
        for name in names:
            state = h2.get(name)
            signatures.append({
                "state": name,
                "resolved": state is not None,
                "positive_spin_multiplicity": None if state is None else state["positive_spin_multiplicity"],
                "axis_support_symbol": None if state is None else state["axis_support_symbol"],
                "held_inversion_label": None if state is None else state["held_inversion_label"],
            })
        rows.append({
            "target_id": "selection-" + str(source["target_id"]),
            "target_kind": "complete-transition-record",
            "source_id": SOURCE_ID,
            "source_row_kind": source["source_row_kind"],
            "source_row_ordinal": source["source_row_ordinal"],
            "state_record": source["state_record"],
            "transition_inscription": source["transition_inscription"],
            "observation_class": source["observation_class"],
            "endpoint_signatures": signatures,
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_hash": snapshot_hash,
        })
    parser = CellParser()
    parser.feed((ROOT / SNAPSHOT_PATH).read_text(encoding="utf-8"))
    notes = {row[0]: row[1] for row in parser.rows if len(row) == 2 and row[0] in {"42", "73", "78"}}
    if set(notes) != {"42", "73", "78"}:
        raise ValueError("complete adverse note surface was not reconstructed")
    for note in ("42", "73", "78"):
        rows.append({
            "target_id": "selection-adverse-note-" + note,
            "target_kind": "adverse-observation-note",
            "source_id": SOURCE_ID,
            "note_id": note,
            "note_text": notes[note],
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_hash": snapshot_hash,
        })
    if len(rows) != 63:
        raise ValueError("ELEC-010 requires all 60 transition rows and three adverse notes")
    targets = {"schema": "sft-v3-selection-rule-withheld-targets/1", "source": SOURCE_ID, "rows": rows}
    identities = {
        "schema": "sft-v3-selection-rule-identities/1",
        "source": SOURCE_ID,
        "rows": [{
            "target_id": row["target_id"],
            "target_kind": row["target_kind"],
            "source_id": SOURCE_ID,
            "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
            "snapshot_path": SNAPSHOT_PATH,
            "snapshot_hash": snapshot_hash,
        } for row in rows],
    }
    for path, payload in ((IDENTITY_PATH, identities), (TARGET_PATH, targets)):
        destination = ROOT / path
        destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(path, hash_file(destination))


if __name__ == "__main__":
    main()
