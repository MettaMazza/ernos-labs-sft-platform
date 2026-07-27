#!/usr/bin/env python3
"""Freeze the complete post-seal external angle vector for Chemistry PROP-003.

The NIST CCCBDB species pages are retained byte-for-byte.  A separate identity
registry contains no angle values.  The numerical inscriptions are held in a
target document that the empirical validator may open only after sealing the
value-free Fold turn-fraction prediction.
"""

from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


SNAPSHOT_ROOT = Path("experiments/external_sources/chemistry/snapshots")
IDENTITY_PATH = Path("experiments/external_sources/chemistry/bond_angle_target_identities_v1.json")
TARGET_PATH = Path("experiments/external_sources/chemistry/bond_angle_withheld_targets_v1.json")


SOURCES = (
    {
        "species": "BF3",
        "cas_registry_number": "7637-07-2",
        "source_id": "NIST-CCCBDB-SRD101-BF3-EXPERIMENTAL-GEOMETRY",
        "url": "https://cccbdb.nist.gov/expgeom2x.asp?casno=7637072&charge=0",
        "snapshot": SNAPSHOT_ROOT / "prop-003-nist-cccbdb-bf3-v1.html",
        "point_group": "D3h",
        "geometry": "trigonal-planar-equal-three-sector",
        "required_text": ("Listing of experimental geometry data for BF", "Point Group D", "3h", "aFBF", "120", "1998Kuc"),
        "angles": (
            {
                "target_id": "NIST-CCCBDB-BF3-FBF-ADJACENT",
                "angle_definition": "F-B-F adjacent ligand-sector angle",
                "coordinate": "aFBF",
                "sector_count": 3,
                "sector_separation": 1,
                "inscription_degrees": "120",
                "source_comment": "1998Kuc experimental-geometry reference",
            },
        ),
    },
    {
        "species": "XeF2",
        "cas_registry_number": "13709-36-9",
        "source_id": "NIST-CCCBDB-SRD101-XEF2-EXPERIMENTAL-GEOMETRY",
        "url": "https://cccbdb.nist.gov/expgeom2x.asp?casno=13709369",
        "snapshot": SNAPSHOT_ROOT / "prop-003-nist-cccbdb-xef2-v1.html",
        "point_group": "D-infinity-h",
        "geometry": "linear-equal-two-sector",
        "required_text": ("Listing of experimental geometry data for XeF", "Point Group D", "infinity", "aFXeF", "180", "from symmetry"),
        "angles": (
            {
                "target_id": "NIST-CCCBDB-XEF2-FXEF-OPPOSITE",
                "angle_definition": "F-Xe-F opposite ligand-sector angle",
                "coordinate": "aFXeF",
                "sector_count": 2,
                "sector_separation": 1,
                "inscription_degrees": "180",
                "source_comment": "from symmetry",
            },
        ),
    },
    {
        "species": "XeF4",
        "cas_registry_number": "13709-61-0",
        "source_id": "NIST-CCCBDB-SRD101-XEF4-EXPERIMENTAL-GEOMETRY",
        "url": "https://cccbdb.nist.gov/expgeom2x.asp?casno=13709610",
        "snapshot": SNAPSHOT_ROOT / "prop-003-nist-cccbdb-xef4-v1.html",
        "point_group": "D4h",
        "geometry": "square-planar-equal-four-sector",
        "required_text": ("Listing of experimental geometry data for XeF", "Point Group D", "4h", "aFXeF", "90", "180", "by symmetry"),
        "angles": (
            {
                "target_id": "NIST-CCCBDB-XEF4-FXEF-ADJACENT",
                "angle_definition": "F-Xe-F adjacent ligand-sector angle",
                "coordinate": "aFXeF",
                "sector_count": 4,
                "sector_separation": 1,
                "inscription_degrees": "90",
                "source_comment": "by symmetry",
            },
            {
                "target_id": "NIST-CCCBDB-XEF4-FXEF-OPPOSITE",
                "angle_definition": "F-Xe-F opposite ligand-sector angle",
                "coordinate": "aFXeF",
                "sector_count": 4,
                "sector_separation": 2,
                "inscription_degrees": "180",
                "source_comment": "by symmetry",
            },
        ),
    },
)


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        normalized = " ".join(data.split())
        if normalized:
            self.parts.append(normalized)


def visible_text(payload: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    text = " | ".join(parser.parts)
    return text.replace("∞", "infinity")


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Ernos-Labs-SFT-v3-source-capture/1"})
    with urlopen(request, timeout=30) as response:
        payload = response.read()
    if len(payload) < 1000:
        raise ValueError(f"PROP-003 source response is unexpectedly short: {url}")
    return payload


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    identities: list[dict[str, object]] = []
    measurements: list[dict[str, object]] = []
    for source in SOURCES:
        payload = fetch(str(source["url"]))
        text = visible_text(payload)
        missing = tuple(fragment for fragment in source["required_text"] if str(fragment) not in text)
        if missing:
            raise ValueError(f"PROP-003 NIST source surface changed for {source['species']}: {missing}")
        snapshot = ROOT / source["snapshot"]
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_bytes(payload)
        snapshot_hash = hash_file(snapshot)
        for angle in source["angles"]:
            identities.append({
                "target_id": angle["target_id"],
                "species": source["species"],
                "cas_registry_number": source["cas_registry_number"],
                "molecular_state": "neutral CCCBDB experimental-geometry record",
                "geometry": source["geometry"],
                "point_group": source["point_group"],
                "angle_definition": angle["angle_definition"],
                "coordinate": angle["coordinate"],
                "sector_count": angle["sector_count"],
                "sector_separation": angle["sector_separation"],
                "method_and_condition": "NIST CCCBDB SRD 101 experimental geometry; gas-phase molecular identity retained",
                "source_comment": angle["source_comment"],
                "source_id": source["source_id"],
                "source_locator": source["url"],
                "snapshot_path": str(source["snapshot"]),
                "snapshot_hash": snapshot_hash,
                "target_value_absent": True,
            })
            measurements.append({
                "target_id": angle["target_id"],
                "species": source["species"],
                "coordinate": angle["coordinate"],
                "inscription": angle["inscription_degrees"],
                "unit": "degree",
                "observation_interval": {
                    "central": angle["inscription_degrees"],
                    "lower": angle["inscription_degrees"],
                    "upper": angle["inscription_degrees"],
                    "uncertainty_form": "source-absent-structural-EmptyOne",
                },
                "source_comment": angle["source_comment"],
                "source_snapshot_hash": snapshot_hash,
            })
    identity_document = {
        "schema": "sft-v3-molecular-bond-angle-identities/1",
        "provenance": "observational_derivation",
        "development_measurements_already_known": True,
        "not_claimed_as_unknown-target-forward-prediction": True,
        "all_measurement_values_absent": True,
        "complete_registered_carrier_vector": True,
        "rows": identities,
    }
    target_document = {
        "schema": "sft-v3-molecular-bond-angle-withheld-measurements/1",
        "identity_document_hash": sha256_identity(identity_document),
        "release_requires_prediction_seal": True,
        "source_resolution": "exact displayed degree inscription; uncertainty absent in source and represented by EmptyOne",
        "rows": measurements,
    }
    write_json(ROOT / IDENTITY_PATH, identity_document)
    write_json(ROOT / TARGET_PATH, target_document)
    for source in SOURCES:
        print(source["snapshot"], hash_file(ROOT / source["snapshot"]))
    print(IDENTITY_PATH, hash_file(ROOT / IDENTITY_PATH))
    print(TARGET_PATH, hash_file(ROOT / TARGET_PATH))


if __name__ == "__main__":
    main()
