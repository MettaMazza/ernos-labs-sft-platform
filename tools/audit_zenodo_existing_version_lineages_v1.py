#!/usr/bin/env python3
"""Read-only preflight for the seven existing Zenodo version lineages.

The audit never authenticates, creates a draft, requests a new version, uploads
files or changes a remote record.  It fails closed unless every candidate is
still based on the latest expected record in its existing concept DOI lineage.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.request


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Lineage:
    branch: str
    record_id: int
    record_doi: str
    concept_doi: str
    current_version: str
    candidate_version: str
    metadata_path: str


LINEAGES = (
    Lineage("mathematics", 21627708, "10.5281/zenodo.21627708", "10.5281/zenodo.21516145", "1.4.0", "1.5.0", "publications/successors/mathematics/zenodo_metadata_v1_5.json"),
    Lineage("information_science", 21627717, "10.5281/zenodo.21627717", "10.5281/zenodo.21516915", "1.3.0", "1.4.0", "publications/successors/information_science/zenodo_metadata_v1_4.json"),
    Lineage("computation", 21627721, "10.5281/zenodo.21627721", "10.5281/zenodo.21518310", "1.3.0", "1.4.0", "publications/successors/computation/zenodo_metadata_v1_4.json"),
    Lineage("quantum_computation", 21627748, "10.5281/zenodo.21627748", "10.5281/zenodo.21518312", "1.3.0", "1.4.0", "publications/successors/quantum_computation/zenodo_metadata_v1_4.json"),
    Lineage("physics", 21627765, "10.5281/zenodo.21627765", "10.5281/zenodo.21520880", "1.2.0", "1.3.0", "publications/successors/physics/zenodo_metadata_v1_3.json"),
    Lineage("chemistry", 21627782, "10.5281/zenodo.21627782", "10.5281/zenodo.21531454", "1.2.0", "1.3.0", "publications/successors/chemistry/zenodo_metadata_v1.3_draft.json"),
    Lineage("materials", 21629306, "10.5281/zenodo.21629306", "10.5281/zenodo.21532481", "1.2.0", "1.3.0", "publications/successors/materials/zenodo_metadata_v1_3.json"),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "Ernos-Labs-SFT-Zenodo-Lineage-Audit/1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        require(response.status == 200, f"Zenodo transport status {response.status}: {url}")
        return json.load(response)


def audit(lineage: Lineage) -> dict:
    record_url = f"https://zenodo.org/api/records/{lineage.record_id}"
    remote = fetch_json(record_url)
    latest_url = remote.get("links", {}).get("latest")
    require(isinstance(latest_url, str) and latest_url.startswith("https://zenodo.org/api/records/"), f"latest-version link missing: {lineage.branch}")
    latest = fetch_json(latest_url)
    local = read_json(ROOT / lineage.metadata_path)
    metadata = local.get("metadata", {})
    relations = metadata.get("related_identifiers", [])

    checks = {
        "record_id_matches": remote.get("id") == lineage.record_id,
        "record_doi_matches": remote.get("doi") == lineage.record_doi,
        "concept_doi_matches": remote.get("conceptdoi") == lineage.concept_doi,
        "current_version_matches": remote.get("metadata", {}).get("version") == lineage.current_version,
        "record_is_still_latest": latest.get("id") == lineage.record_id,
        "latest_concept_doi_matches": latest.get("conceptdoi") == lineage.concept_doi,
        "candidate_version_matches": metadata.get("version") == lineage.candidate_version,
        "candidate_versions_expected_record": any(
            item.get("identifier") == lineage.record_doi
            and item.get("relation") == "isNewVersionOf"
            and item.get("scheme") == "doi"
            for item in relations
        ),
        "publication_authorized_false": local.get("publication_authorized") is False,
        "ready_to_publish_false": local.get("ready_to_publish") is False,
        "maria_smith_is_remote_creator": any(
            creator.get("name") in {"Smith, Maria", "Maria Smith"}
            for creator in remote.get("metadata", {}).get("creators", [])
        ),
        "maria_smith_is_candidate_creator": any(
            creator.get("name") in {"Smith, Maria", "Maria Smith"}
            for creator in metadata.get("creators", [])
        ),
    }
    failures = [name for name, passed in checks.items() if not passed]
    require(not failures, f"Zenodo lineage preflight halted for {lineage.branch}: {', '.join(failures)}")
    return {
        "branch": lineage.branch,
        "status": "PASS",
        "record_id": lineage.record_id,
        "record_doi": lineage.record_doi,
        "concept_doi": lineage.concept_doi,
        "current_version": lineage.current_version,
        "candidate_version": lineage.candidate_version,
        "remote_title": remote.get("metadata", {}).get("title"),
        "remote_updated": remote.get("updated"),
        "remote_file_count": len(remote.get("files", [])),
        "metadata_path": lineage.metadata_path,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()
    rows = [audit(lineage) for lineage in LINEAGES]
    result = {
        "schema": "sft-v3-zenodo-existing-version-lineage-preflight/1",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "mode": "read-only-unauthenticated",
        "remote_action_performed": False,
        "publication_authorized": False,
        "papers": rows,
        "summary": {
            "papers": len(rows),
            "passes": len(rows),
            "halts": 0,
            "existing_records_only": True,
            "new_records_created": 0,
            "new_versions_created": 0,
            "uploads_performed": 0,
        },
    }
    if args.json_out:
        destination = args.json_out if args.json_out.is_absolute() else ROOT / args.json_out
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
