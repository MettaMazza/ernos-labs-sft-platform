#!/usr/bin/env python3
"""Capture the complete NIST H2/HD/D2 isotopologue and vibronic surface."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/nuclear-electronic-v1"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/nuclear_electronic_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/nuclear_electronic_withheld_targets_v1.json"
H2_SOURCE = ROOT / "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
TERM_PATTERN = re.compile(r"\^[1-9][0-9]*(?:Σ|Π|Δ|Φ)")
WEIGHT_PATTERN = re.compile(r"Molecular weight.*?</a>:</strong>\s*([^<]+)", re.S)

SOURCES = (
    ("H2", "C1333740", ("protium", "protium"), "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000"),
    ("HD", "C13983205", ("protium", "deuterium"), "https://webbook.nist.gov/cgi/cbook.cgi?ID=C13983205&Mask=1000"),
    ("D2", "C7782390", ("deuterium", "deuterium"), "https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782390&Mask=1000"),
)


class DiatomicParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.depth = self.in_row = self.in_cell = self.in_note = 0
        self.cell = []
        self.row = []
        self.rows = []

    def handle_starttag(self, tag, attrs) -> None:
        attributes = dict(attrs)
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self.depth += 1
        elif self.depth and tag == "tr":
            self.in_row, self.row = 1, []
        elif self.in_row and tag in {"td", "th"}:
            self.in_cell, self.cell = 1, []
        elif self.in_cell and tag == "a" and (attributes.get("href") or "").startswith("#Dia"):
            self.in_note += 1
        elif self.in_cell and not self.in_note and tag == "sup":
            self.cell.append("^")
        elif self.in_cell and not self.in_note and tag == "sub":
            self.cell.append("_")

    def handle_endtag(self, tag) -> None:
        if tag == "a" and self.in_note:
            self.in_note -= 1
        elif self.in_cell and tag in {"td", "th"}:
            self.row.append(" ".join(unescape("".join(self.cell)).split()))
            self.in_cell = 0
        elif self.in_row and tag == "tr":
            if self.row:
                self.rows.append(tuple(self.row))
            self.in_row = 0
        elif self.depth and tag == "table":
            self.depth -= 1

    def handle_data(self, data) -> None:
        if self.in_cell and not self.in_note:
            self.cell.append(data)


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def source_bytes(species: str, url: str) -> bytes:
    if species == "H2":
        return H2_SOURCE.read_bytes()
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT/3.0 scientific-reproducibility Maria.Smith.Sftoe@gmail.com"})
    return urlopen(request, timeout=60).read()


def main() -> None:
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    identities = []
    targets = []
    source_rows = []
    expected_counts = {"H2": 46, "HD": 20, "D2": 29}
    for species, nist_id, isotopes, url in SOURCES:
        path = SNAPSHOT_ROOT / (nist_id + ".html")
        payload = source_bytes(species, url)
        path.write_bytes(payload)
        text = payload.decode("utf-8", "replace")
        weight_match = WEIGHT_PATTERN.search(text)
        if weight_match is None:
            raise RuntimeError(species + ": molecular-weight inscription missing")
        molecular_weight = weight_match.group(1).strip()
        parser = DiatomicParser()
        parser.feed(text)
        states = tuple(row for row in parser.rows if len(row) == 13 and TERM_PATTERN.search(row[0]))
        if len(states) != expected_counts[species]:
            raise RuntimeError(species + ": complete NIST state count changed")
        snapshot_path = str(path.relative_to(ROOT))
        snapshot_hash = file_hash(path)
        source_rows.append({
            "species": species,
            "nist_id": nist_id,
            "source_url": url,
            "snapshot_path": snapshot_path,
            "snapshot_hash": snapshot_hash,
            "state_row_count": len(states),
        })
        for ordinal, row in enumerate(states, start=1):
            target_id = "%s-nuclear-electronic-%03d" % (nist_id, ordinal)
            identities.append({
                "target_id": target_id,
                "species": species,
                "nist_id": nist_id,
                "nuclear_isotope_labels": list(isotopes),
                "state_row_ordinal": ordinal,
                "source_url": url,
                "snapshot_path": snapshot_path,
                "snapshot_hash": snapshot_hash,
            })
            targets.append({
                "target_id": target_id,
                "species": species,
                "nuclear_isotope_labels": list(isotopes),
                "molecular_weight_inscription": molecular_weight,
                "state_cells": list(row),
                "source_absent_cell_count": sum(cell == "" for cell in row),
                "snapshot_path": snapshot_path,
                "snapshot_hash": snapshot_hash,
            })
    if len(identities) != 95 or len(targets) != 95:
        raise RuntimeError("complete H2/HD/D2 surface must contain 95 rows")
    source = {
        "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-HD-D2-DIATOMIC-CONSTANTS-2026",
        "body": "National Institute of Standards and Technology",
        "database": "NIST Chemistry WebBook SRD 69",
        "doi": "10.18434/T4D303",
        "retrieval_date": "2026-07-26",
        "species": source_rows,
    }
    IDENTITIES.write_text(json.dumps({"schema": "sft-v3-nuclear-electronic-identities/1", "source": source, "rows": identities}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    TARGETS.write_text(json.dumps({"schema": "sft-v3-nuclear-electronic-withheld-targets/1", "source": source, "rows": targets}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("complete isotopologue state rows:", len(targets))
    print("source absent cells:", sum(row["source_absent_cell_count"] for row in targets))
    print("identity registry:", file_hash(IDENTITIES))
    print("withheld target registry:", file_hash(TARGETS))


if __name__ == "__main__":
    main()
