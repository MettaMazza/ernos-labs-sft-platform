#!/usr/bin/env python3
"""Verify the seven published final-publication Zenodo versions and lineages."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from publish_final_publication_versions_v1 import (  # noqa: E402
    API,
    PUBLICATIONS,
    expected_file_map,
    public_request,
)


RECEIPTS = {
    "mathematics": "audits/FINAL_PUBLICATION_ZENODO_MATHEMATICS_PUBLISHED_2026-07-29.json",
    "information_science": "audits/FINAL_PUBLICATION_ZENODO_INFORMATION_SCIENCE_PUBLISHED_2026-07-29.json",
    "computation": "audits/FINAL_PUBLICATION_ZENODO_CLASSICAL_COMPUTATION_PUBLISHED_2026-07-29.json",
    "quantum_computation": "audits/FINAL_PUBLICATION_ZENODO_QUANTUM_COMPUTATION_PUBLISHED_2026-07-29.json",
    "physics": "audits/FINAL_PUBLICATION_ZENODO_PHYSICS_PUBLISHED_2026-07-29.json",
    "chemistry": "audits/FINAL_PUBLICATION_ZENODO_CHEMISTRY_PUBLISHED_2026-07-29.json",
    "materials": "audits/FINAL_PUBLICATION_ZENODO_MATERIALS_PUBLISHED_2026-07-29.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def public_files(record: dict) -> dict[str, tuple[int, str]]:
    return {
        item["key"]: (int(item["size"]), item["checksum"].removeprefix("md5:"))
        for item in record.get("files", [])
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    rows = []
    for branch, publication in PUBLICATIONS.items():
        receipt_path = ROOT / RECEIPTS[branch]
        receipt = read(receipt_path)
        require(receipt.get("status") == "PUBLISHED_VERIFIED" and receipt.get("published") is True, f"published receipt missing: {branch}")
        require(receipt.get("source_record") == publication.source_record, f"source record mismatch: {branch}")
        require(receipt.get("source_doi") == publication.source_doi, f"source DOI mismatch: {branch}")
        require(receipt.get("concept_doi") == publication.concept_doi, f"receipt concept DOI mismatch: {branch}")
        require(receipt.get("version") == publication.candidate_version, f"receipt version mismatch: {branch}")
        record_id = int(receipt["record_id"])
        record = public_request(f"{API}/records/{record_id}")
        source = public_request(f"{API}/records/{publication.source_record}")
        source_latest = public_request(source["links"]["latest"])
        record_latest = public_request(record["links"]["latest"])
        expected = expected_file_map(publication)
        receipt_files = {
            item["filename"]: (int(item["bytes"]), item["checksum"].removeprefix("md5:"))
            for item in receipt["files"]
        }
        checks = {
            "record_id_matches": record.get("id") == record_id,
            "doi_matches": record.get("doi") == receipt.get("doi"),
            "concept_doi_retained": record.get("conceptdoi") == publication.concept_doi,
            "version_matches": record.get("metadata", {}).get("version") == publication.candidate_version,
            "publication_date_matches": record.get("metadata", {}).get("publication_date") == "2026-07-29",
            "maria_smith_is_creator": any(
                creator.get("name") in {"Smith, Maria", "Maria Smith"}
                for creator in record.get("metadata", {}).get("creators", [])
            ),
            "parent_relation_preserved": any(
                item.get("identifier") == publication.source_doi
                and item.get("relation") == "isNewVersionOf"
                for item in record.get("metadata", {}).get("related_identifiers", [])
            ),
            "source_latest_is_published_version": source_latest.get("id") == record_id,
            "record_is_latest": record_latest.get("id") == record_id,
            "public_files_match_release": public_files(record) == expected,
            "receipt_files_match_release": receipt_files == expected,
        }
        failures = [name for name, passed in checks.items() if not passed]
        require(not failures, f"published Zenodo verification halted for {branch}: {', '.join(failures)}")
        rows.append(
            {
                "branch": branch,
                "status": "PASS",
                "version": publication.candidate_version,
                "record_id": record_id,
                "doi": record.get("doi"),
                "concept_doi": record.get("conceptdoi"),
                "source_record_id": publication.source_record,
                "source_doi": publication.source_doi,
                "title": record.get("metadata", {}).get("title"),
                "file_count": len(expected),
                "files": [
                    {"filename": name, "bytes": size, "md5": checksum}
                    for name, (size, checksum) in sorted(expected.items())
                ],
                "receipt_path": RECEIPTS[branch],
                "checks": checks,
            }
        )
    result = {
        "schema": "sft-v3-final-publication-zenodo-verification/1",
        "date": "2026-07-29",
        "papers": rows,
        "summary": {
            "papers": len(rows),
            "passes": len(rows),
            "halts": 0,
            "published_versions": len(rows),
            "existing_concept_dois_retained": len(rows),
            "independent_concept_records_created": 0,
            "all_public_files_checksum_verified": True,
        },
    }
    if args.json_out:
        destination = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
