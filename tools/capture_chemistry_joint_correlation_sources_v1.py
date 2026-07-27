#!/usr/bin/env python3
"""Capture primary dissociation records for ELEC-007 joint correlation support."""

from __future__ import annotations

from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
APS_PATH = "experiments/external_sources/chemistry/snapshots/aps-hydrogen-dissociation-1994.json"
APS_HASH = "sha256:9c41d01395090b18b2eb8b1223e9cb430d9309f79d1a0324b092a5ed8c1b6953"
NIST_PATH = "experiments/external_sources/chemistry/snapshots/electron-spin-v1/C1333740.html"
NIST_HASH = "sha256:410fae804b1fa35ab72d829d95bd3b26c831dde2f0ec0078b614fea2c87d795e"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/joint_correlation_target_identities_v1.json"
TARGETS = ROOT / "experiments/external_sources/chemistry/joint_correlation_withheld_targets_v1.json"


def file_hash(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


class NoteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_row = False
        self.note_id: Optional[str] = None
        self.parts: list[str] = []
        self.notes: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        attributes = dict(attrs)
        if tag == "tr":
            self.in_row, self.note_id, self.parts = True, None, []
        elif self.in_row and tag == "a" and str(attributes.get("id", "")).startswith("Dia"):
            self.note_id = str(attributes["id"])
        elif self.in_row and tag == "sup":
            self.parts.append("^")
        elif self.in_row and tag == "sub":
            self.parts.append("_")

    def handle_endtag(self, tag: str) -> None:
        if tag == "tr" and self.in_row:
            if self.note_id is not None:
                self.notes[self.note_id] = " ".join(unescape("".join(self.parts)).split())
            self.in_row = False

    def handle_data(self, data: str) -> None:
        if self.in_row:
            self.parts.append(data)


def main() -> None:
    if file_hash(ROOT / APS_PATH) != APS_HASH or file_hash(ROOT / NIST_PATH) != NIST_HASH:
        raise RuntimeError("ELEC-007 primary-source bytes changed")
    aps = json.loads((ROOT / APS_PATH).read_text(encoding="utf-8"))
    if aps.get("schema") != "sft-v3-primary-source-numeric-extract/1" or len(aps.get("records", ())) != 6:
        raise RuntimeError("ELEC-007 APS record surface is incomplete")
    parser = NoteParser()
    parser.feed((ROOT / NIST_PATH).read_text(encoding="utf-8"))
    note111 = parser.notes.get("Dia111", "")
    note125 = parser.notes.get("Dia125", "")
    for fragment, note in (
        ("118377._6", note111),
        ("28174.2", note111),
        ("36118.3 ± 0.5", note125),
    ):
        if fragment not in note:
            raise RuntimeError("ELEC-007 NIST dissociation inscription is absent")

    identities = []
    targets = []
    for ordinal, record in enumerate(aps["records"], start=1):
        target_id = f"APS-HYDROGEN-DISSOCIATION-{ordinal:03d}"
        identities.append(
            {
                "target_id": target_id,
                "source_id": "APS-PRA-49-2460-1994",
                "record_ordinal": ordinal,
                "snapshot_path": APS_PATH,
                "snapshot_hash": APS_HASH,
                "source_url": aps["source"]["url"],
            }
        )
        targets.append(
            {
                "target_id": target_id,
                "source_id": "APS-PRA-49-2460-1994",
                "species": record["species"],
                "state": record["state"],
                "record_kind": record["kind"],
                "value_inscription": record["value_inscription"],
                "value_numerator": record["value_numerator"],
                "value_denominator": record["value_denominator"],
                "uncertainty_inscription": record["uncertainty_inscription"],
                "uncertainty_numerator": record["uncertainty_numerator"],
                "uncertainty_denominator": record["uncertainty_denominator"],
                "unit": record["unit"],
                "joint_support_role": "bound-state-to-separated-product-support",
                "snapshot_path": APS_PATH,
                "snapshot_hash": APS_HASH,
            }
        )

    nist_records = (
        {
            "note_id": "Dia111",
            "species": "H2",
            "state": "B-state-dissociation-limit",
            "record_kind": "compiled_observed_dissociation_limit",
            "value_inscription": "118377._6",
            "value_numerator": 1183776,
            "value_denominator": 10,
            "uncertainty_inscription": "absence",
            "joint_support_role": "bound-excited-state-to-separated-product-support",
        },
        {
            "note_id": "Dia111",
            "species": "H2",
            "state": "B-state",
            "record_kind": "compiled_dissociation_energy",
            "value_inscription": "28174.2",
            "value_numerator": 281742,
            "value_denominator": 10,
            "uncertainty_inscription": "absence",
            "joint_support_role": "bound-excited-state-to-separated-product-support",
        },
        {
            "note_id": "Dia125",
            "species": "H2",
            "state": "X-ground",
            "record_kind": "measured_upper_limit",
            "value_inscription": "36118.3",
            "value_numerator": 361183,
            "value_denominator": 10,
            "uncertainty_inscription": "0.5",
            "uncertainty_numerator": 5,
            "uncertainty_denominator": 10,
            "joint_support_role": "bound-ground-state-to-separated-product-support",
        },
    )
    for ordinal, record in enumerate(nist_records, start=1):
        target_id = f"NIST-H2-DISSOCIATION-{ordinal:03d}"
        identities.append(
            {
                "target_id": target_id,
                "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-DISSOCIATION",
                "note_id": record["note_id"],
                "snapshot_path": NIST_PATH,
                "snapshot_hash": NIST_HASH,
                "source_url": "https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740&Mask=1000",
            }
        )
        targets.append(
            {
                "target_id": target_id,
                "source_id": "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-DISSOCIATION",
                "species": record["species"],
                "state": record["state"],
                "record_kind": record["record_kind"],
                "value_inscription": record["value_inscription"],
                "value_numerator": record["value_numerator"],
                "value_denominator": record["value_denominator"],
                "uncertainty_inscription": record["uncertainty_inscription"],
                "uncertainty_numerator": record.get("uncertainty_numerator", "absence"),
                "uncertainty_denominator": record.get("uncertainty_denominator", "absence"),
                "unit": "inverse-centimetre",
                "joint_support_role": record["joint_support_role"],
                "source_note_id": record["note_id"],
                "source_note_text": parser.notes[record["note_id"]],
                "snapshot_path": NIST_PATH,
                "snapshot_hash": NIST_HASH,
            }
        )
    if len(identities) != 9 or len(targets) != 9:
        raise RuntimeError("ELEC-007 complete dissociation vector must contain nine records")
    if any(int(row["value_numerator"]) < 1 or int(row["value_denominator"]) < 1 for row in targets):
        raise RuntimeError("ELEC-007 dissociation values must remain exact positive records")
    source = {
        "source_ids": ["APS-PRA-49-2460-1994", "NIST-CHEMISTRY-WEBBOOK-SRD69-H2-DISSOCIATION"],
        "primary_measurement_body": "American Physical Society",
        "measurement_doi": "10.1103/PhysRevA.49.2460",
        "reference_body": "National Institute of Standards and Technology",
        "reference_doi": "10.18434/T4D303",
        "retrieval_date": "2026-07-26",
    }
    IDENTITIES.write_text(
        json.dumps(
            {"schema": "sft-v3-joint-correlation-identities/1", "source": source, "rows": identities},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    TARGETS.write_text(
        json.dumps(
            {"schema": "sft-v3-joint-correlation-withheld-targets/1", "source": source, "rows": targets},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print("dissociation records:", len(targets))
    print(
        "direct measured/compiled records:",
        sum(
            row["record_kind"]
            in {
                "measured_dissociation_threshold",
                "measured_ground_state_dissociation_energy",
                "compiled_observed_dissociation_limit",
                "compiled_dissociation_energy",
                "measured_upper_limit",
            }
            for row in targets
        ),
    )
    print("derived ion records:", sum(row["record_kind"] == "derived_from_measured-neutral-and-ionization-intervals" for row in targets))
    print("identity registry:", file_hash(IDENTITIES))
    print("withheld target registry:", file_hash(TARGETS))


if __name__ == "__main__":
    main()
