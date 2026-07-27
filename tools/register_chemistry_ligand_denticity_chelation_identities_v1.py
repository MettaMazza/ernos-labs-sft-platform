#!/usr/bin/env python3
"""Seal the complete value-free INORG-003 target identity surface."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


SPEC = ROOT / "experiments/external_sources/chemistry/ligand_denticity_chelation_capture_spec_v1.json"
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-003-ligand-denticity-chelation-v1"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/ligand_denticity_chelation_target_identities_v1.json"


DOCUMENTS = (
    ("iupac-binding-sites.json", "binding-sites"),
    ("iupac-chelation.json", "chelation"),
    ("iupac-denticity.json", "denticity"),
    ("iupac-eta.json", "eta"),
    ("iupac-kappa.json", "kappa"),
    ("iupac-ligands.json", "ligands"),
)
SURFACES = (
    "complete-current-term-record",
    "complete-definition-surface",
    "complete-example-and-boundary-surface",
    "complete-status-source-citation-license-and-disclaimer-surface",
)


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    by_name = {Path(row["snapshot_path"]).name: row for row in inventory["rows"]}
    rows = []
    ordinal = 1
    for document, term_role in DOCUMENTS:
        source = by_name[document]
        for surface in SURFACES:
            rows.append(
                {
                    "target_id": f"SFT-CHEM-INORG003-TOPOLOGY-{ordinal:03d}",
                    "source_record_ordinal": ordinal,
                    "authority": "IUPAC",
                    "source_document_identity": document,
                    "source_term_role": term_role,
                    "source_record_role": surface,
                    "source_locator": source["uri"],
                    "snapshot_path": source["snapshot_path"],
                    "snapshot_sha256": source["snapshot_sha256"],
                }
            )
            ordinal += 1
    payload = {
        "schema": "sft-v3-ligand-denticity-chelation-target-identities/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-003",
        "claim_id": "SFT-CHEM-LIGAND-DENTICITY-CHELATION-TOPOLOGY-003",
        "prefetch_spec_sha256": hash_file(SPEC),
        "source_inventory_sha256": hash_file(INVENTORY),
        "complete_registered_target_count": len(rows),
        "target_values_or_hashes_present": False,
        "all_definition_example_exclusion_topology_formula_status_source_citation_license_disclaimer_and_target_hash_values_absent": True,
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "identity_sha256": hash_file(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
