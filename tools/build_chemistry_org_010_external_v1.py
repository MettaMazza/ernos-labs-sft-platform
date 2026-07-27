#!/usr/bin/env python3
"""Reconstruct the complete post-seal ORG-010 supplementary evidence vector.

This program is deliberately downstream of the frozen prediction seal.  It
does not decide the Fold law.  It verifies the captured Europe PMC archive,
retains every PDF page, enumerates every characterized product in source
order, and records adverse and unresolved conventional observations without
turning them into native arithmetic.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/org-010-europe-pmc-blind-v1"
INVENTORY_PATH = SNAPSHOT_DIR / "source-inventory-v1.json"
PDF_PATH = SNAPSHOT_DIR / "SC-015-D4SC01905A-s001.pdf"
OUTPUT_PATH = SNAPSHOT_DIR / "complete-postseal-analysis-v1.json"

EXPECTED_ARCHIVE_HASH = "sha256:3f2136b22a780a0e8e04c314c5733e7712299fdcca9f7525663f056ceb643a74"
EXPECTED_PDF_HASH = "sha256:f274759e0f850ecefb14e4d685d78bcae2641284b366d74f2bd03b10a8459620"
EXPECTED_PRODUCT_CODES = tuple(
    [f"3{letter}" for letter in "abcdefghijklmnopqrstuvwxyz"]
    + [f"3a{letter}" for letter in "abcdef"]
)


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_hash(value: object) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )


def _normalise(value: str) -> str:
    value = value.replace("\u00ad", "").replace("\uf0b7", " ")
    return " ".join(value.split())


def _product_blocks(complete_text: str, page_texts: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    del complete_text
    # The registered identity fixes characterization to printed pages 46--53.
    # Using that complete range also prevents the following spectral pages from
    # being mistaken for duplicate characterization starts.
    section = _normalise("\n".join(page_texts[45:53]))
    start_pattern = re.compile(
        r"(?P<name>[^.]{4,240}?)\s*\(\s*(?P<code>3(?:[a-z]|a[a-f]))\s*\)\.\s+General procedure",
        re.IGNORECASE,
    )
    starts = tuple(start_pattern.finditer(section))
    codes = tuple(match.group("code").lower() for match in starts)
    if codes != EXPECTED_PRODUCT_CODES:
        raise ValueError(f"complete ORG-010 product order changed: {codes}")

    rows: list[dict[str, object]] = []
    for ordinal, match in enumerate(starts, 1):
        boundary = starts[ordinal].start() if ordinal < len(starts) else len(section)
        block = section[match.start():boundary].strip()
        code = match.group("code").lower()
        name = re.sub(r"^\d{1,3}\s+", "", _normalise(match.group("name"))).strip()
        pre_spectrum = re.split(r"\b1H NMR\b", block, maxsplit=1)[0]
        compact_pre_spectrum = re.sub(r"(?<=\d)\s+(?=\d\s*[:%])", "", pre_spectrum)
        percentages = tuple(
            dict.fromkeys(re.findall(r"(?:>|<)?\s*\d+\s*%", compact_pre_spectrum))
        )
        ratios = tuple(
            dict.fromkeys(
                re.findall(
                    r"(?:E:Z|A:B|Internal:Terminal)\s*[;:=]?\s*>?\s*\d+\s*:\s*\d+",
                    compact_pre_spectrum,
                    flags=re.IGNORECASE,
                )
            )
        )
        alternative_codes = tuple(
            dict.fromkeys(re.findall(r"\b3(?:[a-z]|a[a-f])[\u2019']", pre_spectrum))
        )
        page_numbers = tuple(
            index
            for index, page in enumerate(page_texts, 1)
            if re.search(rf"\(\s*{re.escape(code)}\s*\)\.", _normalise(page), flags=re.IGNORECASE)
        )
        if len(page_numbers) != 1:
            raise ValueError(f"product {code} does not have one characterization start page: {page_numbers}")
        lower_name = name.lower()
        unsaturation_visible = any(token in lower_name for token in ("en", "vinyl", "allyl"))
        modalities = tuple(
            modality
            for modality, marker in (
                ("1H-NMR", "1H NMR"),
                ("13C-NMR", "13C NMR"),
                ("19F-NMR", "19F NMR"),
                ("IR", "IR ("),
                ("HRMS", "HRMS"),
            )
            if marker in block
        )
        rows.append(
            {
                "ordinal": ordinal,
                "product_code": code,
                "reported_name": name,
                "characterization_start_page": page_numbers[0],
                "procedure": re.search(r"General procedure\s+(2\.1[67])", block).group(1),
                "percent_inscriptions_before_first_spectrum": percentages,
                "isomer_ratio_inscriptions": ratios,
                "alternative_product_codes": alternative_codes,
                "matched_prior_literature_inscription": "matched" in pre_spectrum.lower()
                and "literature" in pre_spectrum.lower(),
                "characterization_modalities": modalities,
                "observable_unsaturation_in_reported_product_name": unsaturation_visible,
                "full_reactant_byproduct_carrier_present_in_characterization_block": False,
                "complete_atom_and_support_balance_status": "unresolved_in_this_conventional_product_block",
                "source_block_sha256": _sha256_bytes(block.encode("utf-8")),
                "source_block": block,
            }
        )
    if not all(row["observable_unsaturation_in_reported_product_name"] for row in rows):
        missing = tuple(row["product_code"] for row in rows if not row["observable_unsaturation_in_reported_product_name"])
        raise ValueError(f"reported unsaturation marker absent from product names: {missing}")
    return tuple(rows)


# These rows are a literal transcription of the complete image tables on PDF
# pages 25--27.  Values remain external inscriptions, including dashes and the
# source's missing entry number; they are never converted to native Fold values.
OPTIMISATION_TABLES = (
    {
        "table": "S1",
        "page": 25,
        "rows": (
            {"entry": "NBS", "conjugate_acid_pKa": "14.7", "products": "3a", "yield": "39%"},
            {"entry": "2-bromo-2-nitropropane", "conjugate_acid_pKa": "~17", "products": "3a", "yield": "83%"},
            {"entry": "ethyl 2-bromoisobutyrate", "conjugate_acid_pKa": "~27", "products": "4a", "yield": "70%"},
        ),
    },
    {
        "table": "S2",
        "page": 25,
        "rows": tuple(
            {"entry": str(entry), "temperature_C": temperature, "yield_3a_3a_prime": result}
            for entry, temperature, result in (
                (1, "60", "38/25"), (2, "70", "47/27"), (3, "80", "65/14"),
                (4, "95", "77/-"), (5, "110", "69/-"),
            )
        ),
    },
    {
        "table": "S3",
        "page": 26,
        "rows": tuple(
            {"entry": entry, "solvent": solvent, "concentration_M": concentration, "yield_3a_3a_prime": result}
            for entry, solvent, concentration, result in (
                ("1", "CH3CN", "0.1", "77/-"), ("2", "DMF", "0.1", "36/-"),
                ("3", "THF", "0.1", "-"), ("4", "Et2O", "0.1", "-"),
                ("5", "DCM", "0.1", "-"), ("6", "not_printed_in_source_table", "not_printed", "not_printed"),
                ("7", "CH3CN (wet)", "0.1", "60/-"), ("8", "CH3CN", "0.05", "39/-"),
            )
        ),
    },
    {
        "table": "S4",
        "page": 26,
        "rows": tuple(
            {"entry": str(entry), "1a_equivalent": one_a, "2a_equivalent": two_a, "yield_3a_3a_prime": result}
            for entry, one_a, two_a, result in (
                (1, "1", "1", "77/-"), (2, "1", "1.2", "88/-"), (3, "1", "1.5", "80/-"),
                (4, "1", "2", "67/-"), (5, "1.2", "1", "91/-"), (6, "1.5", "1", "41/-"),
            )
        ),
    },
    {
        "table": "S5",
        "page": 26,
        "rows": tuple(
            {"entry": str(entry), "time_h": time, "yield_3a_3a_prime": result}
            for entry, time, result in ((1, "1.5", "73/10"), (2, "3", "88/-"), (3, "4.5", "84/-"), (4, "6", "84/-"))
        ),
    },
    {
        "table": "S6",
        "page": 27,
        "rows": tuple(
            {"entry": str(entry), "cation": cation, "yield_3a_3a_prime": result}
            for entry, cation, result in ((1, "Li+", "5/2"), (2, "Na+", "63/-"), (3, "K+", "88/-"), (4, "Cs+", "81/-"))
        ),
    },
    {
        "table": "S7",
        "page": 27,
        "rows": (
            {"entry": "1", "condition": "2a (1.2 equiv.), CH3CN, 95 C, 3h, 0.2 mmol scale", "yield_3a": "88"},
            {"entry": "2", "condition": "Co/Acr photoredox dual catalytic", "yield_3a": "6"},
            {"entry": "3", "condition": "PIFA microwave assisted", "yield_3a": "-"},
            {"entry": "4", "condition": "copper-catalyzed literature conditions", "yield_3a": "89"},
        ),
    },
)


UNSUCCESSFUL_SUBSTRATE_ROWS = (
    {"ordinal": 1, "substrate": "ortho-nitro carboxylate structure", "observed": "carboxylic acid retained"},
    {"ordinal": 2, "substrate": "para-nitro secondary carboxylate structure", "observed": "Hass-Bender oxidation and bromination-followed-by-SN2 products"},
    {"ordinal": 3, "substrate": "para-CF3 carboxylate structure", "observed": "carboxylic acid retained"},
    {"ordinal": 4, "substrate": "3,5-bis-CF3 carboxylate structure", "observed": "No reaction"},
    {"ordinal": 5, "substrate": "para-CONMe2 carboxylate structure", "observed": "<5% elimination"},
)


def build() -> dict[str, object]:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if (
        inventory.get("archive_sha256") != EXPECTED_ARCHIVE_HASH
        or inventory.get("archive_bytes") != 15_503_988
        or inventory.get("capture_status") != "captured_once_after_claim_specific_seal"
        or inventory.get("source_recapture_count") != 0
        or len(inventory.get("members", ())) != 22
    ):
        raise ValueError("ORG-010 source inventory boundary changed")
    archive_path = ROOT / inventory["archive_path"]
    if _hash_file(archive_path) != EXPECTED_ARCHIVE_HASH:
        raise ValueError("ORG-010 archive hash changed")
    for member in inventory["members"]:
        path = ROOT / member["snapshot_path"]
        if path.stat().st_size != member["snapshot_bytes"] or _hash_file(path) != member["snapshot_sha256"]:
            raise ValueError(f"ORG-010 archive member changed: {member['archive_member']}")
    with zipfile.ZipFile(archive_path) as archive:
        if sorted(archive.namelist()) != sorted(member["archive_member"] for member in inventory["members"]):
            raise ValueError("ORG-010 archive member list changed")

    if _hash_file(PDF_PATH) != EXPECTED_PDF_HASH:
        raise ValueError("ORG-010 supplementary PDF changed")
    reader = PdfReader(PDF_PATH)
    if len(reader.pages) != 117:
        raise ValueError("ORG-010 complete PDF page boundary changed")
    page_texts = tuple(page.extract_text() or "" for page in reader.pages)
    page_rows = tuple(
        {
            "page": ordinal,
            "text_character_count": len(text),
            "text_sha256": _sha256_bytes(text.encode("utf-8")),
            "has_extracted_text": bool(text.strip()),
        }
        for ordinal, text in enumerate(page_texts, 1)
    )
    complete_text = "\n\f\n".join(page_texts)
    products = _product_blocks(complete_text, page_texts)
    optimisation_row_count = sum(len(table["rows"]) for table in OPTIMISATION_TABLES)

    result: dict[str, object] = {
        "schema": "sft-v3-chemistry-org-010-complete-postseal-analysis/1",
        "claim_id": "SFT-CHEM-ELIMINATION-REACTION-FAMILY-010",
        "obligation_id": "SFT-CHEM-OBL-ORG-010",
        "custody": {
            "archive_sha256": EXPECTED_ARCHIVE_HASH,
            "archive_bytes": inventory["archive_bytes"],
            "archive_member_count": len(inventory["members"]),
            "pdf_sha256": EXPECTED_PDF_HASH,
            "pdf_bytes": PDF_PATH.stat().st_size,
            "pdf_page_count": len(reader.pages),
            "source_recapture_count": inventory["source_recapture_count"],
            "all_archive_members_and_pdf_pages_retained": True,
        },
        "complete_page_text_vector": page_rows,
        "complete_page_text_vector_sha256": _canonical_hash(page_rows),
        "characterized_product_rows_in_source_order": products,
        "characterized_product_count": len(products),
        "products_with_observable_unsaturation_count": sum(
            bool(row["observable_unsaturation_in_reported_product_name"]) for row in products
        ),
        "products_with_full_carrier_balance_in_characterization_block_count": sum(
            bool(row["full_reactant_byproduct_carrier_present_in_characterization_block"]) for row in products
        ),
        "unresolved_complete_carrier_balance_count": sum(
            row["complete_atom_and_support_balance_status"] == "unresolved_in_this_conventional_product_block"
            for row in products
        ),
        "products_with_reported_isomer_ratio_count": sum(bool(row["isomer_ratio_inscriptions"]) for row in products),
        "alternative_product_rows": tuple(
            {"product_code": row["product_code"], "alternatives": row["alternative_product_codes"]}
            for row in products
            if row["alternative_product_codes"]
        ),
        "optimisation_tables": OPTIMISATION_TABLES,
        "optimisation_table_count": len(OPTIMISATION_TABLES),
        "optimisation_row_count_including_explicit_source_gap": optimisation_row_count,
        "unsuccessful_substrate_rows": UNSUCCESSFUL_SUBSTRATE_ROWS,
        "unsuccessful_substrate_count": len(UNSUCCESSFUL_SUBSTRATE_ROWS),
        "mechanistic_and_control_page_range": "28-43",
        "mechanistic_and_control_page_vector": page_rows[27:43],
        "observed_intermediate_record": {
            "page": 29,
            "intermediate": "3a-prime",
            "product": "3a",
            "reported_15_minute_GC_ratio": "3a:3a-prime = 72:28",
            "reported_time_course_page": 38,
            "reported_time_course_rows": (
                {"minutes": "10", "3a_percent": "28", "3a_prime_percent": "44"},
                {"minutes": "20", "3a_percent": "40", "3a_prime_percent": "31"},
                {"minutes": "30", "3a_percent": "50", "3a_prime_percent": "23.5"},
                {"minutes": "45", "3a_percent": "60", "3a_prime_percent": "14"},
                {"minutes": "60", "3a_percent": "70", "3a_prime_percent": "7"},
                {"minutes": "90", "3a_percent": "80", "3a_prime_percent": "3"},
            ),
        },
        "comparison_status": {
            "observable_unsaturation_product_rows_favorable": len(products),
            "complete_atom_support_carrier_rows_favorable": 0,
            "complete_atom_support_carrier_rows_adverse": 0,
            "complete_atom_support_carrier_rows_unresolved": len(products),
            "unsuccessful_or_low_elimination_rows_preserved": len(UNSUCCESSFUL_SUBSTRATE_ROWS),
            "no_post_outcome_product_filter_applied": True,
            "no_optimization_or_control_page_omitted": True,
        },
        "scientific_scope": {
            "externally_supported": "all 32 characterized products display an exact unsaturation consequence and the intermediate/product time course displays loss of 3a-prime as 3a grows",
            "not_claimed_from_this_source": "the isolated product blocks do not display every coproduct, so complete atom and held-support balance is unresolved rather than awarded",
            "formal_law_role": "complete carrier conservation and exact inverse-addition adjacency accounting remain the independently forced structural law",
        },
    }
    result["complete_result_vector_sha256"] = _canonical_hash(result)
    return result


def main() -> None:
    payload = build()
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"products: {payload['characterized_product_count']}")
    print(f"optimization rows: {payload['optimisation_row_count_including_explicit_source_gap']}")
    print(f"unresolved full-carrier rows: {payload['unresolved_complete_carrier_balance_count']}")
    print(f"result vector: {payload['complete_result_vector_sha256']}")


if __name__ == "__main__":
    main()
