#!/usr/bin/env python3
"""Register the complete NIST H2 state-transition surface for ELEC-009."""

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
SOURCE_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-TRANSITIONS"
SOURCE_URL = "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/state_transition_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/state_transition_withheld_targets_v1.json"
TERM_PATTERN = re.compile(r"\^([1-9][0-9]*)(Σ|Π|Δ|Φ)")


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.depth = 0; self.in_row = False; self.in_cell = False; self.parts = []; self.row = []; self.rows = []
    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split(): self.depth += 1
        elif self.depth and tag == "tr": self.in_row, self.row = True, []
        elif self.in_row and tag in {"td", "th"}: self.in_cell, self.parts = True, []
        elif self.in_cell and tag == "sup": self.parts.append("^")
        elif self.in_cell and tag == "sub": self.parts.append("_")
    def handle_endtag(self, tag: str) -> None:
        if self.in_cell and tag in {"td", "th"}: self.row.append(" ".join(unescape("".join(self.parts)).split())); self.in_cell = False
        elif self.in_row and tag == "tr":
            if self.row: self.rows.append(tuple(self.row))
            self.in_row = False
        elif self.depth and tag == "table": self.depth -= 1
    def handle_data(self, data: str) -> None:
        if self.in_cell: self.parts.append(data)


def hash_file(path: Path) -> str:
    from hashlib import sha256
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def observation_class(inscription: str) -> str:
    if not inscription: return "absent-transition-coordinate"
    if any(arrow in inscription for arrow in ("→", "←", "↔")): return "observed-directional-transition"
    return "observed-coupled-state-relation"


def main() -> None:
    source = ROOT / SOURCE_PATH
    if hash_file(source) != SOURCE_HASH: raise RuntimeError("ELEC-009 NIST H2 source changed")
    parser = TableParser(); parser.feed(source.read_text(encoding="utf-8"))
    identities, targets = [], []
    primary_count = continuation_count = 0
    current_state = None
    for row in parser.rows:
        if len(row) == 13 and TERM_PATTERN.search(row[0]):
            primary_count += 1; current_state = row[0]
            target_id = f"H2-transition-state-{primary_count:03d}"
            transition, band = row[11] or "absence", row[12] or "absence"
            identities.append({"target_id": target_id, "source_id": SOURCE_ID, "source_url": SOURCE_URL, "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH, "source_row_kind": "primary-state", "source_row_ordinal": primary_count})
            targets.append({"target_id": target_id, "source_id": SOURCE_ID, "source_row_kind": "primary-state", "source_row_ordinal": primary_count, "state_record": row[0], "transition_inscription": transition, "band_origin_inscription": band, "observation_class": observation_class(row[11]), "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH})
        elif len(row) == 12 and current_state is not None and row[10].strip():
            continuation_count += 1
            target_id = f"H2-transition-continuation-{continuation_count:03d}"
            identities.append({"target_id": target_id, "source_id": SOURCE_ID, "source_url": SOURCE_URL, "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH, "source_row_kind": "continuation-transition", "source_row_ordinal": continuation_count})
            targets.append({"target_id": target_id, "source_id": SOURCE_ID, "source_row_kind": "continuation-transition", "source_row_ordinal": continuation_count, "state_record": current_state, "transition_inscription": row[10], "band_origin_inscription": row[11] or "absence", "observation_class": observation_class(row[10]), "snapshot_path": SOURCE_PATH, "snapshot_hash": SOURCE_HASH})
    if primary_count != 46 or continuation_count != 14 or len(targets) != 60: raise RuntimeError("ELEC-009 complete transition census differs")
    counts = {"primary_state_rows": primary_count, "continuation_transition_rows": continuation_count, "observed_directional_transitions": sum(row["observation_class"] == "observed-directional-transition" for row in targets), "observed_coupled_state_relations": sum(row["observation_class"] == "observed-coupled-state-relation" for row in targets), "absent_transition_coordinates": sum(row["observation_class"] == "absent-transition-coordinate" for row in targets), "positive_band_inscriptions": sum(row["band_origin_inscription"] != "absence" for row in targets), "absent_band_coordinates": sum(row["band_origin_inscription"] == "absence" for row in targets)}
    expected = {"primary_state_rows": 46, "continuation_transition_rows": 14, "observed_directional_transitions": 55, "observed_coupled_state_relations": 4, "absent_transition_coordinates": 1, "positive_band_inscriptions": 55, "absent_band_coordinates": 5}
    if counts != expected: raise RuntimeError("ELEC-009 transition class census differs: " + repr(counts))
    source_meta = {"measurement_body": "National Institute of Standards and Technology", "database": "Chemistry WebBook SRD 69", "doi": "10.18434/T4D303", "retrieval_date": "2026-07-26", **counts}
    IDENTITIES.write_text(json.dumps({"schema": "sft-v3-state-transition-identities/1", "source": source_meta, "rows": identities}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGETS.write_text(json.dumps({"schema": "sft-v3-state-transition-withheld-targets/1", "source": source_meta, "rows": targets}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2, sort_keys=True)); print("identity registry:", hash_file(IDENTITIES)); print("target registry:", hash_file(TARGETS))


if __name__ == "__main__": main()
