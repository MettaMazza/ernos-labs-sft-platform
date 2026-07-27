#!/usr/bin/env python3
"""Seal the complete value-free INORG-001 target identity surface."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/coordination_entity_capture_spec_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-001-coordination-entity-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/coordination_entity_target_identities_v1.json"


RECORDS = (
    ("iupac-coordination-entity.json", "IUPAC", "coordination-entity-current-term"),
    ("iupac-central-atom.json", "IUPAC", "central-atom-current-term"),
    ("iupac-ligands.json", "IUPAC", "ligands-current-term"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-complete-page"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-entity-identity"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-point-group"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-C-Fe-link-count"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-C-O-link-count"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-internal-coordinate-record"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-coordinate-table"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-reference-record"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-rotational-data-status"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-complete-page"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-entity-identity"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-point-group"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-C-Fe-link-count"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-C-C-link-count"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-H-C-link-count"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-coordinate-data-status"),
    ("nist-cccbdb-ferrocene-experimental-geometry.html", "NIST-CCCBDB", "ferrocene-rotational-data-status"),
)


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    by_name = {Path(row["snapshot_path"]).name: row for row in inventory["rows"]}
    rows = []
    for ordinal, (document, authority, role) in enumerate(RECORDS, start=1):
        source = by_name[document]
        rows.append({
            "target_id": f"SFT-CHEM-INORG001-STRUCTURE-{ordinal:03d}",
            "source_record_ordinal": ordinal,
            "authority": authority,
            "source_document_identity": document,
            "source_record_role": role,
            "source_locator": source["uri"],
            "snapshot_path": source["snapshot_path"],
            "snapshot_sha256": source["snapshot_sha256"],
        })
    payload = {
        "schema": "sft-v3-coordination-entity-target-identities/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-001",
        "claim_id": "SFT-CHEM-COORDINATION-ENTITY-RETAINED-IDENTITY-001",
        "prefetch_spec_sha256": hash_file(SPEC),
        "source_inventory_sha256": hash_file(INVENTORY),
        "complete_registered_target_count": len(rows),
        "target_values_or_hashes_present": False,
        "all_definition_formula_point_group_link_count_coordinate_reference_and_limitation_values_absent": True,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "identity_sha256": hash_file(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
