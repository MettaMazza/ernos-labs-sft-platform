#!/usr/bin/env python3
"""Capture the registered NIST diatomic electron/spin validation corpus.

The registry below contains only pre-target molecular identity, nuclear
composition and held charge transfer.  Electronic state terms and their
multiplicities are parsed from the byte snapshots into a separate target file;
neither value is present in the derivation or prediction input registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIRECTORY = ROOT / "experiments/external_sources/chemistry/snapshots/electron-spin-v1"
INPUT_REGISTRY = ROOT / "experiments/external_sources/chemistry/electron_spin_inputs_v1.json"
TARGET_REGISTRY = ROOT / "experiments/external_sources/chemistry/electron_spin_withheld_targets_v1.json"
SOURCE_ID = "NIST-CHEMISTRY-WEBBOOK-SRD69-DIATOMIC-CONSTANTS-2025"
SOURCE_DOI = "10.18434/T4D303"
RETRIEVAL_DATE = date(2026, 7, 26).isoformat()


@dataclass(frozen=True)
class SpeciesInput:
    row_id: str
    nist_id: str
    composition: tuple[tuple[str, int, int], ...]
    charge_action: str
    charge_count: int | None


SPECIES = (
    SpeciesInput("hydrogen-neutral", "C1333740", (("H", 1, 2),), "empty-One", None),
    SpeciesInput("nitrogen-neutral", "C7727379", (("N", 7, 2),), "empty-One", None),
    SpeciesInput("oxygen-neutral", "C7782447", (("O", 8, 2),), "empty-One", None),
    SpeciesInput("fluorine-neutral", "C7782414", (("F", 9, 2),), "empty-One", None),
    SpeciesInput("carbon-monoxide-neutral", "C630080", (("C", 6, 1), ("O", 8, 1)), "empty-One", None),
    SpeciesInput("nitric-oxide-neutral", "C10102439", (("N", 7, 1), ("O", 8, 1)), "empty-One", None),
    SpeciesInput("hydroxyl-neutral", "C3352576", (("H", 1, 1), ("O", 8, 1)), "empty-One", None),
    SpeciesInput("imidogen-neutral", "C13774920", (("H", 1, 1), ("N", 7, 1)), "empty-One", None),
    SpeciesInput("methylidyne-neutral", "C3315375", (("C", 6, 1), ("H", 1, 1)), "empty-One", None),
    SpeciesInput("chlorine-neutral", "C7782505", (("Cl", 17, 2),), "empty-One", None),
    SpeciesInput("silicon-monoxide-neutral", "C10097286", (("O", 8, 1), ("Si", 14, 1)), "empty-One", None),
    SpeciesInput("sulfur-monoxide-neutral", "C13827322", (("O", 8, 1), ("S", 16, 1)), "empty-One", None),
    SpeciesInput("hydrogen-fluoride-neutral", "C7664393", (("F", 9, 1), ("H", 1, 1)), "empty-One", None),
    SpeciesInput("hydrogen-chloride-neutral", "C7647010", (("Cl", 17, 1), ("H", 1, 1)), "empty-One", None),
    SpeciesInput("hydrogen-bromide-neutral", "C10035106", (("Br", 35, 1), ("H", 1, 1)), "empty-One", None),
    SpeciesInput("iodine-neutral", "C7553562", (("I", 53, 2),), "empty-One", None),
    SpeciesInput("hydrogen-cation", "C12184906", (("H", 1, 2),), "remove-electron", 1),
    SpeciesInput("nitrogen-cation", "C13966046", (("N", 7, 2),), "remove-electron", 1),
    SpeciesInput("oxygen-cation", "C12185078", (("O", 8, 2),), "remove-electron", 1),
    SpeciesInput("nitric-oxide-cation", "C14452938", (("N", 7, 1), ("O", 8, 1)), "remove-electron", 1),
    SpeciesInput("oxygen-anion", "C11062774", (("O", 8, 2),), "adjoin-electron", 1),
    SpeciesInput("nitric-oxide-anion", "C14967783", (("N", 7, 1), ("O", 8, 1)), "adjoin-electron", 1),
)


class NistParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._data_table_depth = 0
        self._row = False
        self._cell = False
        self._cell_text: list[str] = []
        self._cells: list[str] = []
        self.rows: list[list[str]] = []
        self._json_script = False
        self._json_text: list[str] = []
        self.json_documents: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._json_script = True
            self._json_text = []
        if tag == "table" and "data" in (attributes.get("class") or "").split():
            self._data_table_depth += 1
        elif self._data_table_depth and tag == "tr":
            self._row = True
            self._cells = []
        elif self._row and tag in {"td", "th"}:
            self._cell = True
            self._cell_text = []
        elif self._cell and tag == "sup":
            self._cell_text.append("^")
        elif self._cell and tag == "sub":
            self._cell_text.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_script:
            try:
                document = json.loads("".join(self._json_text))
            except json.JSONDecodeError:
                document = None
            if isinstance(document, dict):
                self.json_documents.append(document)
            self._json_script = False
        if self._cell and tag in {"td", "th"}:
            self._cells.append(" ".join(unescape("".join(self._cell_text)).split()))
            self._cell = False
        elif self._row and tag == "tr":
            if self._cells:
                self.rows.append(self._cells)
            self._row = False
        elif self._data_table_depth and tag == "table":
            self._data_table_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._json_script:
            self._json_text.append(data)
        if self._cell:
            self._cell_text.append(data)


def sha256_file(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def source_url(nist_id: str) -> str:
    return f"https://webbook.nist.gov/cgi/cbook.cgi?ID={nist_id}&Mask=1000"


def capture(species: SpeciesInput) -> tuple[dict[str, object], dict[str, object]]:
    url = source_url(species.nist_id)
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-open-research/1.0"})
    payload = urlopen(request, timeout=45).read()
    text = payload.decode("utf-8")
    if "NIST Chemistry WebBook" not in text or "Constants of diatomic molecules" not in text:
        raise RuntimeError(f"{species.row_id}: official NIST diatomic record is absent")
    snapshot = SNAPSHOT_DIRECTORY / f"{species.nist_id}.html"
    snapshot.write_bytes(payload)
    snapshot_hash = sha256_file(snapshot)

    parser = NistParser()
    parser.feed(text)
    formula_rows = [row.get("molecularFormula") for row in parser.json_documents if row.get("molecularFormula")]
    if len(set(formula_rows)) != 1:
        raise RuntimeError(f"{species.row_id}: molecular formula is not uniquely reproduced")
    state_rows = [row for row in parser.rows if row and re.match(r"^X(?:\s|\^)", row[0])]
    if not state_rows:
        raise RuntimeError(f"{species.row_id}: NIST X-state row is absent")
    state_term = state_rows[0][0]
    multiplicity_match = re.search(r"\^(\d+)", state_term)
    if multiplicity_match is None:
        raise RuntimeError(f"{species.row_id}: X-state multiplicity is not explicit")
    multiplicity = int(multiplicity_match.group(1))
    if multiplicity < 1:
        raise RuntimeError(f"{species.row_id}: multiplicity is not positive")

    input_row = {
        "row_id": species.row_id,
        "nist_id": species.nist_id,
        "source_url": url,
        "snapshot_path": str(snapshot.relative_to(ROOT)),
        "snapshot_hash": snapshot_hash,
        "molecular_formula": formula_rows[0],
        "nuclear_composition": [
            {"element_symbol": symbol, "atomic_number": atomic_number, "occurrence_count": occurrence_count}
            for symbol, atomic_number, occurrence_count in species.composition
        ],
        "charge_action": species.charge_action,
        "charge_count": species.charge_count,
    }
    target_row = {
        "row_id": species.row_id,
        "nist_id": species.nist_id,
        "source_url": url,
        "snapshot_path": str(snapshot.relative_to(ROOT)),
        "snapshot_hash": snapshot_hash,
        "ground_state_term": state_term,
        "measured_multiplicity": multiplicity,
        "term_energy_record": state_rows[0][1] if len(state_rows[0]) > 1 else "",
        "extraction_rule": "first NIST diatomic State row whose state identifier is X; multiplicity is the leading superscript",
    }
    return input_row, target_row


def main() -> None:
    if len({row.row_id for row in SPECIES}) != len(SPECIES) or len({row.nist_id for row in SPECIES}) != len(SPECIES):
        raise RuntimeError("registered species identities are not unique")
    SNAPSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    input_rows = []
    target_rows = []
    for species in SPECIES:
        input_row, target_row = capture(species)
        input_rows.append(input_row)
        target_rows.append(target_row)
        print(f"captured {species.row_id}: {target_row['ground_state_term']}")
    source = {
        "source_id": SOURCE_ID,
        "body": "National Institute of Standards and Technology",
        "database": "NIST Chemistry WebBook, Standard Reference Database 69",
        "doi": SOURCE_DOI,
        "last_data_update": "March 2025",
        "retrieval_date": RETRIEVAL_DATE,
    }
    INPUT_REGISTRY.write_text(
        json.dumps({"schema": "sft-v3-electron-spin-inputs/1", "source": source, "rows": input_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    TARGET_REGISTRY.write_text(
        json.dumps({"schema": "sft-v3-electron-spin-withheld-targets/1", "source": source, "rows": target_rows}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"input rows: {len(input_rows)}")
    print(f"withheld target rows: {len(target_rows)}")
    print(f"input registry: {sha256_file(INPUT_REGISTRY)}")
    print(f"target registry: {sha256_file(TARGET_REGISTRY)}")


if __name__ == "__main__":
    main()
