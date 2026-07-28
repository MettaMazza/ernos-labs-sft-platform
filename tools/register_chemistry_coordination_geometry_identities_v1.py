#!/usr/bin/env python3
"""Materialize the INORG-004 value-free comparison surface from sealed identities."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


FAMILY_REGISTRY = ROOT / "experiments/external_sources/chemistry/inorg_004_017_family_source_identity_registry_v1.json"
FAMILY_REGISTRY_HASH = "sha256:fce17d6e980696c8051f982ce0f4c8364520ea213f68153187253b96ec914bd2"
FAMILY_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/source-inventory-v1.json"
FAMILY_INVENTORY_HASH = "sha256:e03724f16e4866b43b5f3b53a6804588a2c86f5405bcda37cfb717e5724bb7c2"
CORRECTION = ROOT / "experiments/external_sources/chemistry/inorg_004_geometry_identity_correction_v1.json"
CORRECTION_HASH = "sha256:172d67b1a9854dd3ee3114cede27e047ed9a5b209d5ca0061ecc3b408066aeac"
CORRECTION_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-004-geometry-correction-v1/source-inventory-v1.json"
CORRECTION_INVENTORY_HASH = "sha256:86ea1c59187bcdd11efbee59e583ff4ad054acbea8a4c08391642b495ff340e6"
OUTPUT = ROOT / "experiments/external_sources/chemistry/coordination_geometry_target_identities_v1.json"


IUPAC_SURFACES = (
    "complete-source-file",
    "complete-definition-surface",
    "term-identity-and-status",
    "source-citation-license-disclaimer-surface",
)
ADVERSE_SURFACES = (
    "declared-target-identity",
    "complete-response-file",
    "identity-correspondence-status",
)
LIST_SURFACES = (
    "complete-source-file",
    "five-selected-target-identity-rows",
)
GEOMETRY_SURFACES = (
    "complete-response-file",
    "source-entity-identity",
    "point-group-inscription",
    "direct-bond-count-surface",
    "internal-coordinate-surface",
    "cartesian-coordinate-surface",
    "reference-and-absence-status-surface",
)


def main() -> None:
    expected = (
        (FAMILY_REGISTRY, FAMILY_REGISTRY_HASH),
        (FAMILY_INVENTORY, FAMILY_INVENTORY_HASH),
        (CORRECTION, CORRECTION_HASH),
        (CORRECTION_INVENTORY, CORRECTION_INVENTORY_HASH),
    )
    for path, digest in expected:
        if hash_file(path) != digest:
            raise SystemExit(f"VOID_INVALID_HALTED: registered INORG-004 authority changed: {path}")
    family_registry = json.loads(FAMILY_REGISTRY.read_text(encoding="utf-8"))
    family_inventory = json.loads(FAMILY_INVENTORY.read_text(encoding="utf-8"))
    correction = json.loads(CORRECTION.read_text(encoding="utf-8"))
    correction_inventory = json.loads(CORRECTION_INVENTORY.read_text(encoding="utf-8"))
    family_sources = {row["source_id"]: row for row in family_registry["sources"]}
    family_captures = {row["source_id"]: row for row in family_inventory["rows"]}
    correction_captures = {row["source_id"]: row for row in correction_inventory["rows"]}
    rows = []

    def add(source: dict, capture: dict, role: str) -> None:
        rows.append(
            {
                "target_id": f"SFT-CHEM-INORG004-GEOMETRY-{len(rows) + 1:03d}",
                "source_record_ordinal": len(rows) + 1,
                "authority": source["authority"],
                "source_id": source["source_id"],
                "source_document_identity": source["identity"],
                "source_record_role": role,
                "source_locator": source["uri"],
                "snapshot_path": capture["snapshot_path"],
                "snapshot_sha256": capture["snapshot_sha256"],
            }
        )

    iupac = family_sources["IUPAC-C01332"]
    for role in IUPAC_SURFACES:
        add(iupac, family_captures[iupac["source_id"]], role)

    for source_id in correction["original_adverse_source_ids"]:
        source = family_sources[source_id]
        for role in ADVERSE_SURFACES:
            add(source, family_captures[source_id], role)

    list_source = correction["sources"][0]
    for role in LIST_SURFACES:
        add(list_source, correction_captures[list_source["source_id"]], role)

    for source in correction["sources"][1:]:
        for role in GEOMETRY_SURFACES:
            add(source, correction_captures[source["source_id"]], role)

    if len(rows) != 53 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 54)):
        raise SystemExit("VOID_INVALID_HALTED: INORG-004 identity surface is incomplete")
    payload = {
        "schema": "sft-v3-coordination-geometry-target-identities/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-004",
        "claim_id": "SFT-CHEM-COORDINATION-GEOMETRY-HELD-ORIENTATION-004",
        "family_identity_registry_sha256": FAMILY_REGISTRY_HASH,
        "family_source_inventory_sha256": FAMILY_INVENTORY_HASH,
        "identity_correction_sha256": CORRECTION_HASH,
        "correction_source_inventory_sha256": CORRECTION_INVENTORY_HASH,
        "original_adverse_target_count": 4,
        "corrected_geometry_target_count": 5,
        "complete_registered_target_count": len(rows),
        "target_values_or_payload_hashes_present": False,
        "all_geometry_point_group_coordinate_distance_angle_definition_status_and_target_payload_values_absent": True,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "identity_sha256": hash_file(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
