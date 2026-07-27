#!/usr/bin/env python3
"""Register the complete KIN-008 workbook topology without opening cell values."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/parallel_mechanism_capture_spec_v1.json"
SPEC_HASH = "sha256:f32b98d3cc4f02c02f01249b0f92ce799d1453ae04d1f8c9c107be6a509a6e89"
INVENTORY_PATH = ROOT / "experiments/external_sources/chemistry/snapshots/kin-008-parallel-mechanism-v1/source-inventory-v1.json"
INVENTORY_HASH = "sha256:a3c79878aeb0383a64d8bcf9242e9865c791c872ac50f59692348b978cead0d0"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/parallel_mechanism_target_identities_v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH or sha_file(INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("KIN-008 prefetch or source inventory changed")
    inventory = json.loads(INVENTORY_PATH.read_text())
    topology = tuple(inventory.get("workbook_topology_only", ()))
    if (
        inventory.get("worksheet_cell_values_or_hashes_present") is not False
        or len(topology) != 28
        or tuple(row.get("source_sheet_ordinal") for row in topology) != tuple(range(1, 29))
    ):
        raise ValueError("KIN-008 complete value-free workbook topology changed")
    rows = []
    for sheet in topology:
        ordinal = sheet["source_sheet_ordinal"]
        rows.append({
            "target_id": f"SFT-CHEM-KIN008-COMPLETE-SOURCE-SHEET-{ordinal:03d}",
            "source_id": "NATURE-COMMUNICATIONS-S41467-026-70199-4-SOURCE-DATA",
            "article_doi": "10.1038/s41467-026-70199-4",
            "reaction_surface_identity": "complete-article-source-data-workbook",
            "measurement_identity": f"complete-worksheet-{ordinal:03d}",
            "source_sheet_identity": sheet["source_sheet_identity"],
            "source_sheet_ordinal": ordinal,
            "declared_max_row": sheet["declared_max_row"],
            "declared_max_column": sheet["declared_max_column"],
            "source_record_class": "complete-source-data-worksheet-with-every-rectangular-cell-position-retained",
        })
    document = {
        "schema": "sft-v3-parallel-mechanism-value-free-target-identities/1",
        "claim_id": "SFT-CHEM-PARALLEL-MECHANISM-COMPOSITION-008",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-008",
        "prefetch_spec_hash": SPEC_HASH,
        "source_inventory_hash": INVENTORY_HASH,
        "complete_registered_target_count": len(rows),
        "complete_registered_rectangular_cell_position_count": sum(
            row["declared_max_row"] * row["declared_max_column"] for row in rows
        ),
        "all_sheet_cell_label_time_product_concentration_replicate_uncertainty_status_value_and_target_hash_values_absent": True,
        "target_values_or_hashes_present": False,
        "rows": rows,
    }
    IDENTITY_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "identity_path": str(IDENTITY_PATH.relative_to(ROOT)),
        "identity_hash": sha_file(IDENTITY_PATH),
        "complete_registered_target_count": len(rows),
        "complete_registered_rectangular_cell_position_count": document["complete_registered_rectangular_cell_position_count"],
    }, indent=2))


if __name__ == "__main__":
    main()
