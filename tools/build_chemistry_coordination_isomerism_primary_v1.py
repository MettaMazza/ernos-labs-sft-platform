#!/usr/bin/env python3
"""Open and preserve the complete INORG-005 vector after identity sealing."""

from __future__ import annotations

from html import unescape
import json
from pathlib import Path
import re
import sys

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.source import hash_file  # noqa: E402


IDENTITIES = ROOT / "experiments/external_sources/chemistry/coordination_isomerism_target_identities_v2.json"
IDENTITIES_HASH = "sha256:7264542ef42da0fab309f6fd94cc1d7560202767417784bd8b92a1744957bd95"
TARGETS = ROOT / "experiments/external_sources/chemistry/coordination_isomerism_withheld_targets_v1.json"
PRIMARY = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/coordination-isomerism-primary-records-v1.json"


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def plain(fragment: str) -> str:
    value = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.I | re.S)
    value = re.sub(r"<style\b.*?</style>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(unescape(value).split())


def html_between(text: str, start: str, end: str) -> str:
    match = re.search(start + r"(.*?)" + end, text, flags=re.I | re.S)
    return match.group(1) if match else ""


def html_surface(text: str, role: str, path: Path) -> object:
    if role == "complete-source-file":
        return hash_file(path)
    title = plain(html_between(text, r"<title>", r"</title>"))
    heading_matches = re.findall(r"<h2[^>]*class=\"panel-title[^\"]*\"[^>]*>(.*?)</h2>", text, flags=re.I | re.S)
    heading = plain(heading_matches[-1]) if heading_matches else ""
    doi_match = re.search(r"<div id=\"doi\"[^>]*>(.*?)</div>", text, flags=re.I | re.S)
    doi = plain(doi_match.group(1)) if doi_match else ""
    definitions = html_between(text, r"<div id=\"definitions\">", r"</div>\s*</div>\s*</div>")
    citation_match = re.search(r"<b>Citation:</b>(.*?)</div>", text, flags=re.I | re.S)
    citation = plain(citation_match.group(1)) if citation_match else ""
    version_match = re.search(r"<h5>(Version .*?)</h5>", text, flags=re.I | re.S)
    version = plain(version_match.group(1)) if version_match else "not-reported"
    if role == "presented-term-identity":
        return {"page_title": title, "presented_term": heading, "presented_doi": doi}
    if role == "complete-definition-surface":
        return plain(definitions)
    if role == "source-citation-status-license-disclaimer-surface":
        return {
            "citation": citation,
            "collection_version": version,
            "term_status": "not-reported-in-captured-html-response",
            "license": "not-reported-in-captured-html-response",
            "disclaimer": "not-reported-in-captured-html-response",
        }
    raise ValueError(f"unrecognized Gold Book surface: {role}")


def json_surface(text: str, role: str, path: Path) -> object:
    term = json.loads(text)["term"]
    if role == "complete-source-file":
        return hash_file(path)
    if role == "presented-term-identity":
        return {key: term.get(key) for key in ("id", "title", "code", "doi", "status")}
    if role == "complete-definition-surface":
        return term.get("definitions", [])
    if role == "source-citation-status-license-disclaimer-surface":
        return {key: term.get(key) for key in ("citation", "status", "license", "collection", "disclaimer", "accessed")}
    raise ValueError(f"unrecognized Gold Book surface: {role}")


def normalized_page(reader: PdfReader, page_number: int) -> str:
    return " ".join((reader.pages[page_number - 1].extract_text() or "").split())


def red_book_surfaces(path: Path) -> dict[str, object]:
    reader = PdfReader(path)
    pages = tuple(" ".join((page.extract_text() or "").split()) for page in reader.pages)
    attachment_page = pages[170]
    if "two isomeric bidentate modes of binding" not in attachment_page:
        raise ValueError("IUPAC Red Book attachment-mode surface changed")
    if "point of ligation" not in attachment_page.replace("p oint", "point"):
        raise ValueError("IUPAC Red Book point-of-ligation surface changed")
    literal_matches = tuple(index for index, page in enumerate(pages, start=1) if "linkage isomer" in page.lower())
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    return {
        "complete-source-file": hash_file(path),
        "official-publication-identity-and-citation-surface": {
            "document_title_surface": pages[2],
            "publication_surface": pages[3],
            "pdf_metadata": metadata,
            "extracted_page_count": len(pages),
        },
        "coordination-compound-point-of-ligation-surface": {
            "pdf_page_ordinal": 171,
            "complete_extracted_page_surface": attachment_page,
        },
        "isomeric-donor-attachment-mode-surface": {
            "pdf_page_ordinal": 171,
            "complete_extracted_page_surface": attachment_page,
        },
        "explicit-linkage-term-presence-or-absence-status": {
            "normalized_literal": "linkage isomer",
            "matching_pdf_page_ordinals": literal_matches,
            "status": "explicit-literal-absent-from-complete-extracted-document" if not literal_matches else "explicit-literal-present",
        },
    }


def main() -> None:
    if hash_file(IDENTITIES) != IDENTITIES_HASH:
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 target identities changed")
    identities = json.loads(IDENTITIES.read_text(encoding="utf-8"))
    if identities.get("target_values_or_payload_hashes_present") is not False:
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 identity document contains target outcomes")

    pdf_path = ROOT / "experiments/external_sources/chemistry/snapshots/inorg-005-linkage-addendum-v1/iupac-red-book-2005-complete.pdf"
    red_book = red_book_surfaces(pdf_path)
    rows = []
    for identity in identities["rows"]:
        path = ROOT / identity["snapshot_path"]
        role = identity["source_record_role"]
        if identity["source_id"] == "IUPAC-RED-BOOK-2005-COMPLETE":
            inscription = red_book[role]
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            inscription = json_surface(text, role, path) if text.lstrip().startswith("{") else html_surface(text, role, path)
        rows.append(
            identity
            | {
                "source_inscription": inscription,
                "target_payload_hash": sha256_identity((identity["target_id"], role, inscription)),
                "status": "reported-authoritative-record",
            }
        )

    if len(rows) != 17:
        raise SystemExit("VOID_INVALID_HALTED: INORG-005 complete target census changed")
    targets = {
        "schema": "sft-v3-coordination-isomerism-withheld-targets/1",
        "identity_document_sha256": IDENTITIES_HASH,
        "release_requires_prediction_seal": True,
        "complete_registered_target_count": len(rows),
        "rows": rows,
    }
    TARGETS.write_text(json.dumps(targets, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")

    by_source = {}
    for row in rows:
        by_source.setdefault(row["source_id"], {})[row["source_record_role"]] = row["source_inscription"]
    general_definition = canonical(by_source["IUPAC-I03294"]["complete-definition-surface"])
    geometric_definition = by_source["IUPAC-G02620"]["complete-definition-surface"]
    optical_definition = by_source["IUPAC-O04308"]["complete-definition-surface"]
    attachment_surface = canonical(by_source["IUPAC-RED-BOOK-2005-COMPLETE"]["isomeric-donor-attachment-mode-surface"])
    explicit_status = by_source["IUPAC-RED-BOOK-2005-COMPLETE"]["explicit-linkage-term-presence-or-absence-status"]
    analysis = {
        "general_isomer_relation_retained": "relationship between isomers" in general_definition.lower(),
        "geometric_relative_position_distinction_retained": all(fragment in geometric_definition.lower() for fragment in ("differ in the positions", "same side", "opposite sides")),
        "mirror_non_superposable_distinction_retained": (
            "mirror images" in optical_definition.lower()
            and "non-" in optical_definition.lower()
            and "superposable" in optical_definition.lower()
        ),
        "point_of_ligation_distinction_retained": "point of ligation" in attachment_surface.replace("p oint", "point"),
        "two_isomeric_attachment_modes_retained": "two isomeric bidentate modes of binding" in attachment_surface,
        "distinct_attachment_indices_retained": all(fragment in attachment_surface for fragment in ("k2N1,N4", "k2N1,N7")),
        "literal_linkage_term_absence_retained": explicit_status["status"] == "explicit-literal-absent-from-complete-extracted-document",
        "all_seventeen_target_surfaces_retained": len(rows) == 17,
    }
    if not all(analysis.values()):
        raise SystemExit(f"INORG-005 complete authority surface changed: {analysis}")
    identities_observed = {
        source_id: surfaces["presented-term-identity"]
        for source_id, surfaces in by_source.items()
        if "presented-term-identity" in surfaces
    }
    primary = {
        "schema": "sft-v3-coordination-isomerism-primary-records/1",
        "chemistry_obligation": "SFT-CHEM-OBL-INORG-005",
        "claim_id": "SFT-CHEM-COORDINATION-ISOMERISM-EQUIVALENCE-005",
        "identity_document_sha256": IDENTITIES_HASH,
        "target_document_sha256": hash_file(TARGETS),
        "complete_registered_target_count": len(rows),
        "complete_source_class_census": {"IUPAC-Gold-Book": 12, "IUPAC-Red-Book": 5},
        "exact_postseal_analysis": analysis,
        "presented_identity_vector": identities_observed,
        "registered_to_presented_identity_redirect_count": 2,
        "registered_to_presented_identity_redirects_preserved": True,
        "explicit_linkage_literal_absence_preserved": True,
        "isomer_catalogue_name_point_group_plane_mirror_or_observed_class_used_as_fold_proof_parameter": False,
        "rows": rows,
    }
    PRIMARY.write_text(json.dumps(primary, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"targets": len(rows), "targets_sha256": hash_file(TARGETS), "primary_sha256": hash_file(PRIMARY)}, sort_keys=True))


if __name__ == "__main__":
    main()
