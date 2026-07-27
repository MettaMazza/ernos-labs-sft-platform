#!/usr/bin/env python3
"""Capture the complete NIST ethanol experimental internal-rotation paths."""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sft.engine.source import hash_file  # noqa: E402

URL = "https://cccbdb.nist.gov/exprotbar2x.asp?casno=64175&ti=1"
SOURCE_ID = "NIST-CCCBDB-SRD101-ETHANOL-EXPERIMENTAL-ROTATIONAL-BARRIER"
SNAPSHOT_PATH = "experiments/external_sources/chemistry/snapshots/configuration-order-v1/nist-cccbdb-ethanol-experimental-rotational-barrier.html"
IDENTITY_PATH = "experiments/external_sources/chemistry/configuration_order_target_identities_v1.json"
TARGET_PATH = "experiments/external_sources/chemistry/configuration_order_withheld_targets_v1.json"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.in_row = False; self.in_cell = False; self.parts = []; self.row = []; self.rows = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "tr": self.in_row, self.row = True, []
        elif self.in_row and tag.lower() in {"td", "th"}: self.in_cell, self.parts = True, []
    def handle_endtag(self, tag):
        if self.in_cell and tag.lower() in {"td", "th"}: self.row.append(" ".join("".join(self.parts).split())); self.in_cell = False
        elif self.in_row and tag.lower() == "tr":
            if self.row: self.rows.append(tuple(self.row))
            self.in_row = False
    def handle_data(self, data):
        if self.in_cell: self.parts.append(data)


def main() -> None:
    raw = urlopen(Request(URL, headers={"User-Agent": "SFT-v3-source-capture/1"}), timeout=30).read()
    snapshot = ROOT / SNAPSHOT_PATH; snapshot.parent.mkdir(parents=True, exist_ok=True); snapshot.write_bytes(raw)
    snapshot_hash = hash_file(snapshot)
    parser = TableParser(); parser.feed(raw.decode("utf-8", "replace"))
    measured = [row for row in parser.rows if len(row) == 4 and row[0] in {"1", "2"} and row[1].isdigit()]
    if len(measured) != 50:
        raise ValueError("complete two-path 50-row NIST surface was not reconstructed")
    rows = [{"target_id": f"ethanol-torsion-{int(row[0])}-coordinate-{position:02d}", "source_id": SOURCE_ID, "torsion_index": int(row[0]), "path_position": position, "angle_inscription_degrees": row[1], "energy_inscription_kj_mol": row[2], "energy_inscription_cm_inverse": row[3], "snapshot_path": SNAPSHOT_PATH, "snapshot_hash": snapshot_hash} for position, row in enumerate(measured, start=1)]
    targets = {"schema": "sft-v3-configuration-order-withheld-targets/1", "source": SOURCE_ID, "rows": rows}
    identities = {"schema": "sft-v3-configuration-order-identities/1", "source": SOURCE_ID, "rows": [{"target_id": row["target_id"], "source_id": SOURCE_ID, "source_url": URL, "torsion_index": row["torsion_index"], "path_position": row["path_position"], "snapshot_path": SNAPSHOT_PATH, "snapshot_hash": snapshot_hash} for row in rows]}
    for path, payload in ((IDENTITY_PATH, identities), (TARGET_PATH, targets)):
        destination = ROOT / path; destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"); print(path, hash_file(destination))
    print(SNAPSHOT_PATH, snapshot_hash)


if __name__ == "__main__": main()
