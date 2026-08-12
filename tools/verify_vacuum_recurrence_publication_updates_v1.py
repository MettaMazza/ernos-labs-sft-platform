#!/usr/bin/env python3
"""Verify the 2026-08-12 recurrence-work successor publications.

This is a versioned, read-only gate.  It does not alter the frozen shared
verification authority and performs no network or publication action.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "publication/vacuum_recurrence_publication_manifest_v1.json"
STATE = ROOT / "publication/vacuum_recurrence_zenodo_state_v1.json"
RENDER_MANIFEST = ROOT / "output/pdf/vacuum-recurrence-update-2026-08-12/PDF_RENDER_MANIFEST.json"
VISUAL_QA = ROOT / "audits/VACUUM_RECURRENCE_PUBLICATION_PDF_VISUAL_QA_2026-08-12.json"
RELEASE_ROOT = ROOT / "output/release/vacuum-recurrence-update-2026-08-12"

EXPECTED = {
    "physics": {
        "version": "1.5.0",
        "parent_record_id": 21761655,
        "parent_doi": "10.5281/zenodo.21761655",
        "concept_doi": "10.5281/zenodo.21520880",
        "doi": "10.5281/zenodo.21900787",
        "draft_id": 21900787,
        "package": "physics-v1.5.0",
    },
    "engineering_translation": {
        "version": "1.2.0",
        "parent_record_id": 21761664,
        "parent_doi": "10.5281/zenodo.21761664",
        "concept_doi": "10.5281/zenodo.21640815",
        "doi": "10.5281/zenodo.21900789",
        "draft_id": 21900789,
        "package": "engineering-translation-v1.2.0",
    },
    "theory_of_everything": {
        "version": "0.4.0",
        "parent_record_id": 21891879,
        "parent_doi": "10.5281/zenodo.21891879",
        "concept_doi": "10.5281/zenodo.21717583",
        "doi": "10.5281/zenodo.21900790",
        "draft_id": 21900790,
        "package": "theory-of-everything-v0.4.0",
    },
}

CLAIMS = {
    "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096":
        "sha256:b20905e98a76c7cfdf74fbb45265e7800328fe5c4cadbd0f7ac3571565f03b6f",
    "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097":
        "sha256:0e904250bbf4a3a67513237641a6a7014affade133bcbdfcad478d84f8025165",
    "SFT-ENG-VACUUM-RECURRENCE-CYCLE-PROTOCOL-003":
        "sha256:d0cc880185372d6d7b5ac953b756d7475277f03eee3b816591570ea1c71f3372",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return "sha256:" + sha256(path.read_bytes()).hexdigest()


def verify_claims() -> dict[str, object]:
    census = {row["claim_id"]: row for row in read_json(ROOT / "census/claims.json")["claims"]}
    result = {}
    for claim_id, expected_receipt in CLAIMS.items():
        package = ROOT / "claims" / claim_id
        row = census.get(claim_id)
        require(row is not None and row.get("model_admitted") is True, f"claim not admitted: {claim_id}")
        require(row["receipt_hash"] == expected_receipt, f"census receipt differs: {claim_id}")
        receipt = read_json(ROOT / row["receipt_path"])
        certificate = read_json(package / "certificate.json")
        candidates = read_json(package / "candidate_census.json")
        decisions = read_json(package / "elimination_receipt.json")["decisions"]
        controls = read_json(package / "controls.json")["controls"]
        require(receipt["receipt_hash"] == expected_receipt, f"receipt identity differs: {claim_id}")
        require(certificate["engine_receipt_hash"] == expected_receipt, f"certificate differs: {claim_id}")
        require(candidates["expected_cardinality"] == 256 and len(candidates["candidates"]) == 256,
                f"candidate census differs: {claim_id}")
        require(len(decisions) == 256 and sum(bool(row["survives"]) for row in decisions) == 1,
                f"unique-survivor decision differs: {claim_id}")
        require(len(controls) == 4 and all(row["passed"] for row in controls),
                f"adverse controls differ: {claim_id}")
        result[claim_id] = {
            "receipt_hash": expected_receipt,
            "candidate_count": 256,
            "survivor_count": 1,
            "control_count": 4,
        }
    return result


def verify_packages() -> list[dict[str, object]]:
    result = []
    for paper_id, expected in EXPECTED.items():
        package = RELEASE_ROOT / expected["package"]
        manifest = read_json(package / "98_PACKAGE_MANIFEST.json")
        require(manifest["publication_mode"] == "zenodo_newversion", f"wrong route: {paper_id}")
        require(manifest["new_record_created"] is False, f"new record asserted: {paper_id}")
        for key in ("version", "parent_doi", "concept_doi", "doi"):
            require(manifest[key] == expected[key], f"package {key} differs: {paper_id}")
        listed = {row["filename"]: row for row in manifest["files"]}
        disk = {path.name for path in package.iterdir() if path.is_file()}
        require(disk == set(listed) | {"98_PACKAGE_MANIFEST.json", "99_SHA256SUMS.txt"},
                f"unlisted or missing package file: {paper_id}")
        for filename, row in listed.items():
            path = package / filename
            require(path.stat().st_size == row["bytes"] and digest(path) == row["sha256"],
                    f"package checksum differs: {paper_id}/{filename}")
        sums = (package / "99_SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        require(len(sums) == len(listed) + 1, f"checksum ledger length differs: {paper_id}")
        for line in sums:
            hexdigest, filename = line.split("  ", 1)
            require(digest(package / filename) == "sha256:" + hexdigest,
                    f"checksum ledger differs: {paper_id}/{filename}")
        result.append({"paper_id": paper_id, "files": len(disk), "status": "PASS"})
    return result


def main() -> None:
    manifest = read_json(MANIFEST)
    state = read_json(STATE)
    render = read_json(RENDER_MANIFEST)
    visual = read_json(VISUAL_QA)
    require(manifest["schema"] == "sft-v3-vacuum-recurrence-publication-manifest/1", "wrong manifest schema")
    require(state["new_concept_created"] is False and state["new_record_endpoint_used"] is False,
            "Zenodo state permits a new post or concept")
    require(set(state["papers"]) == set(EXPECTED), "Zenodo state paper set differs")
    claims = verify_claims()
    paper_results = []
    render_rows = {row["paper_id"]: row for row in render["papers"]}
    visual_rows = {row["paper_id"]: row for row in visual["papers"]}
    for paper in manifest["papers"]:
        paper_id = paper["paper_id"]
        expected = EXPECTED[paper_id]
        for key in ("version", "parent_record_id", "parent_doi", "concept_doi", "doi", "draft_id"):
            require(paper[key] == expected[key], f"publication {key} differs: {paper_id}")
            require(state["papers"][paper_id][key] == expected[key], f"state {key} differs: {paper_id}")
        source = ROOT / paper["output"]
        source_text = source.read_text(encoding="utf-8")
        require(digest(source) == paper["output_sha256"], f"source hash differs: {paper_id}")
        require("PUBLISHED OPEN-ACCESS BRANCH PAPER" in source_text, f"publication boundary absent: {paper_id}")
        require("no new concept and no standalone post" in source_text, f"version boundary absent: {paper_id}")
        require(expected["doi"] in source_text and expected["concept_doi"] in source_text,
                f"DOI boundary absent: {paper_id}")
        for claim_id in paper["claims"]:
            require(claim_id in source_text and CLAIMS[claim_id] in source_text,
                    f"claim evidence absent from paper: {paper_id}/{claim_id}")
        if "current" in paper:
            require((ROOT / paper["current"]).read_bytes() == source.read_bytes(),
                    f"current paper differs from successor: {paper_id}")
        evidence = read_json(ROOT / paper["evidence_map"])
        require(digest(ROOT / paper["evidence_map"]) == paper["evidence_sha256"],
                f"evidence hash differs: {paper_id}")
        require([row["claim_id"] for row in evidence["new_claims"]] == paper["claims"],
                f"evidence claim order differs: {paper_id}")
        metadata = read_json(ROOT / paper["metadata"])
        require(digest(ROOT / paper["metadata"]) == paper["metadata_sha256"],
                f"metadata hash differs: {paper_id}")
        require(metadata["publication_mode"] == "newversion" and metadata["publication_authorized"] is True,
                f"metadata publication route differs: {paper_id}")
        require(metadata["parent_record_id"] == expected["parent_record_id"] and
                metadata["reserved_doi"] == expected["doi"], f"metadata lineage differs: {paper_id}")
        relations = metadata["metadata"]["related_identifiers"]
        require(any(row == {"identifier": expected["parent_doi"], "relation": "isNewVersionOf", "scheme": "doi"}
                    for row in relations), f"isNewVersionOf relation absent: {paper_id}")
        pdf_row = render_rows[paper_id]
        pdf_path = ROOT / pdf_row["pdf"]
        require(digest(pdf_path) == pdf_row["pdf_sha256"], f"PDF hash differs: {paper_id}")
        require(pdf_row["source_sha256"] == digest(source), f"render source differs: {paper_id}")
        document = fitz.open(pdf_path)
        require(len(document) == pdf_row["page_count"], f"PDF page count differs: {paper_id}")
        require(all(page.get_text("text").strip() for page in document), f"blank PDF page: {paper_id}")
        require(all(abs(page.rect.width - 595.276) < 0.1 and abs(page.rect.height - 841.89) < 0.1
                    for page in document), f"non-A4 PDF page: {paper_id}")
        qa = visual_rows[paper_id]
        require(qa["pdf_sha256"] == digest(pdf_path) and qa["raster_review"]["status"] == "PASS",
                f"visual QA differs: {paper_id}")
        paper_results.append({"paper_id": paper_id, "version": expected["version"],
                              "pdf_pages": len(document), "status": "PASS"})
    packages = verify_packages()
    result = {
        "schema": "sft-v3-vacuum-recurrence-publication-gate/1",
        "date": "2026-08-12",
        "status": "PASS",
        "engine_authority": "verified separately before this read-only gate",
        "new_concept_created": False,
        "new_record_endpoint_used": False,
        "claims": claims,
        "papers": paper_results,
        "packages": packages,
    }
    output = ROOT / "audits/VACUUM_RECURRENCE_PUBLICATION_GATE_2026-08-12.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: {len(claims)} claims, {len(paper_results)} successor papers, {len(packages)} packages")
    print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()
