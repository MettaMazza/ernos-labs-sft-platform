#!/usr/bin/env python3
"""Build the complete post-seal ORG-012 primary-observation vector."""

from __future__ import annotations

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402


SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/org-012-diels-alder-blind-v1"
MEMBERS = SNAPSHOT / "members/PMC8162770"
INVENTORY = SNAPSHOT / "source-inventory-v1.json"
INVENTORY_HASH = "sha256:66d0b968d32a47fa48a58e6ce797e1a285b873f4c4011e50db49acf34f9a6f50"
NXML = MEMBERS / "SC-011-D0SC04553E.nxml"
NXML_HASH = "sha256:7bd269a764fdd5ab7b9b83787c70b4c84313289bacb0153e8163d2024cb94312"
ARTICLE_PDF = MEMBERS / "SC-011-D0SC04553E.pdf"
ARTICLE_PDF_HASH = "sha256:4cf2aa95787ab44d9dca1b806e0c7318a13d746d1e5a0da01f39a5f4748b48bf"
SUPPLEMENT_PDF = MEMBERS / "SC-011-D0SC04553E-s001.pdf"
SUPPLEMENT_PDF_HASH = "sha256:26c5c09b6920c437538d0473b0acdd93da4050edf5e4becb1f8175cd87124fe6"
CIF = MEMBERS / "SC-011-D0SC04553E-s002.cif"
CIF_HASH = "sha256:cd2a848715bd1d513de5d93de0d313c457a940028d1fc3b88cb78094b286abb2"
OUTPUT = SNAPSHOT / "complete-postseal-analysis-v1.json"
XLINK = "{http://www.w3.org/1999/xlink}href"


def digest_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def clean_text(node: ET.Element) -> str:
    return " ".join("".join(node.itertext()).split())


def page_vector(path: Path) -> tuple[dict[str, object], ...]:
    rows = []
    for ordinal, page in enumerate(PdfReader(path).pages, 1):
        text = " ".join((page.extract_text() or "").replace("\u00ad", "").split())
        rows.append({
            "page": ordinal,
            "text_character_count": len(text),
            "text_sha256": digest_bytes(text.encode("utf-8")),
            "has_extracted_text": bool(text),
        })
    return tuple(rows)


def ratio_status(value: str) -> dict[str, object]:
    if value == "—":
        return {
            "experimental_ratio_status": "unresolved_absent_in_primary_table",
            "both_relative_classes_reported": False,
            "preference_class": "unresolved",
        }
    values = tuple(Decimal(row) for row in re.findall(r"\d+(?:\.\d+)?", value))
    if len(values) != 2:
        raise ValueError(f"ORG-012 unparseable experimental ratio: {value}")
    first, second = values
    if first.is_zero() or second.is_zero():
        preference = "one_reported_class_at_conventional_zero"
    elif first > second:
        preference = "first_reported_class_preferred"
    elif first < second:
        preference = "second_reported_class_preferred"
    else:
        preference = "equal_reported_classes"
    return {
        "experimental_ratio_status": "reported",
        "both_relative_classes_reported": not first.is_zero() and not second.is_zero(),
        "preference_class": preference,
    }


def primary_table(root: ET.Element) -> tuple[dict[str, object], ...]:
    table = root.find(".//table-wrap")
    if table is None:
        raise ValueError("ORG-012 primary table missing")
    body = table.find(".//tbody")
    if body is None:
        raise ValueError("ORG-012 primary table body missing")
    rows = []
    current_dienophile_image = None
    for ordinal, tr in enumerate(body.findall("./tr"), 1):
        cells = list(tr)
        if len(cells) == 10:
            image = cells[0].find(".//inline-graphic")
            if image is None or not image.get(XLINK):
                raise ValueError(f"ORG-012 row {ordinal} dienophile identity missing")
            current_dienophile_image = image.get(XLINK)
            cells = cells[1:]
        if len(cells) != 9 or current_dienophile_image is None:
            raise ValueError(f"ORG-012 row {ordinal} table shape changed")
        values = tuple(clean_text(cell) for cell in cells)
        row = {
            "ordinal": ordinal,
            "dienophile_image": current_dienophile_image,
            "diene": values[0],
            "adducts": values[1],
            "temperature_conventional": values[2],
            "time_conventional": values[3],
            "isolated_yield_conventional": values[4],
            "endo_exo_experimental_conventional": values[5],
            "endo_exo_calculated_conventional": values[6],
            "calculated_conformer_distribution_conventional": values[7],
            "homo_lumo_gap_conventional": values[8],
            **ratio_status(values[5]),
        }
        image_path = MEMBERS / current_dienophile_image
        if not image_path.is_file():
            raise ValueError(f"ORG-012 row {ordinal} image missing")
        row["dienophile_image_sha256"] = digest_file(image_path)
        rows.append(row)
    return tuple(rows)


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit("ORG-012 complete post-seal analysis already exists")
    authorities = (
        (INVENTORY, INVENTORY_HASH),
        (NXML, NXML_HASH),
        (ARTICLE_PDF, ARTICLE_PDF_HASH),
        (SUPPLEMENT_PDF, SUPPLEMENT_PDF_HASH),
        (CIF, CIF_HASH),
    )
    for path, expected in authorities:
        if digest_file(path) != expected:
            raise SystemExit(f"ORG-012 source changed: {path}")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    member_rows = tuple(inventory["archive_members_in_source_order"])
    for row in member_rows:
        if row["member_type"] != "file":
            continue
        source = SNAPSHOT / "members" / row["name"]
        if not source.is_file() or digest_file(source) != row["content_sha256"]:
            raise SystemExit(f"ORG-012 archive member changed: {row['name']}")

    xml_root = ET.parse(NXML).getroot()
    table_rows = primary_table(xml_root)
    if len(table_rows) != 32 or tuple(row["ordinal"] for row in table_rows) != tuple(range(1, 33)):
        raise SystemExit("ORG-012 complete primary-table boundary changed")
    measured = tuple(row for row in table_rows if row["experimental_ratio_status"] == "reported")
    unresolved = tuple(row for row in table_rows if row["experimental_ratio_status"] != "reported")
    first = tuple(row for row in measured if row["preference_class"] == "first_reported_class_preferred")
    second = tuple(row for row in measured if row["preference_class"] == "second_reported_class_preferred")
    equal = tuple(row for row in measured if row["preference_class"] == "equal_reported_classes")
    both = tuple(row for row in measured if row["both_relative_classes_reported"])
    if (len(measured), len(unresolved), len(first), len(second), len(equal), len(both)) != (28, 4, 22, 5, 1, 28):
        raise SystemExit("ORG-012 complete primary measured-value vector changed")

    article_pages = page_vector(ARTICLE_PDF)
    supplement_pages = page_vector(SUPPLEMENT_PDF)
    if len(article_pages) != 12 or len(supplement_pages) != 203:
        raise SystemExit("ORG-012 complete PDF page boundary changed")
    table = xml_root.find(".//table-wrap")
    footnotes = tuple(clean_text(row) for row in table.findall(".//table-wrap-foot//fn")) if table is not None else ()
    paragraphs = tuple(clean_text(row) for row in xml_root.findall(".//body//p"))
    paragraph_vector = tuple({
        "ordinal": ordinal,
        "text_character_count": len(text),
        "text_sha256": digest_bytes(text.encode("utf-8")),
    } for ordinal, text in enumerate(paragraphs, 1))

    result = {
        "schema": "sft-v3-chemistry-org-012-complete-postseal-analysis/1",
        "claim_id": "SFT-CHEM-PERICYCLIC-REACTION-FAMILY-012",
        "custody": {
            "package_sha256": inventory["package_sha256"],
            "archive_member_count": inventory["archive_member_count"],
            "archive_regular_file_count": inventory["archive_regular_file_count"],
            "all_archive_members_preserved": inventory["all_archive_members_preserved"],
            "article_pdf_page_count": len(article_pages),
            "supplement_pdf_page_count": len(supplement_pages),
            "crystallographic_information_file_preserved": True,
            "favorable_adverse_absent_and_unresolved_rows_filtered": False,
        },
        "primary_table_caption": clean_text(xml_root.find(".//table-wrap/caption")),
        "primary_table_headers": tuple(
            clean_text(row) for row in xml_root.findall(".//table-wrap//thead/tr[2]/*")
        ),
        "primary_table_rows_in_source_order": table_rows,
        "primary_table_footnotes_in_source_order": footnotes,
        "primary_table_row_count": len(table_rows),
        "experimental_ratio_reported_count": len(measured),
        "experimental_ratio_unresolved_count": len(unresolved),
        "first_reported_class_preferred_count": len(first),
        "second_reported_class_preferred_count": len(second),
        "equal_reported_classes_count": len(equal),
        "both_relative_classes_reported_count": len(both),
        "all_reported_experimental_rows_preserve_both_relative_classes": len(both) == len(measured),
        "one_target_independent_universal_preference_observed": False,
        "article_page_text_vector": article_pages,
        "article_page_text_vector_sha256": sha256_identity(article_pages),
        "supplement_page_text_vector": supplement_pages,
        "supplement_page_text_vector_sha256": sha256_identity(supplement_pages),
        "article_body_paragraph_vector": paragraph_vector,
        "article_body_paragraph_vector_sha256": sha256_identity(paragraph_vector),
        "comparison_status": {
            "native_two_relative_orientation_classes_have_reported_primary_representatives": True,
            "native_nonselection_of_one_universal_preference_matches_complete_primary_vector": True,
            "conventional_ratios_conditions_yields_energies_and_labels_used_to_select_native_law": False,
            "all_archive_members_all_32_primary_rows_all_203_supplement_pages_and_all_absences_preserved": True,
        },
    }
    result["complete_result_vector_sha256"] = sha256_identity(result)
    OUTPUT.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "complete_result_vector_sha256": result["complete_result_vector_sha256"],
        "primary_table_rows": len(table_rows),
        "reported_experimental_ratios": len(measured),
        "second_class_preferences": len(second),
        "equal_class_rows": len(equal),
        "supplement_pages": len(supplement_pages),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
