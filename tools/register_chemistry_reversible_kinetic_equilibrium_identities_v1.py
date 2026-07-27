#!/usr/bin/env python3
"""Register the complete KIN-009 source topology without opening measurement content."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_capture_spec_v1.json"
SPEC_HASH = "sha256:cc936c64ac170830e26ec3fece37d246511b5e76e895c90db82ccaca4a5d3152"
INVENTORY_PATH = ROOT / "experiments/external_sources/chemistry/snapshots/kin-009-reversible-kinetic-equilibrium-v1/source-inventory-v1.json"
INVENTORY_HASH = "sha256:5d7c24d3d62d2b3217a62e7e3f34be9e7425c2d5a3f65ed6acb7b7a404542722"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/reversible_kinetic_equilibrium_target_identities_v1.json"


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if sha_file(SPEC_PATH) != SPEC_HASH or sha_file(INVENTORY_PATH) != INVENTORY_HASH:
        raise ValueError("KIN-009 prefetch or source inventory changed")
    inventory = json.loads(INVENTORY_PATH.read_text())
    archive = tuple(inventory.get("source_data_archive_topology_only", ()))
    if (
        inventory.get("archive_member_content_values_or_hashes_present") is not False
        or len(archive) != 8
        or tuple(row["source_member_ordinal"] for row in archive) != tuple(range(1, 9))
    ):
        raise ValueError("KIN-009 complete value-free archive topology changed")
    rows = []
    ordinal = 1
    for document_identity, page_count, record_class in (
        ("article.pdf", 10, "complete-primary-article-page"),
        ("supplementary-information.pdf", 144, "complete-supplementary-information-page"),
        ("additional-file-description.pdf", 1, "complete-additional-file-description-page"),
    ):
        for page in range(1, page_count + 1):
            rows.append({
                "target_id": f"SFT-CHEM-KIN009-COMPLETE-SOURCE-RECORD-{ordinal:03d}",
                "source_id": "NATURE-COMMUNICATIONS-S41467-023-40190-4-COMPLETE",
                "article_doi": "10.1038/s41467-023-40190-4",
                "reversible_system_identity": "complete-macrocycle-2-and-motor-3-reversible-isomerization-surface",
                "source_document_identity": document_identity,
                "source_record_identity": f"page-{page:03d}",
                "source_record_ordinal": ordinal,
                "source_page_ordinal": page,
                "source_record_class": record_class,
            })
            ordinal += 1
    rows.append({
        "target_id": f"SFT-CHEM-KIN009-COMPLETE-SOURCE-RECORD-{ordinal:03d}",
        "source_id": "NATURE-COMMUNICATIONS-S41467-023-40190-4-COMPLETE",
        "article_doi": "10.1038/s41467-023-40190-4",
        "reversible_system_identity": "complete-macrocycle-2-and-motor-3-reversible-isomerization-surface",
        "source_document_identity": "supplementary-movie.gif",
        "source_record_identity": "complete-supplementary-movie",
        "source_record_ordinal": ordinal,
        "source_page_ordinal": "structural-EmptyOne-not-a-paged-record",
        "source_record_class": "complete-supplementary-movie",
    })
    ordinal += 1
    for member in archive:
        rows.append({
            "target_id": f"SFT-CHEM-KIN009-COMPLETE-SOURCE-RECORD-{ordinal:03d}",
            "source_id": "NATURE-COMMUNICATIONS-S41467-023-40190-4-COMPLETE",
            "article_doi": "10.1038/s41467-023-40190-4",
            "reversible_system_identity": "complete-macrocycle-2-and-motor-3-reversible-isomerization-surface",
            "source_document_identity": "source-data.zip",
            "source_record_identity": member["source_member_identity"],
            "source_record_ordinal": ordinal,
            "source_page_ordinal": "structural-EmptyOne-archive-member",
            "source_record_class": "complete-source-data-archive-member",
            "source_member_ordinal": member["source_member_ordinal"],
            "declared_uncompressed_byte_count": member["declared_uncompressed_byte_count"],
            "declared_compressed_byte_count": member["declared_compressed_byte_count"],
            "archive_directory_entry": member["archive_directory_entry"],
        })
        ordinal += 1
    if len(rows) != 164 or ordinal != 165:
        raise ValueError("KIN-009 complete source-record identity count changed")
    document = {
        "schema": "sft-v3-reversible-kinetic-equilibrium-value-free-target-identities/1",
        "claim_id": "SFT-CHEM-REVERSIBLE-KINETIC-EQUILIBRIUM-CORRESPONDENCE-009",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-009",
        "prefetch_spec_hash": SPEC_HASH,
        "source_inventory_hash": INVENTORY_HASH,
        "complete_registered_target_count": len(rows),
        "complete_primary_article_page_count": 10,
        "complete_supplementary_information_page_count": 144,
        "complete_additional_description_page_count": 1,
        "complete_supplementary_movie_count": 1,
        "complete_source_data_archive_member_count": 8,
        "all_state_pair_direction_time_equilibrium_composition_rate_quantum_yield_condition_uncertainty_fit_calculation_status_value_and_target_hash_values_absent": True,
        "target_values_or_hashes_present": False,
        "rows": rows,
    }
    IDENTITY_PATH.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "identity_path": str(IDENTITY_PATH.relative_to(ROOT)),
        "identity_hash": sha_file(IDENTITY_PATH),
        "complete_registered_target_count": len(rows),
    }, indent=2))


if __name__ == "__main__":
    main()
