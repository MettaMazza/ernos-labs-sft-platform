#!/usr/bin/env python3
"""Open the complete KIN-012 target surface after identity registration."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "experiments/external_sources/chemistry/snapshots/kin-012-kinetic-isotope-effect-v1"
IDENTITIES = ROOT / "experiments/external_sources/chemistry/kinetic_isotope_effect_target_identities_v1.json"
OUTPUT = ROOT / "experiments/external_sources/chemistry/kinetic_isotope_effect_withheld_targets_v1.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.source import hash_file  # noqa: E402


def sha256_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    identity_document = json.loads(IDENTITIES.read_text())
    if identity_document.get("target_values_or_hashes_present") is not False:
        raise SystemExit("KIN-012 identity seal is not value-free")
    pdf_text = {
        name: tuple(page.extract_text() or "" for page in PdfReader(SNAPSHOT / name).pages)
        for name in ("article.pdf", "supplementary-information.pdf", "reporting-summary.pdf")
    }
    with ZipFile(SNAPSHOT / "source-data.xlsx") as archive:
        workbook_parts = {name: archive.read(name) for name in archive.namelist()}
    rows = []
    for identity in identity_document["rows"]:
        record_class = identity["source_record_class"]
        if record_class == "complete-article-landing-record":
            raw = (SNAPSHOT / "article.html").read_bytes()
            target = {
                "source_content_class": "complete-article-landing-html",
                "complete_document_byte_count": len(raw),
                "complete_document_hash": sha256_bytes(raw),
            }
        elif record_class.endswith("-page"):
            text = pdf_text[identity["source_document_identity"]][identity["source_page_ordinal"] - 1]
            target = {
                "complete_extracted_page_text": text,
                "complete_extracted_page_text_hash": sha256_bytes(text.encode("utf-8")),
            }
        elif record_class == "complete-source-data-worksheet":
            raw = workbook_parts[identity["source_workbook_member_identity"]]
            target = {
                "complete_worksheet_xml_byte_count": len(raw),
                "complete_worksheet_xml_hash": sha256_bytes(raw),
                "declared_maximum_row_ordinal": identity["declared_maximum_row_ordinal"],
                "declared_maximum_column_ordinal": identity["declared_maximum_column_ordinal"],
            }
        else:
            raise ValueError(f"unknown KIN-012 source record class: {record_class}")
        rows.append(identity | {"target_payload": target})
    payload = {
        "schema": "sft-v3-kinetic-isotope-effect-withheld-targets/1",
        "chemistry_obligation": "SFT-CHEM-OBL-KIN-012",
        "claim_id": "SFT-CHEM-KINETIC-ISOTOPE-EFFECT-RELATION-012",
        "identity_registry_hash": hash_file(IDENTITIES),
        "complete_registered_target_count": len(rows),
        "complete_pdf_page_target_count": identity_document["complete_pdf_page_count"],
        "complete_source_data_worksheet_target_count": identity_document["complete_source_data_worksheet_count"],
        "release_requires_complete_identity_and_prediction_seal": True,
        "all_complete_source_records_preserved": True,
        "rows": rows,
    }
    write_json(OUTPUT, payload)
    print(json.dumps({"targets": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
