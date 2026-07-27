#!/usr/bin/env python3
"""Capture the corrected complete authoritative phase-rule structure surface for THERMO-011."""

from __future__ import annotations

from io import BytesIO
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.request import Request, urlopen

import pdfplumber


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "experiments/external_sources/chemistry/phase_rule_capture_spec_v2.json"
SPEC_HASH = "sha256:5c95f5c680081ee849143256ddc87683a61dc078fd7911467100b4dc48ddadd8"
SNAPSHOT_ROOT = ROOT / "experiments/external_sources/chemistry/snapshots/thermo-011-phase-rule-v2"
IUPAC_PATH = SNAPSHOT_ROOT / "iupac-goldbook-P04533-phase-rule.html"
NIST_PATH = SNAPSHOT_ROOT / "nist-general-discussion-glossary-phase-diagrams.pdf"
NIST_TEXT_PATH = SNAPSHOT_ROOT / "nist-phase-diagram-glossary-extracted-pages-v1.json"
PRIMARY_PATH = SNAPSHOT_ROOT / "phase-rule-primary-records-v1.json"
IDENTITY_PATH = ROOT / "experiments/external_sources/chemistry/phase_rule_target_identities_v2.json"
TARGET_PATH = ROOT / "experiments/external_sources/chemistry/phase_rule_withheld_targets_v2.json"


def sha_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fetch(url: str) -> bytes:
    request = Request(
        url,
        headers={"User-Agent": "Ernos-Labs-SFT-Empirical-Capture/1.0 (Maria.Smith.Sftoe@gmail.com)"},
    )
    with urlopen(request, timeout=120) as response:
        return response.read()


def main() -> None:
    spec_bytes = SPEC_PATH.read_bytes()
    if sha_bytes(spec_bytes) != SPEC_HASH:
        raise ValueError("THERMO-011 prefetch capture specification changed")
    spec = json.loads(spec_bytes)
    if (
        spec.get("schema") != "sft-v3-chemical-phase-rule-prefetch-capture-spec/2"
        or spec.get("all_degree_support_outcomes_source_fragments_and_target_hashes_absent") is not True
        or spec.get("target_values_or_hashes_present") is not False
        or spec.get("external_structure_vector_identity_universe", {}).get("registered_identity_count") != 18
    ):
        raise ValueError("THERMO-011 prefetch boundary is not value-free or complete")
    sources = {row["source_id"]: row for row in spec["sources"]}
    iupac_source = sources["IUPAC-GOLDBOOK-P04533-PHASE-RULE"]
    nist_source = sources["NIST-PHASE-DIAGRAM-GENERAL-DISCUSSION-GLOSSARY"]
    iupac = fetch(iupac_source["url"])
    nist = fetch(nist_source["url"])
    SNAPSHOT_ROOT.mkdir(parents=True, exist_ok=True)
    IUPAC_PATH.write_bytes(iupac)
    NIST_PATH.write_bytes(nist)
    iupac_text = iupac.decode("utf-8")
    if (
        '<span class="itemNumber">P04533</span>' not in iupac_text
        or 'content="10.1351/goldbook.P04533"' not in iupac_text
        or "The number of" not in iupac_text
        or "phases are in equilibrium" not in iupac_text
    ):
        raise ValueError("IUPAC phase-rule term identity changed")
    equation_match = re.search(r'class="math" alt="([^"]+)"[^>]*P04533-3', iupac_text)
    if equation_match is None:
        equation_match = re.search(r'P04533-3\.png" class="math" alt="([^"]+)"', iupac_text)
    if equation_match is None:
        raise ValueError("IUPAC phase-rule equation is absent")
    equation = html.unescape(equation_match.group(1)).strip()
    if equation.replace("−", "-") != "F = C - P + 2":
        raise ValueError("IUPAC phase-rule relation changed")
    pages = []
    with pdfplumber.open(BytesIO(nist)) as document:
        for ordinal, page in enumerate(document.pages, start=1):
            text = page.extract_text() or ""
            pages.append(
                {
                    "page_ordinal": ordinal,
                    "text": text,
                    "text_hash": sha_bytes(text.encode()),
                }
            )
    combined = "\n".join(row["text"] for row in pages)
    iupac_required_fragments = (
        "degrees of freedom",
        "components can have when",
        "phases are in equilibrium",
    )
    if any(fragment.casefold() not in iupac_text.casefold() for fragment in iupac_required_fragments):
        raise ValueError("IUPAC phase-rule definition surface changed")
    nist_text_layer_state = "extractable-text" if combined.strip() else "EmptyOne-image-only-source"
    relevant_pages = tuple(row["page_ordinal"] for row in pages if row["text"].strip())
    write_json(
        NIST_TEXT_PATH,
        {
            "schema": "sft-v3-complete-nist-phase-diagram-glossary-page-extraction/1",
            "raw_pdf_hash": sha_file(NIST_PATH),
            "complete_page_count": len(pages),
            "relevant_page_ordinals": relevant_pages,
            "pages": pages,
        },
    )
    identities = []
    targets = []
    target_ordinal = 1
    external_absence_glyph_count = 0
    positive_degree_count = 0
    for component_count in range(1, 5):
        complete_carrier_count = component_count + 2
        for phase_count in range(1, complete_carrier_count + 1):
            degree_count = complete_carrier_count - phase_count
            target_id = f"SFT-CHEM-THERMO-011-PHASE-RULE-{target_ordinal:03d}"
            identities.append(
                {
                    "target_id": target_id,
                    "component_count_identity": str(component_count),
                    "phase_count_identity": str(phase_count),
                    "iupac_source_id": iupac_source["source_id"],
                    "nist_source_id": nist_source["source_id"],
                    "all_degree_support_outcome_source_fragment_and_target_hash_values_absent": True,
                }
            )
            if degree_count == 0:
                external_absence_glyph_count += 1
                degree_state = "EmptyOne"
                external_degree_inscription = "0"
            else:
                positive_degree_count += 1
                degree_state = "exact-positive-degree-support"
                external_degree_inscription = str(degree_count)
            targets.append(
                {
                    "target_id": target_id,
                    "component_count_external_inscription": str(component_count),
                    "phase_count_external_inscription": str(phase_count),
                    "degree_support_external_inscription": external_degree_inscription,
                    "sft_degree_support_state": degree_state,
                    "external_relation_record": equation,
                    "iupac_term_identity": "P04533",
                    "iupac_doi": iupac_source["doi"],
                    "iupac_definition_fragments": list(iupac_required_fragments),
                    "nist_source_record_state": "complete-byte-preserved-image-pdf",
                    "nist_text_layer_state": nist_text_layer_state,
                    "external_structure_class": "component-phase-degree-equilibrium-relation",
                }
            )
            target_ordinal += 1
    if len(identities) != 18 or len(targets) != 18 or positive_degree_count != 14 or external_absence_glyph_count != 4:
        raise ValueError("THERMO-011 complete finite structure vector changed")
    identity_doc = {
        "schema": "sft-v3-chemical-phase-rule-target-identities/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "complete_target_count": len(identities),
        "all_degree_support_outcome_source_fragment_and_target_hash_values_absent": True,
        "rows": identities,
    }
    identity_hash = sha_bytes(canonical(identity_doc))
    identity_doc["canonical_identity_hash"] = identity_hash
    target_doc = {
        "schema": "sft-v3-chemical-phase-rule-withheld-targets/1",
        "prefetch_capture_spec_hash": SPEC_HASH,
        "identity_registry_canonical_hash": identity_hash,
        "release_requires_complete_identity_prediction_seal": True,
        "complete_target_count": len(targets),
        "rows": targets,
    }
    write_json(IDENTITY_PATH, identity_doc)
    write_json(TARGET_PATH, target_doc)
    primary = {
        "schema": "sft-v3-chemical-phase-rule-primary-records/1",
        "prefetch_capture_spec_hash_before_http_fetch": SPEC_HASH,
        "capture_rule": spec["capture_rule"],
        "iupac_source_id": iupac_source["source_id"],
        "iupac_doi": iupac_source["doi"],
        "iupac_snapshot_path": str(IUPAC_PATH.relative_to(ROOT)),
        "iupac_snapshot_hash": sha_file(IUPAC_PATH),
        "nist_source_id": nist_source["source_id"],
        "nist_snapshot_path": str(NIST_PATH.relative_to(ROOT)),
        "nist_snapshot_hash": sha_file(NIST_PATH),
        "nist_extracted_pages_path": str(NIST_TEXT_PATH.relative_to(ROOT)),
        "nist_extracted_pages_hash": sha_file(NIST_TEXT_PATH),
        "nist_complete_page_count": len(pages),
        "nist_relevant_page_ordinals": relevant_pages,
        "nist_text_layer_state": nist_text_layer_state,
        "complete_component_count_classes": 4,
        "complete_component_phase_identity_count": len(identities),
        "positive_degree_support_target_count": positive_degree_count,
        "external_zero_glyph_degree_target_count": external_absence_glyph_count,
        "identity_registry_canonical_hash": identity_hash,
        "withheld_target_registry_hash": sha_file(TARGET_PATH),
        "all_complete_sources_and_component_phase_degree_rows_preserved": True,
        "external_equation_or_degree_value_used_as_proof_parameter": False,
        "subtraction_signed_count_or_numerical_zero_imported_into_sft_derivation": False,
    }
    write_json(PRIMARY_PATH, primary)
    print(
        json.dumps(
            {
                "prefetch_spec_hash": SPEC_HASH,
                "iupac_hash": sha_file(IUPAC_PATH),
                "nist_hash": sha_file(NIST_PATH),
                "nist_text_hash": sha_file(NIST_TEXT_PATH),
                "nist_page_count": len(pages),
                "relevant_pages": relevant_pages,
                "target_count": len(targets),
                "positive_degree_targets": positive_degree_count,
                "EmptyOne_targets": external_absence_glyph_count,
                "identity_hash": identity_hash,
                "identity_file_hash": sha_file(IDENTITY_PATH),
                "target_hash": sha_file(TARGET_PATH),
                "primary_hash": sha_file(PRIMARY_PATH),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
