#!/usr/bin/env python3
"""Freeze the value-free and withheld PROP-004 ethanol torsion surfaces.

The byte-sealed NIST CCCBDB experimental internal-rotation page is reused as
the authoritative source.  Its fifty numerical rows remain in a post-seal
target vault; the public identity surface retains only molecule, state, ordered
four-atom carrier, rotor type, orientation, path position and recurrence role.
"""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


SNAPSHOT_PATH = Path("experiments/external_sources/chemistry/snapshots/configuration-order-v1/nist-cccbdb-ethanol-experimental-rotational-barrier.html")
SNAPSHOT_HASH = "sha256:afd9991078eac697439f353271666c9020d40f906bff78838c6cbe3696b14209"
IDENTITY_PATH = Path("experiments/external_sources/chemistry/dihedral_torsion_target_identities_v1.json")
TARGET_PATH = Path("experiments/external_sources/chemistry/dihedral_torsion_withheld_targets_v1.json")
SOURCE_ID = "NIST-CCCBDB-SRD101-ETHANOL-EXPERIMENTAL-ROTATIONAL-BARRIER"
SOURCE_URI = "https://cccbdb.nist.gov/exprotbar2x.asp?casno=64175&ti=1"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, ...]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.casefold() == "tr":
            self._row = []
        elif tag.casefold() in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            normalized = " ".join(data.split())
            if normalized:
                self._cell.append(normalized)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append("".join(self._cell))
            self._cell = None
        elif tag.casefold() == "tr" and self._row is not None:
            if self._row:
                self.rows.append(tuple(self._row))
            self._row = None
            self._cell = None


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    snapshot = ROOT / SNAPSHOT_PATH
    if hash_file(snapshot) != SNAPSHOT_HASH:
        raise SystemExit("PROP-004 NIST source identity changed")
    source_text = snapshot.read_text(encoding="utf-8", errors="replace")
    for required in (
        "internal rotation in gauche ethyl alcohol", "1980Kak/Qua:4300",
        "Atoms in torsion 1 are 1, 2, 3, 4", "The rotor type is OH",
        "Atoms in torsion 2 are 3, 2, 1, 5", "The rotor type is CH",
    ):
        if required.casefold() not in source_text.casefold():
            raise ValueError(f"PROP-004 source condition changed: {required}")
    parser = TableParser()
    parser.feed(source_text)
    raw = tuple(row for row in parser.rows if len(row) == 4 and row[0] in {"1", "2"} and row[1].isdigit())
    if len(raw) != 50:
        raise ValueError("PROP-004 complete fifty-row source surface is absent")
    specifications = {
        "1": {"torsion_label": "ethanol-OH-internal-rotation", "ordered_atoms": ("1", "2", "3", "4"), "rotor_type": "OH"},
        "2": {"torsion_label": "ethanol-CH3-internal-rotation", "ordered_atoms": ("3", "2", "1", "5"), "rotor_type": "CH3"},
    }
    identities: list[dict[str, object]] = []
    targets: list[dict[str, object]] = []
    ordinal_by_torsion = {"1": 0, "2": 0}
    for source_row in raw:
        torsion, angle, energy_kj, energy_cm = source_row
        ordinal_by_torsion[torsion] += 1
        position = ordinal_by_torsion[torsion]
        specification = specifications[torsion]
        coordinate_form = (
            "structural-EmptyOne-anchor" if position == 1
            else "recurrent-One" if position == 25
            else "positive-exact-turn-part"
        )
        target_id = f"ethanol-torsion-{torsion}-sector-{position:02d}"
        identities.append({
            "target_id": target_id,
            "species": "ethanol",
            "molecular_state": "gauche ethyl alcohol experimental internal-rotation record",
            "conformer_scope": "complete periodic internal-rotation path",
            "torsion_index": int(torsion),
            "torsion_label": specification["torsion_label"],
            "ordered_four_atom_carrier": specification["ordered_atoms"],
            "rotor_type": specification["rotor_type"],
            "held_orientation": "source-forward-periodic-order",
            "registered_sector_count": 24,
            "path_position": position,
            "coordinate_form": coordinate_form,
            "barrier_definition": "ordered-positive-Take-from-local-barrier-to-adjacent-conformer-minimum",
            "method_and_condition": "microwave rotational spectrum and internal rotation in gauche ethyl alcohol; 1980Kak/Qua:4300; NIST CCCBDB SRD 101 Release 22",
            "source_id": SOURCE_ID,
            "source_locator": SOURCE_URI,
            "snapshot_path": str(SNAPSHOT_PATH),
            "snapshot_hash": SNAPSHOT_HASH,
            "target_value_absent": True,
        })
        targets.append({
            "target_id": target_id,
            "torsion_index": int(torsion),
            "path_position": position,
            "angle_inscription_degrees": angle,
            "energy_inscription_kj_mol": energy_kj,
            "energy_inscription_cm_inverse": energy_cm,
            "source_zero_glyph_semantics": "absence from the least-energy state, represented natively by structural EmptyOne",
            "source_snapshot_hash": SNAPSHOT_HASH,
        })
    identity_document = {
        "schema": "sft-v3-dihedral-torsion-identities/1",
        "provenance": "observational_derivation",
        "development_measurements_already_known": True,
        "not_claimed_as_unknown-target-forward-prediction": True,
        "all_angle_and_energy_values_absent": True,
        "complete_registered_two_path_surface": True,
        "rows": identities,
    }
    target_document = {
        "schema": "sft-v3-dihedral-torsion-withheld-measurements/1",
        "identity_document_hash": sha256_identity(identity_document),
        "release_requires_prediction_seal": True,
        "source_zero_is_absence_glyph_only": True,
        "rows": targets,
    }
    write_json(ROOT / IDENTITY_PATH, identity_document)
    write_json(ROOT / TARGET_PATH, target_document)
    print(IDENTITY_PATH, hash_file(ROOT / IDENTITY_PATH))
    print(TARGET_PATH, hash_file(ROOT / TARGET_PATH))


if __name__ == "__main__":
    main()
