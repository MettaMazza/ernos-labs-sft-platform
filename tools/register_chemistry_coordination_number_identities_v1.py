#!/usr/bin/env python3
"""Seal the complete value-free INORG-002 target identity surface."""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from sft.engine.source import hash_file  # noqa: E402

SPEC = ROOT / "experiments/external_sources/chemistry/coordination_number_capture_spec_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-002-coordination-number-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/coordination_number_target_identities_v1.json"

RECORDS = (
    ("iupac-coordination-number.json", "IUPAC", "complete-current-term-record"),
    ("iupac-coordination-number.json", "IUPAC", "general-direct-link-definition"),
    ("iupac-coordination-number.json", "IUPAC", "inorganic-sigma-link-definition"),
    ("iupac-coordination-number.json", "IUPAC", "crystallographic-sense-boundary"),
    ("iupac-coordination-number.json", "IUPAC", "pi-link-exclusion-boundary"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-complete-page"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-entity-identity"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-point-group"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-direct-link-count"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-coordinate-data-status"),
    ("nist-cccbdb-scandium-trifluoride-experimental-geometry.html", "NIST-CCCBDB", "ScF3-rotational-data-status"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-complete-page"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-entity-identity"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-point-group"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-direct-link-count"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-internal-coordinate-record"),
    ("nist-cccbdb-titanium-tetrachloride-experimental-geometry.html", "NIST-CCCBDB", "TiCl4-rotational-data-status"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-complete-page"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-entity-identity"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-point-group"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-direct-link-count"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-internal-coordinate-record"),
    ("nist-cccbdb-iron-pentacarbonyl-experimental-geometry.html", "NIST-CCCBDB", "FeCO5-rotational-data-status"),
)

def main() -> None:
    inventory = json.loads(INVENTORY.read_text())
    by_name = {Path(row["snapshot_path"]).name: row for row in inventory["rows"]}
    rows = []
    for ordinal, (document, authority, role) in enumerate(RECORDS, start=1):
        source = by_name[document]
        rows.append({"target_id": f"SFT-CHEM-INORG002-COUNT-{ordinal:03d}", "source_record_ordinal": ordinal, "authority": authority, "source_document_identity": document, "source_record_role": role, "source_locator": source["uri"], "snapshot_path": source["snapshot_path"], "snapshot_sha256": source["snapshot_sha256"]})
    payload = {"schema": "sft-v3-coordination-number-target-identities/1", "chemistry_obligation": "SFT-CHEM-OBL-INORG-002", "claim_id": "SFT-CHEM-COORDINATION-NUMBER-INCIDENCE-COUNT-002", "prefetch_spec_sha256": hash_file(SPEC), "source_inventory_sha256": hash_file(INVENTORY), "complete_registered_target_count": len(rows), "target_values_or_hashes_present": False, "all_definition_formula_point_group_link_count_coordinate_limitation_values_absent": True, "rows": rows}
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"targets": len(rows), "identity_sha256": hash_file(OUTPUT)}, sort_keys=True))

if __name__ == "__main__":
    main()
