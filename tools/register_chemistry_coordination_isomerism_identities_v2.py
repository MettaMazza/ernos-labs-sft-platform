#!/usr/bin/env python3
"""Register the complete value-free INORG-005 comparison surface."""

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
ADDENDUM = ROOT / "experiments/external_sources/chemistry/inorg_005_linkage_source_identity_addendum_v1.json"
ADDENDUM_HASH = "sha256:da68d9c34165fb25c56c44d30b619804e42016a5ad29e4350f2e6fc6d185bac7"
ADDENDUM_INVENTORY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/source-inventory-v1.json"
ADDENDUM_INVENTORY_HASH = "sha256:3abde417b058f41574fefad5f26c2741fa6b462574601c74a69d4a49f4f3f12c"
PRELIMINARY = ROOT / "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v1.json"
PRELIMINARY_HASH = "sha256:52224a0a386431cc43129efe732acf6c46fe0c09ea3dacf586cc1e17e0c7d34c"
OUTPUT = ROOT / "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v2.json"


GOLD_BOOK_SURFACES = (
    "complete-source-file",
    "presented-term-identity",
    "complete-definition-surface",
    "source-citation-status-license-disclaimer-surface",
)
RED_BOOK_SURFACES = (
    "complete-source-file",
    "official-publication-identity-and-citation-surface",
    "coordination-compound-point-of-ligation-surface",
    "isomeric-donor-attachment-mode-surface",
    "explicit-linkage-term-presence-or-absence-status",
)


def main() -> None:
    for path, digest in (
        (FAMILY_REGISTRY, FAMILY_REGISTRY_HASH),
        (FAMILY_INVENTORY, FAMILY_INVENTORY_HASH),
        (ADDENDUM, ADDENDUM_HASH),
        (ADDENDUM_INVENTORY, ADDENDUM_INVENTORY_HASH),
        (PRELIMINARY, PRELIMINARY_HASH),
    ):
        if hash_file(path) != digest:
            raise SystemExit(f"VOID_INVALID_HALTED: registered INORG-005 authority changed: {path}")

    family = json.loads(FAMILY_REGISTRY.read_text(encoding="utf-8"))
    family_inventory = json.loads(FAMILY_INVENTORY.read_text(encoding="utf-8"))
    addendum = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    addendum_inventory = json.loads(ADDENDUM_INVENTORY.read_text(encoding="utf-8"))
    if (
        family.get("target_values_or_outcomes_present") is not False
        or addendum.get("target_values_or_outcomes_present") is not False
        or addendum.get("linkage_definition_example_class_formula_page_section_or_payload_present") is not False
    ):
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 identity boundary is not value-free")

    family_sources = {row["source_id"]: row for row in family["sources"]}
    family_captures = {row["source_id"]: row for row in family_inventory["rows"]}
    addendum_source = addendum["source"]
    addendum_capture = addendum_inventory["rows"][0]
    rows = []

    def add(source: dict, capture: dict, role: str) -> None:
        rows.append(
            {
                "target_id": f"SFT-CHEM-INORG005-ISOMER-{len(rows) + 1:03d}",
                "source_record_ordinal": len(rows) + 1,
                "authority": source["authority"],
                "source_id": source["source_id"],
                "registered_identity": source["identity"],
                "source_record_role": role,
                "source_locator": source["uri"],
                "snapshot_path": capture["snapshot_path"],
                "snapshot_sha256": capture["snapshot_sha256"],
            }
        )

    for source_id in ("IUPAC-I03294", "IUPAC-G02620", "IUPAC-O04308"):
        source = family_sources[source_id]
        for role in GOLD_BOOK_SURFACES:
            add(source, family_captures[source_id], role)
    for role in RED_BOOK_SURFACES:
        add(addendum_source, addendum_capture, role)

    if len(rows) != 17 or tuple(row["source_record_ordinal"] for row in rows) != tuple(range(1, 18)):
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 identity surface is incomplete")
    payload = {
        "schema": "sft-v3-coordination-isomerism-target-identities/2",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-005",
        "claim_id": "SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005",
        "family_identity_registry_sha256": FAMILY_REGISTRY_HASH,
        "family_source_inventory_sha256": FAMILY_INVENTORY_HASH,
        "linkage_identity_addendum_sha256": ADDENDUM_HASH,
        "linkage_source_inventory_sha256": ADDENDUM_INVENTORY_HASH,
        "preserved_incomplete_preliminary_identity_sha256": PRELIMINARY_HASH,
        "complete_registered_target_count": len(rows),
        "target_values_or_payload_hashes_present": False,
        "all_definition_class_example_formula_page_section_status_source_citation_license_disclaimer_and_target_payload_values_absent": True,
        "rows": rows,
    }
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"targets": len(rows), "identity_sha256": hash_file(OUTPUT)}, sort_keys=True))


if __name__ == "__main__":
    main()
