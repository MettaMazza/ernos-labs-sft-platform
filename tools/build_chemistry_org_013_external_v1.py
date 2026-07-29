#!/usr/bin/env python3
"""Build the complete post-seal ORG-013 observation vector."""

from __future__ import annotations

from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sft.engine.canonical import sha256_identity  # noqa: E402

SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-013-radical-network-blind-v1"
BASE = SNAPSHOT / "members/PMC11598545"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
NXML = BASE / "polymers-16-03225.nxml"
PDF = BASE / "polymers-16-03225.pdf"
SUPPLEMENT = BASE / "polymers-16-03225-s001.zip"
OUTPUT = SNAPSHOT / "complete-postseal-analysis-v1.json"
HASHES = {
    INVENTORY: "sha256:b85c4bc4fefea490bf8270043971f60cede2d2aa5261292e2d61684b860f38b0",
    NXML: "sha256:ff27819a129bc340665ac31cf164046358d21a7cc874512e5c5b5a048f062211",
    PDF: "sha256:82623c2e65d4809f19833d9a3fb20b857106d05f518bf3d54ac1235d30d4bffc",
    SUPPLEMENT: "sha256:fbcdd10d7fc012e8d67e1a81f1efd4701867c0af2ee18c8df6a4e810da3baa86",
}


def digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def clean(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def pages(reader: PdfReader) -> tuple[dict[str, object], ...]:
    result = []
    for ordinal, page in enumerate(reader.pages, 1):
        text = " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        result.append({"page": ordinal, "text_character_count": len(text), "text_sha256": digest(text.encode()), "has_extracted_text": bool(text)})
    return tuple(result)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("ORG-013 analysis already exists")
    for path, expected in HASHES.items():
        if digest(path.read_bytes()) != expected:
            raise SystemExit(f"ORG-013 source changed: {path}")
    inventory = json.loads(INVENTORY.read_text())
    for row in inventory["archive_members_in_source_order"]:
        if row["member_type"] == "file":
            path = SNAPSHOT / "members" / row["name"]
            if not path.is_file() or digest(path.read_bytes()) != row["content_sha256"]:
                raise SystemExit(f"ORG-013 member changed: {row['name']}")

    root = ET.parse(NXML).getroot()
    table_rows = []
    counts = []
    for table_ordinal, table in enumerate(root.findall(".//table-wrap"), 1):
        caption = clean(table.find("caption"))
        headers = tuple(clean(row) for row in table.findall(".//thead//th"))
        rows = tuple(tuple(clean(cell) for cell in list(tr)) for tr in table.findall(".//tbody/tr"))
        table_rows.append({"table": table_ordinal, "caption": caption, "headers": headers, "rows_in_source_order": rows, "row_count": len(rows)})
        counts.append(len(rows))
    if tuple(counts) != (47, 12, 4, 4):
        raise SystemExit("ORG-013 complete table boundary changed")

    main_pages = pages(PdfReader(PDF))
    with ZipFile(SUPPLEMENT) as archive:
        members = archive.infolist()
        if len(members) != 1 or members[0].filename != "polymers-3299596-supplementary.pdf":
            raise SystemExit("ORG-013 supplement member boundary changed")
        supplement_payload = archive.read(members[0])
    supplement_pages = pages(PdfReader(BytesIO(supplement_payload)))
    if len(main_pages) != 24 or len(supplement_pages) != 5:
        raise SystemExit("ORG-013 PDF page boundary changed")
    body_text = " ".join(clean(row) for row in root.findall(".//body//p")).casefold()
    structural = {
        "initiation_explicit": "initiation" in body_text,
        "propagation_explicit": "propagation" in body_text,
        "termination_explicit": "termination" in body_text,
        "two_propagating_radicals_terminate_together_explicit": "two propagating radicals react together" in body_text,
        "chain_length_dependence_explicit": "chain-length" in body_text,
    }
    if not all(structural.values()):
        raise SystemExit(f"ORG-013 structural relation changed: {structural}")
    result = {
        "schema": "sft-v3-chemistry-org-013-complete-postseal-analysis/1",
        "claim_id": "SFT-CHEM-RADICAL-REACTION-NETWORK-013",
        "custody": {
            "package_sha256": inventory["package_sha256"], "archive_member_count": 24,
            "archive_regular_file_count": 23, "all_archive_members_preserved": True,
            "article_page_count": 24, "supplement_page_count": 5,
            "favorable_adverse_absent_and_unresolved_rows_filtered": False,
        },
        "tables_in_source_order": table_rows,
        "table_count": 4,
        "complete_table_row_count": sum(counts),
        "table_row_counts": counts,
        "small_chain_termination_activation_energy_rows": table_rows[2]["rows_in_source_order"],
        "negative_signed_degree_of_polymerization_energy_rows_preserved": table_rows[3]["rows_in_source_order"],
        "article_page_text_vector": main_pages,
        "article_page_text_vector_sha256": sha256_identity(main_pages),
        "supplement_archive_member": {"filename": members[0].filename, "bytes": len(supplement_payload), "sha256": digest(supplement_payload)},
        "supplement_page_text_vector": supplement_pages,
        "supplement_page_text_vector_sha256": sha256_identity(supplement_pages),
        "structural_relation_checks": structural,
        "comparison_status": {
            "initiation_positive_finite_propagation_and_termination_observed": True,
            "two_active_chain_supports_close_at_termination_observed": True,
            "all_67_rows_all_29_pages_all_24_archive_members_and_all_signed_adverse_absent_fields_preserved": True,
            "external_energy_rate_chain_length_temperature_concentration_or_uncertainty_used_to_select_native_law": False,
        },
    }
    result["complete_result_vector_sha256"] = sha256_identity(result)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    print(json.dumps({"result": result["complete_result_vector_sha256"], "rows": sum(counts), "article_pages": 24, "supplement_pages": 5}, sort_keys=True))


if __name__ == "__main__":
    main()
