#!/usr/bin/env python3
"""Reconstruct the complete first post-seal ORG-011 evidence surface.

The registered supplement is retained even though its displayed reaction
schemes do not expose every reagent-derived and coproduct carrier needed for
an exact whole-reaction atom/support reconstruction.  This builder therefore
records every source, product, mixture, competing branch, value and PDF page,
but awards no complete-carrier comparison that the source does not contain.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = ROOT / "experiments/external_sources/chemistry/snapshots/org-011-europe-pmc-blind-v1"
INVENTORY_PATH = SNAPSHOT_DIR / "source-inventory-v1.json"
PDF_PATH = SNAPSHOT_DIR / "ANIE-60-7360-s001.pdf"
OUTPUT_PATH = SNAPSHOT_DIR / "complete-postseal-analysis-v1.json"

EXPECTED_ARCHIVE_HASH = "sha256:dd756122730f2446435df37d757b083f5b967560f36574ac5b819d354fbc32bb"
EXPECTED_PDF_HASH = "sha256:63eb137b44d7e3772960ee2befc91ee1ee421c21edd95cd7227b4772e07f210c"
EXPECTED_STARTING_CODES = tuple(f"5{letter}" for letter in "abcdefghijklmnopqrst")
EXPECTED_SEMIPINACOL_BLOCK_CODES = (
    ("6a",), ("7a",), ("6b",), ("7b",), ("6c",), ("7c",),
    ("6d",), ("7d",), ("6e",), ("7e",), ("6f",), ("7f",),
    ("7g",), ("6h",), ("7h",), ("6i",), ("7i",), ("6j",),
    ("7j",), ("6k",), ("7k",), ("6l",), ("7l",), ("6m",),
    ("7m",), ("6n",), ("7n",), ("6o",), ("7o",), ("6p",),
    ("7p",), ("6q",), ("6r",), ("7r",), ("6s",), ("7s",),
    ("6t", "6t-prime"), ("7t", "7t-prime"),
)
EXPECTED_EPOXIDE_BLOCK_CODES = (
    ("8a",), ("8d-prime", "8d"), ("8f",), ("8j",), ("8l",),
    ("8n",), ("8p-prime", "8p"), ("8s",), ("14",),
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


def _display_code(value: str) -> str:
    return value.replace("’", "-prime").replace("'", "-prime")


def _codes_near_marker(prefix: str) -> tuple[str, ...]:
    raw = re.findall(r"\b(?:6|7|8)[a-z](?:[’']|\b)|\b(?:13|14)\b", prefix[-420:])
    retained: list[str] = []
    for value in raw:
        code = _display_code(value)
        if code not in retained:
            retained.append(code)
    # Incidental NMR numerals occur earlier in the window.  The product title
    # ends at the procedure marker, so retain the shortest suffix containing
    # the expected product-code family.
    family = tuple(value for value in retained if re.fullmatch(r"[678][a-z](?:-prime)?|1[34]", value))
    return family


def _page_for_offset(page_texts: tuple[str, ...], first_page: int, offset: int) -> int:
    traversed = 0
    for page in range(first_page, len(page_texts) + 1):
        chunk = _normalise(page_texts[page - 1]) + " "
        if traversed + len(chunk) > offset:
            return page
        traversed += len(chunk)
    raise ValueError("offset falls outside declared PDF surface")


def _structured_block(
    *,
    section: str,
    ordinal: int,
    page: int,
    codes: tuple[str, ...],
    source_text: str,
    source_code: str | None,
    procedure: str,
) -> dict[str, object]:
    before_spectra = re.split(r"\b1H NMR\b", source_text, maxsplit=1)[0]
    formulas = tuple(
        dict.fromkeys(_normalise(value) for value in re.findall(r"Calcd\.?\s*for\s+(.{1,120}?)\s+m/z", source_text))
    )
    percent_inscriptions = tuple(dict.fromkeys(re.findall(r"(?:<\s*)?\d+\s*%", before_spectra)))
    ratio_inscriptions = tuple(
        dict.fromkeys(
            re.findall(r"\b\d+\s*:\s*\d+(?:\.\d+)?\b|\b\d+\s*:\s*0\.\d+\b", before_spectra)
        )
    )
    return {
        "section": section,
        "ordinal": ordinal,
        "characterization_start_page": page,
        "product_codes": codes,
        "reported_source_code": source_code,
        "procedure": procedure,
        "percent_inscriptions_before_first_spectrum": percent_inscriptions,
        "ratio_inscriptions_before_first_spectrum": ratio_inscriptions,
        "hrms_formula_inscriptions": formulas,
        "complete_reagent_and_coproduct_carrier_family_exposed": False,
        "exact_whole_reaction_atom_support_reconstruction_status": "unresolved_in_incomplete_displayed_reaction_surface",
        "source_block_sha256": _sha256_bytes(source_text.encode("utf-8")),
        "source_block": source_text,
    }


def _starting_material_rows(page_texts: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    section = _normalise("\n".join(page_texts[4:12]))
    pattern = re.compile(r"(?P<code>5[a-t])\s+Prepared using general procedure\s*1", re.IGNORECASE)
    starts = tuple(pattern.finditer(section))
    codes = tuple(match.group("code").lower() for match in starts)
    if codes != EXPECTED_STARTING_CODES:
        raise ValueError(f"ORG-011 starting-material order changed: {codes}")
    rows: list[dict[str, object]] = []
    for ordinal, match in enumerate(starts, 1):
        boundary = starts[ordinal].start() if ordinal < len(starts) else len(section)
        block_start = max(
            section.rfind("See spectrum", 0, match.start()) + len("See spectrum"),
            section.rfind("See spectra", 0, match.start()) + len("See spectra"),
            section.rfind("carbinols", 0, match.start()) + len("carbinols"),
        )
        block = section[block_start:boundary].strip()
        rows.append(
            {
                "ordinal": ordinal,
                "starting_material_code": match.group("code").lower(),
                "characterization_start_page": _page_for_offset(page_texts, 5, match.start()),
                "percent_inscriptions": tuple(dict.fromkeys(re.findall(r"(?:<\s*)?\d+\s*%", block))),
                "hrms_formula_inscriptions": tuple(
                    dict.fromkeys(_normalise(value) for value in re.findall(r"Calcd\.?\s*for\s+(.{1,120}?)\s+m/z", block))
                ),
                "source_block_sha256": _sha256_bytes(block.encode("utf-8")),
                "source_block": block,
            }
        )
    return tuple(rows)


def _procedure_rows(
    page_texts: tuple[str, ...],
    *,
    first_page: int,
    last_page: int,
    section: str,
    procedure_digit: str,
    expected_codes: tuple[tuple[str, ...], ...],
) -> tuple[dict[str, object], ...]:
    page_chunks = tuple(_normalise(page_texts[page - 1]) + " " for page in range(first_page, last_page + 1))
    joined = "".join(page_chunks)
    pattern = re.compile(
        rf"Prepared following general procedur\s*e?\s*(?P<procedure>{procedure_digit}\s*[ab])",
        re.IGNORECASE,
    )
    matches = tuple(pattern.finditer(joined))
    rows: list[dict[str, object]] = []
    found_codes: list[tuple[str, ...]] = []
    for ordinal, match in enumerate(matches, 1):
        prefix = joined[:match.start()]
        candidates = _codes_near_marker(prefix)
        expected = expected_codes[ordinal - 1]
        # The product title is the final code-bearing phrase before the marker.
        codes = tuple(code for code in candidates if code in expected)
        if codes != expected:
            raise ValueError(f"ORG-011 {section} code boundary changed at {ordinal}: {codes} != {expected}")
        found_codes.append(codes)
        next_start = matches[ordinal].start() if ordinal < len(matches) else len(joined)
        prior_anchor = max(
            joined.rfind("See spectrum", 0, match.start()) + len("See spectrum"),
            joined.rfind("See spectra", 0, match.start()) + len("See spectra"),
            joined.rfind("Scope of the", 0, match.start()),
        )
        block = joined[prior_anchor:next_start].strip()
        source_codes = tuple(dict.fromkeys(re.findall(r"\b5[a-t]\b", block, flags=re.IGNORECASE)))
        rows.append(
            _structured_block(
                section=section,
                ordinal=ordinal,
                page=first_page + next(index for index, total in enumerate(_cumulative(page_chunks)) if match.start() < total),
                codes=codes,
                source_text=block,
                source_code=source_codes[0].lower() if source_codes else None,
                procedure=_normalise(match.group("procedure")).lower(),
            )
        )
    if tuple(found_codes) != expected_codes:
        raise ValueError(f"ORG-011 {section} procedure-block count changed")
    return tuple(rows)


def _cumulative(values: tuple[str, ...]) -> tuple[int, ...]:
    total = 0
    result = []
    for value in values:
        total += len(value)
        result.append(total)
    return tuple(result)


def _special_rows(page_texts: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    complete = _normalise("\n".join(page_texts))
    specifications = (
        ("initial", "10", "Benzyl 3-chloro-3-(1-hydroxy-1-phenylethyl)azetidine-1-carboxylate, 10", "Benzyl 3-(1-hydroxy-1-phenylethyl)-3-iodoazetidine-1-carboxylate, 11"),
        ("initial", "11", "Benzyl 3-(1-hydroxy-1-phenylethyl)-3-iodoazetidine-1-carboxylate, 11", "2,2,2-Trifluoro-1-(3-(1-hydroxy-1-phenylethyl)-3-iodoazetidin-1-yl)ethan-1-one, 12"),
        ("initial", "12", "2,2,2-Trifluoro-1-(3-(1-hydroxy-1-phenylethyl)-3-iodoazetidin-1-yl)ethan-1-one, 12", "1.5. Optimisation of the semipinacol rearrangement reaction"),
        ("semipinacol", "13+7q+7q-prime", "Semipinacol rearrangement of 5q with Tf2O", "1,1'-(3-Phenylazetidine-1,3-diyl)bis(2,2,2-trifluoroethan-1-one), 6r"),
        ("epoxide", "15", "2-Methyl-2-phenyl-5-tosyl-1-oxa-5-azaspiro[2.3]hexane, 15", "2. NMR Spectra"),
    )
    rows = []
    for ordinal, (section, code_label, start_marker, end_marker) in enumerate(specifications, 1):
        start = complete.find(start_marker)
        end = complete.find(end_marker, start + len(start_marker))
        if start < 0 or end < 0:
            raise ValueError(f"ORG-011 special block changed: {code_label}")
        block = complete[start:end].strip()
        codes = tuple(code_label.split("+"))
        source_codes = tuple(dict.fromkeys(re.findall(r"\b5[a-t]\b", block, flags=re.IGNORECASE)))
        rows.append(
            _structured_block(
                section=section,
                ordinal=ordinal,
                page=next(index for index, page in enumerate(page_texts, 1) if start_marker in _normalise(page)),
                codes=codes,
                source_text=block,
                source_code=source_codes[0].lower() if source_codes else None,
                procedure="explicit-source-procedure",
            )
        )
    return tuple(rows)


OPTIMISATION_ROWS = (
    {"entry": "1", "R2O": "(CF3CO)2O", "additive": "EmptyOne external blank", "solvent": "MeCN", "temperature": "0 C", "time": "15 mins", "yield_6a_or_7a": "71%"},
    {"entry": "2", "R2O": "(CF3CO)2O", "additive": "EmptyOne external blank", "solvent": "DCM", "temperature": "-78 C", "time": "1 h", "yield_6a_or_7a": "93% isolated"},
    {"entry": "3", "R2O": "(CF3CO)2O", "additive": "2,6-lutidene", "solvent": "DCM", "temperature": "-78 C", "time": "1 h", "yield_6a_or_7a": "61%"},
    {"entry": "4", "R2O": "Tf2O", "additive": "EmptyOne external blank", "solvent": "MeCN", "temperature": "0 C", "time": "15 mins", "yield_6a_or_7a": "40%"},
    {"entry": "5", "R2O": "Tf2O", "additive": "EmptyOne external blank", "solvent": "DCM", "temperature": "-78 C", "time": "1 h", "yield_6a_or_7a": "67%"},
    {"entry": "6", "R2O": "Tf2O", "additive": "2,6-lutidene", "solvent": "DCM", "temperature": "-78 C", "time": "1 h", "yield_6a_or_7a": "79% isolated"},
)


def build() -> dict[str, object]:
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    if (
        inventory.get("archive_sha256") != EXPECTED_ARCHIVE_HASH
        or inventory.get("archive_bytes") != 11_608_470
        or inventory.get("capture_status") != "captured_once_after_claim_specific_seal"
        or inventory.get("source_recapture_count") != 0
        or len(inventory.get("members", ())) != 12
    ):
        raise ValueError("ORG-011 V1 source inventory boundary changed")
    archive_path = ROOT / inventory["archive_path"]
    if _hash_file(archive_path) != EXPECTED_ARCHIVE_HASH:
        raise ValueError("ORG-011 V1 archive hash changed")
    for member in inventory["members"]:
        path = ROOT / member["snapshot_path"]
        if path.stat().st_size != member["snapshot_bytes"] or _hash_file(path) != member["snapshot_sha256"]:
            raise ValueError(f"ORG-011 V1 member changed: {member['archive_member']}")
    with zipfile.ZipFile(archive_path) as archive:
        if sorted(archive.namelist()) != sorted(member["archive_member"] for member in inventory["members"]):
            raise ValueError("ORG-011 V1 archive member list changed")
    if _hash_file(PDF_PATH) != EXPECTED_PDF_HASH:
        raise ValueError("ORG-011 V1 PDF hash changed")

    reader = PdfReader(PDF_PATH)
    if len(reader.pages) != 114:
        raise ValueError("ORG-011 V1 PDF page boundary changed")
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
    starting = _starting_material_rows(page_texts)
    semipinacol = _procedure_rows(
        page_texts,
        first_page=16,
        last_page=39,
        section="semipinacol",
        procedure_digit="2",
        expected_codes=EXPECTED_SEMIPINACOL_BLOCK_CODES,
    )
    epoxide = _procedure_rows(
        page_texts,
        first_page=39,
        last_page=45,
        section="epoxide",
        procedure_digit="3",
        expected_codes=EXPECTED_EPOXIDE_BLOCK_CODES,
    )
    special = _special_rows(page_texts)
    all_product_rows = tuple(sorted((*semipinacol, *epoxide, *special), key=lambda row: (row["characterization_start_page"], row["section"], row["ordinal"])))
    if len(starting) != 20 or len(semipinacol) != 38 or len(epoxide) != 9 or len(special) != 5:
        raise ValueError("ORG-011 V1 complete row census changed")

    result: dict[str, object] = {
        "schema": "sft-v3-chemistry-org-011-complete-postseal-analysis/1",
        "claim_id": "SFT-CHEM-REARRANGEMENT-REACTION-FAMILY-011",
        "obligation_id": "SFT-CHEM-OBL-ORG-011",
        "source_identity": {
            "pmcid": "PMC8247891",
            "doi": "10.1002/anie.202100583",
            "title": "Divergent, Strain-Release Reactions of Azabicyclo[1.1.0]butyl Carbinols: Semipinacol or Spiroepoxy Azetidine Formation",
        },
        "custody": {
            "archive_sha256": EXPECTED_ARCHIVE_HASH,
            "archive_member_count": 12,
            "pdf_sha256": EXPECTED_PDF_HASH,
            "pdf_page_count": 114,
            "source_recapture_count": 0,
            "complete_page_text_vector_sha256": _canonical_hash(page_rows),
        },
        "complete_page_text_vector": page_rows,
        "starting_material_rows_in_source_order": starting,
        "product_characterization_rows_in_source_order": all_product_rows,
        "semipinacol_procedure_block_count": len(semipinacol),
        "semipinacol_reported_product_species_count": sum(len(row["product_codes"]) for row in semipinacol) + 3,
        "epoxide_procedure_block_count": len(epoxide),
        "epoxide_reported_product_species_count": sum(len(row["product_codes"]) for row in epoxide) + 1,
        "initial_investigation_product_count": 3,
        "optimization_rows": OPTIMISATION_ROWS,
        "comparison_status": {
            "complete_whole_reaction_source_product_pairs_exposed": 0,
            "complete_atom_support_pairs_favorable": 0,
            "complete_atom_support_pairs_adverse": 0,
            "complete_atom_support_pairs_unresolved": len(all_product_rows),
            "reason": "The displayed schemes and characterization blocks omit at least one complete reagent-derived or coproduct carrier; exact whole-reaction atom/support identity cannot be inferred from a partial carrier surface.",
            "semipinacol_and_spiroepoxy_branches_preserved_separately": True,
            "mixed_products_and_alternatives_preserved": True,
            "optimization_and_initial_investigation_rows_preserved": True,
            "no_success_yield_or_branch_filter_applied": True,
            "blind_supplement_does_not_by_itself_close_the_registered_exact_structure_vector": True,
        },
    }
    result["complete_result_vector_sha256"] = _canonical_hash(result)
    return result


def main() -> int:
    result = build()
    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "output_sha256": _hash_file(OUTPUT_PATH),
        "complete_result_vector_sha256": result["complete_result_vector_sha256"],
        "starting_material_rows": len(result["starting_material_rows_in_source_order"]),
        "product_rows": len(result["product_characterization_rows_in_source_order"]),
        "complete_pairs_favorable": result["comparison_status"]["complete_atom_support_pairs_favorable"],
        "complete_pairs_unresolved": result["comparison_status"]["complete_atom_support_pairs_unresolved"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
