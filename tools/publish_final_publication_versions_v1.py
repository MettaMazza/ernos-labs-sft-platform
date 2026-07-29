#!/usr/bin/env python3
"""Fail-closed controller for the seven approved Zenodo new-version releases.

This controller is bound to Maria Smith's approval receipt and the already
passed final-publication release gate.  It can operate on only one named branch
per invocation.  It never creates a new concept record: `create-draft` calls
Zenodo's `newversion` action on the exact published parent record.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from publish_zenodo_deposit import API, request  # noqa: E402


APPROVAL = ROOT / "audits/FINAL_PUBLICATION_MARIA_APPROVAL_RECEIPT_2026-07-29.json"
RELEASE_GATE = ROOT / "audits/FINAL_PUBLICATION_RELEASE_GATE_V1_2026-07-29.json"


@dataclass(frozen=True)
class Publication:
    branch: str
    source_record: int
    source_doi: str
    concept_doi: str
    current_version: str
    candidate_version: str
    release_dir: str
    metadata_path: str
    preserve_inherited: tuple[str, ...] = ()


PUBLICATIONS = {
    item.branch: item
    for item in (
        Publication("mathematics", 21627708, "10.5281/zenodo.21627708", "10.5281/zenodo.21516145", "1.4.0", "1.5.0", "output/release/mathematics-1.5.0", "publications/successors/mathematics/zenodo_metadata_v1_5.json"),
        Publication("information_science", 21627717, "10.5281/zenodo.21627717", "10.5281/zenodo.21516915", "1.3.0", "1.4.0", "output/release/information-science-1.4.0", "publications/successors/information_science/zenodo_metadata_v1_4.json"),
        Publication("computation", 21627721, "10.5281/zenodo.21627721", "10.5281/zenodo.21518310", "1.3.0", "1.4.0", "output/release/classical-computation-1.4.0", "publications/successors/computation/zenodo_metadata_v1_4.json"),
        Publication("quantum_computation", 21627748, "10.5281/zenodo.21627748", "10.5281/zenodo.21518312", "1.3.0", "1.4.0", "output/release/quantum-computation-1.4.0", "publications/successors/quantum_computation/zenodo_metadata_v1_4.json"),
        Publication("physics", 21627765, "10.5281/zenodo.21627765", "10.5281/zenodo.21520880", "1.2.0", "1.3.0", "output/release/physics-1.3.0", "publications/successors/physics/zenodo_metadata_v1_3.json"),
        Publication(
            "chemistry",
            21627782,
            "10.5281/zenodo.21627782",
            "10.5281/zenodo.21531454",
            "1.2.0",
            "1.3.0",
            "output/release/chemistry-1.3.0",
            "publications/successors/chemistry/zenodo_metadata_v1.3_draft.json",
            (
                "04_Catalytic-Turnover-Complete-Supplementary-Data.zip",
                "05_USPTO-Full-Remapped-Reaction-Source.csv",
            ),
        ),
        Publication("materials", 21629306, "10.5281/zenodo.21629306", "10.5281/zenodo.21532481", "1.2.0", "1.3.0", "output/release/materials-1.3.0", "publications/successors/materials/zenodo_metadata_v1_3.json"),
    )
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def token() -> str:
    token_file = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    value = token_file.read_text(encoding="utf-8").strip()
    require(bool(value), "Zenodo token file is empty")
    return value


def public_request(url: str) -> dict:
    call = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Ernos-Labs-SFT-Final-Publication/1"})
    with urllib.request.urlopen(call, timeout=180) as response:
        return json.load(response)


def approval_and_gate(publication: Publication) -> tuple[dict, dict]:
    approval = read(APPROVAL)
    gate = read(RELEASE_GATE)
    require(approval.get("approved") is True and approval.get("approver") == "Maria Smith", "Maria Smith approval receipt is absent")
    for key in ("approval_dossier", "release_gate", "zenodo_lineage_preflight"):
        reference = approval[key]
        require(sha256(ROOT / reference["path"]) == reference["sha256"], f"approval-bound authority changed: {key}")
    approved = next((row for row in approval["candidates"] if row["branch"] == publication.branch), None)
    gated = next((row for row in gate["papers"] if row["branch"] == publication.branch), None)
    require(approved is not None and gated is not None and gated.get("status") == "PASS", f"approved release gate row missing: {publication.branch}")
    require(approved["version"] == publication.candidate_version == gated["version"], f"approved version mismatch: {publication.branch}")
    require(approved["existing_record_doi"] == publication.source_doi == gated["previous_version_doi"], f"approved parent DOI mismatch: {publication.branch}")
    require(approved["concept_doi"] == publication.concept_doi, f"approved concept DOI mismatch: {publication.branch}")
    require(approved["manuscript_sha256"] == gated["manuscript_sha256"], f"approved manuscript mismatch: {publication.branch}")
    require(approved["pdf_sha256"] == gated["pdf_sha256"], f"approved PDF mismatch: {publication.branch}")
    return approved, gated


def local_files(publication: Publication) -> dict[str, Path]:
    release = ROOT / publication.release_dir
    files = {path.name: path for path in sorted(release.iterdir()) if path.is_file()}
    require(bool(files), f"release directory is empty: {release}")
    return files


def metadata(publication: Publication) -> dict:
    document = read(ROOT / publication.metadata_path)
    value = dict(document["metadata"])
    require(value.get("version") == publication.candidate_version, f"candidate metadata version mismatch: {publication.branch}")
    require(document.get("publication_authorized") is False and document.get("ready_to_publish") is False, f"preapproval metadata boundary changed: {publication.branch}")
    require(any(row.get("identifier") == publication.source_doi and row.get("relation") == "isNewVersionOf" for row in value.get("related_identifiers", [])), f"candidate parent DOI relation missing: {publication.branch}")
    value["notes"] = (
        "Publication approved by Maria Smith on 29 July 2026. Paper and documentation: CC BY 4.0; "
        "repository code: Apache-2.0. This deposit is a new version of "
        f"{publication.source_doi} in the existing {publication.concept_doi} concept DOI lineage."
    )
    return value


def public_latest(publication: Publication) -> dict:
    current = public_request(f"{API}/records/{publication.source_record}")
    latest_url = current.get("links", {}).get("latest")
    require(latest_url, f"public latest link missing: {publication.branch}")
    latest = public_request(latest_url)
    require(current.get("id") == latest.get("id") == publication.source_record, f"source record is no longer latest: {publication.branch}")
    require(current.get("doi") == publication.source_doi and current.get("conceptdoi") == publication.concept_doi, f"public DOI lineage changed: {publication.branch}")
    require(current.get("metadata", {}).get("version") == publication.current_version, f"public source version changed: {publication.branch}")
    return current


def source_deposition(publication: Publication, access_token: str) -> dict:
    source = request(access_token, "GET", f"{API}/deposit/depositions/{publication.source_record}")
    require(source.get("submitted") is True, f"source deposition is not published: {publication.branch}")
    require(source.get("metadata", {}).get("version") == publication.current_version, f"authenticated source version changed: {publication.branch}")
    concept = source.get("conceptdoi") or source.get("metadata", {}).get("conceptdoi")
    require(concept == publication.concept_doi, f"authenticated concept DOI changed: {publication.branch}")
    latest_draft = source.get("links", {}).get("latest_draft", "").rstrip("/").rsplit("/", 1)[-1]
    require(latest_draft in {"", str(publication.source_record)}, f"an existing successor draft already exists for {publication.branch}: {latest_draft}")
    present = {item["filename"] for item in source.get("files", [])}
    require(set(publication.preserve_inherited).issubset(present), f"required inherited evidence missing: {publication.branch}")
    return source


def remote_file_map(deposition: dict) -> dict[str, tuple[int, str]]:
    return {
        item["filename"]: (int(item["filesize"]), item["checksum"].removeprefix("md5:"))
        for item in deposition.get("files", [])
    }


def expected_file_map(publication: Publication) -> dict[str, tuple[int, str]]:
    expected = {
        name: (path.stat().st_size, md5(path))
        for name, path in local_files(publication).items()
    }
    if publication.preserve_inherited:
        source = public_request(f"{API}/records/{publication.source_record}")
        source_files = {
            item["key"]: (int(item["size"]), item["checksum"].removeprefix("md5:"))
            for item in source.get("files", [])
        }
        for name in publication.preserve_inherited:
            require(name in source_files, f"published inherited evidence missing: {publication.branch}: {name}")
            require(name not in expected, f"release file collides with inherited evidence: {name}")
            expected[name] = source_files[name]
    return expected


def write_receipt(path: Path | None, value: dict) -> None:
    if path is None:
        return
    destination = path if path.is_absolute() else ROOT / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def preflight(publication: Publication, access_token: str) -> dict:
    approved, gated = approval_and_gate(publication)
    current = public_latest(publication)
    source = source_deposition(publication, access_token)
    files = local_files(publication)
    require(any(path.suffix.lower() == ".pdf" and sha256(path) == gated["pdf_sha256"] for path in files.values()), f"approved PDF absent from release: {publication.branch}")
    require(any(path.suffix.lower() == ".md" and sha256(path) == gated["manuscript_sha256"] for path in files.values()), f"approved manuscript absent from release: {publication.branch}")
    return {
        "branch": publication.branch,
        "status": "PASS",
        "mode": "authenticated-read-only",
        "source_record": publication.source_record,
        "source_doi": publication.source_doi,
        "concept_doi": publication.concept_doi,
        "current_version": publication.current_version,
        "candidate_version": publication.candidate_version,
        "source_file_count": len(source.get("files", [])),
        "release_file_count": len(files),
        "preserved_inherited_files": list(publication.preserve_inherited),
        "remote_updated": current.get("updated"),
        "approved_manuscript_sha256": approved["manuscript_sha256"],
        "approved_pdf_sha256": approved["pdf_sha256"],
        "remote_action_performed": False,
    }


def create_draft(publication: Publication, access_token: str) -> dict:
    check = preflight(publication, access_token)
    source_url = f"{API}/deposit/depositions/{publication.source_record}"
    created = request(access_token, "POST", f"{source_url}/actions/newversion")
    draft_url = created.get("links", {}).get("latest_draft")
    require(bool(draft_url), f"Zenodo returned no successor draft: {publication.branch}")
    draft = request(access_token, "GET", draft_url)
    concept = draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")
    require(draft.get("submitted") is False and concept == publication.concept_doi, f"successor draft lineage mismatch: {publication.branch}")
    return {
        **check,
        "status": "DRAFT_CREATED",
        "mode": "newversion-only",
        "draft_id": draft.get("id"),
        "reserved_doi": draft.get("metadata", {}).get("prereserve_doi", {}).get("doi"),
        "remote_action_performed": True,
        "new_record_created": False,
        "new_concept_doi_created": False,
    }


def stage(publication: Publication, draft_id: int, access_token: str) -> dict:
    approval_and_gate(publication)
    files = local_files(publication)
    draft_url = f"{API}/deposit/depositions/{draft_id}"
    draft = request(access_token, "GET", draft_url)
    require(draft.get("submitted") is False, f"draft is already published: {draft_id}")
    concept = draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")
    require(concept == publication.concept_doi, f"draft concept DOI mismatch: {publication.branch}")

    complete_expected = expected_file_map(publication)
    preserved = {}
    for inherited in draft.get("files", []):
        name = inherited["filename"]
        if name in publication.preserve_inherited:
            preserved[name] = (int(inherited["filesize"]), inherited["checksum"].removeprefix("md5:"))
            require(preserved[name] == complete_expected[name], f"inherited evidence checksum changed: {publication.branch}: {name}")
        else:
            request(access_token, "DELETE", inherited["links"]["self"])

    bucket = draft["links"]["bucket"].rstrip("/")
    expected = dict(preserved)
    for name, path in files.items():
        require(name not in expected, f"release file collides with preserved evidence: {name}")
        request(access_token, "PUT", f"{bucket}/{urllib.parse.quote(name, safe='')}", path.read_bytes(), "application/octet-stream")
        expected[name] = (path.stat().st_size, md5(path))
    require(expected == complete_expected, f"complete staged expectation mismatch: {publication.branch}")

    remote_metadata = metadata(publication)
    request(access_token, "PUT", draft_url, json.dumps({"metadata": remote_metadata}).encode("utf-8"), "application/json")
    verified = request(access_token, "GET", draft_url)
    require(remote_file_map(verified) == expected, f"staged file verification failed: {publication.branch}")
    verified_metadata = verified.get("metadata", {})
    require(verified_metadata.get("title") == remote_metadata["title"], f"staged title mismatch: {publication.branch}")
    require(verified_metadata.get("version") == publication.candidate_version, f"staged version mismatch: {publication.branch}")
    return {
        "branch": publication.branch,
        "status": "DRAFT_STAGED_VERIFIED",
        "draft_id": draft_id,
        "reserved_doi": verified_metadata.get("prereserve_doi", {}).get("doi"),
        "concept_doi": publication.concept_doi,
        "candidate_version": publication.candidate_version,
        "files": [
            {"filename": name, "bytes": size, "md5": checksum, "preserved_inherited": name in preserved}
            for name, (size, checksum) in sorted(expected.items())
        ],
        "remote_action_performed": True,
        "published": False,
    }


def publish(publication: Publication, draft_id: int, access_token: str) -> dict:
    approval_and_gate(publication)
    draft_url = f"{API}/deposit/depositions/{draft_id}"
    draft = request(access_token, "GET", draft_url)
    require(draft.get("submitted") is False, f"draft is already published: {draft_id}")
    concept = draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")
    require(concept == publication.concept_doi, f"draft concept DOI mismatch: {publication.branch}")
    require(draft.get("metadata", {}).get("version") == publication.candidate_version, f"draft version mismatch: {publication.branch}")
    expected = expected_file_map(publication)
    expected_names = set(expected)
    require(remote_file_map(draft) == expected, f"draft file checksum inventory mismatch: {publication.branch}")
    published = request(access_token, "POST", f"{draft_url}/actions/publish")
    record_id = int(published.get("record_id") or published.get("id"))
    record = public_request(f"{API}/records/{record_id}")
    require(record.get("conceptdoi") == publication.concept_doi, f"published concept DOI mismatch: {publication.branch}")
    require(record.get("metadata", {}).get("version") == publication.candidate_version, f"published version mismatch: {publication.branch}")
    published_files = {
        item["key"]: (int(item["size"]), item["checksum"].removeprefix("md5:"))
        for item in record.get("files", [])
    }
    require(published_files == expected, f"published file checksum inventory mismatch: {publication.branch}")
    return {
        "branch": publication.branch,
        "status": "PUBLISHED_VERIFIED",
        "source_record": publication.source_record,
        "source_doi": publication.source_doi,
        "record_id": record_id,
        "doi": record.get("doi"),
        "concept_doi": record.get("conceptdoi"),
        "version": record.get("metadata", {}).get("version"),
        "title": record.get("metadata", {}).get("title"),
        "publication_date": record.get("metadata", {}).get("publication_date"),
        "files": [
            {"filename": item["key"], "bytes": item["size"], "checksum": item["checksum"]}
            for item in sorted(record.get("files", []), key=lambda item: item["key"])
        ],
        "new_record_created": False,
        "new_concept_doi_created": False,
        "remote_action_performed": True,
        "published": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "create-draft", "stage", "publish"))
    parser.add_argument("--branch", required=True, choices=tuple(PUBLICATIONS))
    parser.add_argument("--draft", type=int)
    parser.add_argument("--receipt-out", type=Path)
    args = parser.parse_args()
    if args.action in {"stage", "publish"} and args.draft is None:
        parser.error(f"{args.action} requires --draft")
    publication = PUBLICATIONS[args.branch]
    access_token = token()
    if args.action == "preflight":
        result = preflight(publication, access_token)
    elif args.action == "create-draft":
        result = create_draft(publication, access_token)
    elif args.action == "stage":
        result = stage(publication, args.draft, access_token)
    else:
        result = publish(publication, args.draft, access_token)
    write_receipt(args.receipt_out, result)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
