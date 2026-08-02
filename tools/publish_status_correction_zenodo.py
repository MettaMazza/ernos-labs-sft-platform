#!/usr/bin/env python3
"""Issue and verify status-only patch versions of the 18 published SFT papers.

The correction is deliberately narrow: it replaces false prepublication
wording, records the real DOI, increments the patch version, and preserves the
scientific text, identifiers, evidence classifications, and machine records.
Every remote update uses Zenodo's ``newversion`` action on the current record.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import fitz


ROOT = Path(__file__).resolve().parents[1]
API = "https://zenodo.org/api"
DATE = "2026-08-02"
BASE_SUITE = ROOT / "publications/lean4_verification/LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"
BASE_RECORD = ROOT / "publications/lean4_verification/LEAN4_VERIFIED_ZENODO_PUBLICATION_RECORD_2026-08-02.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
STATE = ROOT / "audits/PUBLISHED_STATUS_CORRECTION_ZENODO_STATE_2026-08-02.json"
AUTHORIZATION = ROOT / "audits/PUBLISHED_STATUS_CORRECTION_MARIA_AUTHORIZATION_2026-08-02.json"
MANIFEST = ROOT / "publications/lean4_verification/PUBLISHED_STATUS_CORRECTION_SUITE_MANIFEST_2026-08-02.json"
AGGREGATE = ROOT / "publications/lean4_verification/PUBLISHED_STATUS_CORRECTION_ZENODO_PUBLICATION_RECORD_2026-08-02.json"
RECEIPTS = ROOT / "publications/lean4_verification/zenodo_receipts/published_status_correction"
PDF_ROOT = ROOT / "output/pdf/published_status_correction_2026-08-02"
PDF_MANIFEST = PDF_ROOT / "PDF_RENDER_MANIFEST.json"
AUDIT = ROOT / "audits/PUBLISHED_STATUS_CORRECTION_TEXT_AND_PDF_AUDIT_2026-08-02.json"
RELEASE_ROOT = ROOT / "output/release/published-status-correction-2026-08-02"
EXCLUDED = {"formal_verification_counterpaper", "strict_openai_comparison"}
CHEMISTRY_PRESERVED = {
    "04_Catalytic-Turnover-Complete-Supplementary-Data.zip",
    "05_USPTO-Full-Remapped-Reaction-Source.csv",
}
FORBIDDEN = (
    "unpublished local publication candidate",
    "final local publication candidate",
    "final local standalone publication candidate",
    "final publication candidate",
    "not approved, deposited or published",
    "not deposited or published",
    "not yet approved or deposited",
    "awaiting maria smith's approval",
    "pending the authorised new-version or new-record deposit",
    "pending a new standalone record after explicit confirmation",
    "no push, upload, doi action, release or publication is authorised",
    "no push, upload, doi creation, release or publication is authorised",
)
CLAIM_ID = re.compile(r"SFT-[A-Z0-9-]+")
SHA256_TEXT = re.compile(r"(?:sha256:)?[0-9a-f]{64}")
DOI_TEXT = re.compile(r"10\.5281/zenodo\.\d+")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


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
    path = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    value = path.read_text(encoding="utf-8").strip()
    require(bool(value), "Zenodo token file is empty")
    return value


def api_request(method: str, url: str, *, access_token: str | None = None, data: bytes | None = None, content_type: str | None = None) -> dict | None:
    headers = {"Accept": "application/json", "User-Agent": "Ernos-Labs-SFT-Status-Correction/1.0"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if content_type:
        headers["Content-Type"] = content_type
    for attempt in range(5):
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code in {408, 409, 425, 429, 500, 502, 503, 504} and attempt < 4:
                time.sleep(min(2 ** attempt, 16))
                continue
            raise RuntimeError(f"Zenodo {method} {url} failed with HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < 4:
                time.sleep(min(2 ** attempt, 16))
                continue
            raise RuntimeError(f"Zenodo {method} {url} failed: {exc}") from exc
    raise AssertionError("unreachable")


def patch_version(version: str) -> str:
    major, minor, patch = (int(part) for part in version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def version_token(version: str, *, full: bool) -> str:
    major, minor, patch = version.split(".")
    return f"V{major}_{minor}_{patch}" if full else f"V{major}_{minor}"


def corrected_path(path_text: str, old_version: str, new_version: str) -> str:
    path = Path(path_text)
    old_token = version_token(old_version, full=not old_version.endswith(".0"))
    new_token = version_token(new_version, full=True)
    name = path.name.replace(old_token, new_token, 1)
    require(name != path.name, f"version token not found in path: {path_text}")
    parent_text = path.parent.as_posix()
    old_dir = "v" + old_version.replace(".", "_")
    new_dir = "v" + new_version.replace(".", "_")
    if old_dir in parent_text:
        parent_text = parent_text.replace(old_dir, new_dir, 1)
    return (Path(parent_text) / name).as_posix()


def base_rows() -> list[dict]:
    suite = read_json(BASE_SUITE)
    published = {row["paper_id"]: row for row in read_json(BASE_RECORD)["records"]}
    rows = []
    for paper in suite["papers"]:
        paper_id = paper["paper_id"]
        if paper_id in EXCLUDED:
            continue
        current = published[paper_id]
        old_version = paper["version"]
        require(current["version"] == old_version, f"base version mismatch: {paper_id}")
        row = dict(paper)
        row.update(
            {
                "previous_version": old_version,
                "version": patch_version(old_version),
                "source": paper["output"],
                "source_sha256": sha256(ROOT / paper["output"]),
                "output": corrected_path(paper["output"], old_version, patch_version(old_version)),
                "evidence_map": corrected_path(paper["evidence_map"], old_version, patch_version(old_version)),
                "metadata": corrected_path(paper["metadata"], old_version, patch_version(old_version)),
                "parent_record_id": int(current["record_id"]),
                "parent_doi": current["doi"],
                "concept_doi": current["concept_doi"],
                "publication_status": "published_open_access",
                "status_correction_only": True,
            }
        )
        rows.append(row)
    require(len(rows) == 18, "correction scope must contain exactly 18 published papers")
    return rows


def load_state() -> dict:
    if STATE.is_file():
        return read_json(STATE)
    return {
        "schema": "sft.published_status_correction_zenodo_state.v1",
        "date": DATE,
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "status": "INITIALIZED",
        "papers": {},
    }


def save_state(state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    write_json(STATE, state)


def file_map(record: dict, *, public: bool) -> dict[str, tuple[int, str]]:
    if public:
        return {
            item["key"]: (int(item["size"]), item["checksum"].removeprefix("md5:"))
            for item in record.get("files", [])
        }
    return {
        item["filename"]: (int(item["filesize"]), item["checksum"].removeprefix("md5:"))
        for item in record.get("files", [])
    }


def preflight_row(row: dict, access_token: str, state: dict) -> dict:
    paper_id = row["paper_id"]
    public = api_request("GET", f"{API}/records/{row['parent_record_id']}")
    require(public and public.get("doi") == row["parent_doi"], f"parent record unavailable: {paper_id}")
    latest = api_request("GET", public["links"]["latest"])
    require(latest and int(latest["id"]) == row["parent_record_id"], f"parent is not latest: {paper_id}")
    require(public.get("conceptdoi") == row["concept_doi"], f"concept DOI mismatch: {paper_id}")
    require(public.get("metadata", {}).get("version") == row["previous_version"], f"parent version mismatch: {paper_id}")
    deposit = api_request("GET", f"{API}/deposit/depositions/{row['parent_record_id']}", access_token=access_token)
    require(deposit and deposit.get("submitted") is True, f"parent is not published: {paper_id}")
    latest_draft = deposit.get("links", {}).get("latest_draft", "").rstrip("/").rsplit("/", 1)[-1]
    known = str(state.get("papers", {}).get(paper_id, {}).get("draft_id", ""))
    require(latest_draft in {str(row["parent_record_id"]), known}, f"unknown successor draft exists: {paper_id}")
    if paper_id == "chemistry":
        require(CHEMISTRY_PRESERVED.issubset(file_map(public, public=True)), "chemistry preserved evidence missing")
    return public


def create_drafts() -> None:
    access_token = token()
    state = load_state()
    rows = base_rows()
    for row in rows:
        preflight_row(row, access_token, state)
    authorization = {
        "schema": "sft.published_status_correction_authorization.v1",
        "date": DATE,
        "authorizer": "Maria Smith",
        "authorized": True,
        "scope": "Correct only the false unpublished/local-candidate wording and issue updated versions of the 18 already-published papers in their existing Zenodo lineages.",
        "scientific_changes_authorized": False,
        "visual_reaudit_required": False,
        "source_instruction": "Direct user instruction in the Codex publication session on 2 August 2026.",
    }
    write_json(AUTHORIZATION, authorization)
    state["status"] = "CREATING_DRAFTS"
    save_state(state)
    for row in rows:
        paper_id = row["paper_id"]
        if state["papers"].get(paper_id, {}).get("draft_id"):
            print(f"DRAFT_REUSED paper={paper_id} draft={state['papers'][paper_id]['draft_id']}", flush=True)
            continue
        created = api_request(
            "POST",
            f"{API}/deposit/depositions/{row['parent_record_id']}/actions/newversion",
            access_token=access_token,
        )
        draft_url = (created or {}).get("links", {}).get("latest_draft")
        require(bool(draft_url), f"Zenodo returned no draft URL: {paper_id}")
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"invalid correction draft: {paper_id}")
        doi = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi")
        require(bool(doi), f"reserved DOI missing: {paper_id}")
        require((draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")) == row["concept_doi"], f"draft lineage mismatch: {paper_id}")
        state["papers"][paper_id] = {
            "paper_id": paper_id,
            "parent_record_id": row["parent_record_id"],
            "parent_doi": row["parent_doi"],
            "concept_doi": row["concept_doi"],
            "previous_version": row["previous_version"],
            "version": row["version"],
            "draft_id": int(draft["id"]),
            "reserved_doi": doi,
            "status": "DRAFT_CREATED",
            "created_at_utc": utc_now(),
        }
        save_state(state)
        print(f"DRAFT_CREATED paper={paper_id} version={row['version']} doi={doi}", flush=True)
    require(len(state["papers"]) == 18, "not all correction drafts were created")
    state["status"] = "ALL_DRAFTS_CREATED"
    save_state(state)


def published_block(doi: str, parent_doi: str) -> str:
    return (
        "> **Publication record.** Maria Smith authorised this status-only correction.\n"
        f"> It is published open access at [{doi}](https://doi.org/{doi}) through\n"
        f"> Zenodo's new-version route after [{parent_doi}](https://doi.org/{parent_doi})\n"
        "> in the same concept DOI lineage. The correction changes no scientific claim,\n"
        "> evidence classification, mathematical value, source identity or machine record."
    )


def transform_source(text: str, row: dict, doi: str) -> tuple[str, dict]:
    original = text
    counts: dict[str, int] = {}

    def substitute(name: str, pattern: str, replacement, *, count: int = 0, flags: int = 0) -> None:
        nonlocal text
        text, number = re.subn(pattern, replacement, text, count=count, flags=flags)
        counts[name] = number

    substitute(
        "header_version",
        rf"(?m)^\*\*Version:\*\* {re.escape(row['previous_version'])}\s*$",
        f"**Version:** {row['version']}  ",
        count=1,
    )
    substitute(
        "header_status",
        r"(?m)^\*\*Status:\*\* Final local(?: standalone)? publication candidate; not approved, deposited or published\s*$",
        "**Status:** Published open access; Zenodo record verified  ",
        count=1,
    )
    substitute(
        "pending_doi",
        r"(?m)^\*\*(?:Successor )?DOI:\*\* (?:Pending the authorised new-version or new-record deposit; no identifier has been invented|Pending a new standalone record after explicit confirmation; no DOI has been assigned or invented)\s*$",
        (
            f"**Correction predecessor:** Version {row['previous_version']} at `{row['source']}`  \n"
            f"**Correction predecessor DOI:** [{row['parent_doi']}](https://doi.org/{row['parent_doi']})  \n"
            f"**DOI:** [{doi}](https://doi.org/{doi})  "
        ),
        count=1,
    )
    substitute(
        "publication_control",
        r"(?ms)^> \*\*Publication control\.\*\*.*?(?=\n\n(?:> |## ))",
        published_block(doi, row["parent_doi"]),
        count=1,
    )
    substitute(
        "status_tables",
        r"(?m)^\| Publication status \| Version ([^|]+?) is a final(?: local)? publication candidate awaiting Maria Smith's approval\. It is not(?: yet)? deposited(?: or published)?\. \|$",
        lambda match: f"| Publication status | Version {match.group(1)} was published open access in its existing Zenodo concept DOI lineage. |",
    )
    substitute(
        "publication_banners",
        r"\*\*FINAL PUBLICATION CANDIDATE — NOT YET APPROVED OR DEPOSITED\.\*\*",
        "**PUBLISHED OPEN-ACCESS PAPER.**",
    )
    status_line = (
        f"| Publication status | Version {row['version']} is published open access at "
        f"[{doi}](https://doi.org/{doi}) in the existing Zenodo concept DOI lineage. |"
    )
    text, current_table_count = re.subn(
        r"(?m)^\| Publication status \|.*\|$",
        status_line,
        text,
        count=1,
    )
    counts["current_status_table"] = current_table_count
    require(counts["header_version"] == 1, f"version header not uniquely corrected: {row['paper_id']}")
    require(counts["header_status"] == 1, f"status header not uniquely corrected: {row['paper_id']}")
    require(counts["pending_doi"] == 1, f"pending DOI line not uniquely corrected: {row['paper_id']}")
    require(counts["publication_control"] == 1, f"publication control not uniquely corrected: {row['paper_id']}")
    require(counts["current_status_table"] == 1, f"current status table missing: {row['paper_id']}")
    lower = text.lower()
    remaining = [phrase for phrase in FORBIDDEN if phrase in lower]
    require(not remaining, f"prepublication wording remains in {row['paper_id']}: {remaining}")
    require(set(CLAIM_ID.findall(original)) == set(CLAIM_ID.findall(text)), f"claim identity changed: {row['paper_id']}")
    require(set(SHA256_TEXT.findall(original)) == set(SHA256_TEXT.findall(text)), f"machine hash identity changed: {row['paper_id']}")
    require(set(DOI_TEXT.findall(original)).issubset(set(DOI_TEXT.findall(text))), f"existing DOI was removed: {row['paper_id']}")
    return text.rstrip() + "\n", counts


def build_sources() -> None:
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_CREATED", "SOURCES_BUILT"}, "create all drafts first")
    papers = []
    transformations = []
    for row in base_rows():
        item = state["papers"][row["paper_id"]]
        doi = item["reserved_doi"]
        source_path = ROOT / row["source"]
        output_path = ROOT / row["output"]
        corrected, counts = transform_source(source_path.read_text(encoding="utf-8"), row, doi)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(corrected, encoding="utf-8")

        prior_evidence = read_json(ROOT / next(p["evidence_map"] for p in read_json(BASE_SUITE)["papers"] if p["paper_id"] == row["paper_id"]))
        evidence = dict(prior_evidence)
        evidence.update(
            {
                "version": row["version"],
                "publication_authorized": True,
                "remote_actions_performed": True,
                "publication_status": "PUBLISHED_OPEN_ACCESS",
                "doi": doi,
                "concept_doi": row["concept_doi"],
                "status_correction_only": True,
                "correction_predecessor_path": row["source"],
                "correction_predecessor_sha256": sha256(source_path),
            }
        )
        if "successor_path" in evidence:
            evidence.update({"source_path": row["source"], "source_sha256": sha256(source_path), "successor_path": row["output"], "successor_sha256": sha256(output_path)})
        else:
            evidence.update({"paper_path": row["output"], "paper_sha256": sha256(output_path)})
        write_json(ROOT / row["evidence_map"], evidence)

        prior_metadata = read_json(ROOT / next(p["metadata"] for p in read_json(BASE_SUITE)["papers"] if p["paper_id"] == row["paper_id"]))
        metadata = dict(prior_metadata.get("metadata", {}))
        metadata.update(
            {
                "title": row["title"],
                "version": row["version"],
                "publication_date": DATE,
                "description": f"Published open-access status correction for {row['title']}, version {row['version']}. This patch removes erroneous prepublication wording from the already-published paper and changes no scientific content.",
                "notes": f"Status-only correction authorised by Maria Smith. New version of {row['parent_doi']} in the existing {row['concept_doi']} concept DOI lineage. Scientific claims, evidence classifications, values, sources and machine records are unchanged.",
                "related_identifiers": [{"identifier": row["parent_doi"], "relation": "isNewVersionOf", "scheme": "doi"}],
            }
        )
        wrapper = {
            "paper_id": row["paper_id"],
            "publication_authorized": True,
            "ready_for_review": True,
            "ready_to_publish": True,
            "remote_action_permitted": True,
            "status_correction_only": True,
            "metadata": metadata,
        }
        write_json(ROOT / row["metadata"], wrapper)
        row.update(
            {
                "doi": doi,
                "output_sha256": sha256(output_path),
                "evidence_map_sha256": sha256(ROOT / row["evidence_map"]),
                "metadata_sha256": sha256(ROOT / row["metadata"]),
            }
        )
        papers.append(row)
        transformations.append({"paper_id": row["paper_id"], "counts": counts})
        print(f"SOURCE_CORRECTED paper={row['paper_id']} version={row['version']} doi={doi}", flush=True)

    lean_row = next(row for row in papers if row["paper_id"] == "lean4_whole_model_verification")
    cff_path = ROOT / "publications/lean4_verification/CITATION.cff"
    cff = cff_path.read_text(encoding="utf-8")
    cff = re.sub(r"(?m)^version: .*?$", f"version: {lean_row['version']}", cff, count=1)
    cff = re.sub(r"(?m)^doi: .*?$", f"doi: {lean_row['doi']}", cff, count=1)
    cff = re.sub(r'(?m)^url: "https://doi\.org/10\.5281/zenodo\.\d+"$', f'url: "https://doi.org/{lean_row["doi"]}"', cff, count=1)
    cff_path.write_text(cff, encoding="utf-8")

    manifest = {
        "schema": "sft.published_status_correction_suite.v1",
        "date": DATE,
        "status": "AUTHORIZED_STATUS_CORRECTION",
        "paper_count": 18,
        "publication_authority": "Maria Smith",
        "publication_authorized": True,
        "remote_actions_performed": True,
        "scientific_changes": False,
        "correction_scope": "False prepublication status wording, paper patch version, and DOI fields only.",
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "authorization_sha256": sha256(AUTHORIZATION),
        "base_suite": BASE_SUITE.relative_to(ROOT).as_posix(),
        "base_suite_sha256": sha256(BASE_SUITE),
        "base_publication_record": BASE_RECORD.relative_to(ROOT).as_posix(),
        "base_publication_record_sha256": sha256(BASE_RECORD),
        "lean_report_path": LEAN_REPORT.relative_to(ROOT).as_posix(),
        "lean_report_sha256": sha256(LEAN_REPORT),
        "papers": papers,
        "transformations": transformations,
    }
    write_json(MANIFEST, manifest)
    state["status"] = "SOURCES_BUILT"
    state["manifest"] = MANIFEST.relative_to(ROOT).as_posix()
    state["manifest_sha256"] = sha256(MANIFEST)
    save_state(state)


def copy_file(source: Path, destination: Path) -> None:
    require(source.is_file(), f"package source missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def audit_and_build_packages() -> None:
    state = load_state()
    require(state.get("status") in {"SOURCES_BUILT", "PACKAGES_BUILT"}, "build corrected sources first")
    manifest = read_json(MANIFEST)
    render = read_json(PDF_MANIFEST)
    render_by_id = {row["paper_id"]: row for row in render["papers"]}
    require(len(render_by_id) == 18 and render.get("status") == "PASS", "corrected PDF render is incomplete")
    audit_rows = []
    for paper in manifest["papers"]:
        record = render_by_id[paper["paper_id"]]
        pdf_path = ROOT / record["pdf"]
        require(record["source_sha256"] == paper["output_sha256"], f"PDF source mismatch: {paper['paper_id']}")
        require(sha256(pdf_path) == record["pdf_sha256"], f"PDF hash mismatch: {paper['paper_id']}")
        with fitz.open(pdf_path) as document:
            all_text = "\n".join(page.get_text("text", sort=True) for page in document)
            cover = document[0].get_text("text", sort=True).lower()
            require(paper["doi"].lower() in cover, f"correct DOI absent from PDF cover: {paper['paper_id']}")
            require("published open access" in cover and "zenodo record verified" in cover, f"published status absent from PDF cover: {paper['paper_id']}")
            remaining = [phrase for phrase in FORBIDDEN if phrase in all_text.lower()]
            require(not remaining, f"prepublication wording remains in PDF {paper['paper_id']}: {remaining}")
            audit_rows.append({"paper_id": paper["paper_id"], "version": paper["version"], "doi": paper["doi"], "pdf": record["pdf"], "pdf_sha256": record["pdf_sha256"], "page_count": document.page_count, "status": "PASS"})
        print(f"PDF_STATUS_PASS paper={paper['paper_id']} pages={audit_rows[-1]['page_count']}", flush=True)
    audit = {
        "schema": "sft.published_status_correction_text_pdf_audit.v1",
        "date": DATE,
        "generated_at_utc": utc_now(),
        "status": "PASS",
        "paper_count": 18,
        "page_count": sum(row["page_count"] for row in audit_rows),
        "scientific_changes": False,
        "visual_reaudit_performed": False,
        "checks": ["correct DOI on cover", "published-open-access status on cover", "forbidden prepublication wording absent from all extracted PDF text", "source and PDF hashes match manifests"],
        "papers": audit_rows,
    }
    write_json(AUDIT, audit)

    for paper in manifest["papers"]:
        paper_id = paper["paper_id"]
        version = paper["version"]
        slug = paper_id.replace("_", "-")
        directory = RELEASE_ROOT / f"{slug}-v{version}"
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        files = [
            (f"01_{slug}-v{version}.pdf", ROOT / render_by_id[paper_id]["pdf"]),
            (f"02_{slug}-v{version}.md", ROOT / paper["output"]),
            (f"03_{slug}-v{version}-Evidence-Map.json", ROOT / paper["evidence_map"]),
            ("04_SFT-Lean4-Whole-Model-Validation.json", LEAN_REPORT),
            ("05_Published-Status-Correction-Manifest.json", MANIFEST),
            ("06_Published-Status-Correction-Audit.json", AUDIT),
            ("07_Maria-Smith-Status-Correction-Authorization.json", AUTHORIZATION),
        ]
        if paper_id == "theory_of_everything":
            files.extend(
                [
                    ("08_Authoritative-Corpus-Inventory.json", ROOT / paper["inventory"]),
                    ("09_Exhaustive-ToE-Content-Matrix.json", ROOT / paper["matrix"]),
                ]
            )
        if paper_id == "lean4_whole_model_verification":
            files.append(("08_CITATION.cff", ROOT / "publications/lean4_verification/CITATION.cff"))
            prior_zip = ROOT / "output/release/lean4-verified-2026-08-02/lean4-whole-model-verification-v1.0.0/10_SFT-Lean4-Verification-Source-and-Evidence-v1.0.0.zip"
            files.append((f"09_SFT-Lean4-Verification-Source-and-Evidence-v{version}.zip", prior_zip))
        copied = []
        for name, source in files:
            target = directory / name
            copy_file(source, target)
            copied.append(target)
        package_manifest = {
            "schema": "sft.published_status_correction_package.v1",
            "paper_id": paper_id,
            "title": paper["title"],
            "version": version,
            "doi": paper["doi"],
            "concept_doi": paper["concept_doi"],
            "parent_doi": paper["parent_doi"],
            "status_correction_only": True,
            "scientific_changes": False,
            "files": [{"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "md5": md5(path)} for path in copied],
        }
        package_manifest_path = directory / "98_PACKAGE_MANIFEST.json"
        write_json(package_manifest_path, package_manifest)
        copied.append(package_manifest_path)
        sums = directory / "99_SHA256SUMS.txt"
        sums.write_text("".join(f"{sha256(path).removeprefix('sha256:')}  {path.name}\n" for path in sorted(copied)), encoding="utf-8")
        copied.append(sums)
        state["papers"][paper_id]["package_dir"] = directory.relative_to(ROOT).as_posix()
        state["papers"][paper_id]["package_files"] = [{"filename": path.name, "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "md5": md5(path)} for path in sorted(copied)]
        state["papers"][paper_id]["status"] = "PACKAGE_BUILT"
        save_state(state)
        print(f"PACKAGE_BUILT paper={paper_id} files={len(copied)}", flush=True)
    state["status"] = "PACKAGES_BUILT"
    save_state(state)


def package_map(state: dict, paper_id: str) -> dict[str, tuple[Path, int, str]]:
    result = {}
    for row in state["papers"][paper_id]["package_files"]:
        path = ROOT / row["path"]
        require(path.is_file() and path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"] and md5(path) == row["md5"], f"package changed: {paper_id}: {row['filename']}")
        result[row["filename"]] = (path, row["bytes"], row["md5"])
    return result


def expected_map(state: dict, paper: dict) -> dict[str, tuple[int, str]]:
    result = {name: (size, checksum) for name, (_, size, checksum) in package_map(state, paper["paper_id"]).items()}
    if paper["paper_id"] == "chemistry":
        parent = api_request("GET", f"{API}/records/{paper['parent_record_id']}")
        parent_files = file_map(parent or {}, public=True)
        for name in CHEMISTRY_PRESERVED:
            result[name] = parent_files[name]
    return result


def remote_metadata(paper: dict, draft: dict) -> dict:
    wrapper = read_json(ROOT / paper["metadata"])
    server_only = {"prereserve_doi", "doi", "conceptdoi"}
    value = {key: item for key, item in draft.get("metadata", {}).items() if key not in server_only}
    value.update(wrapper["metadata"])
    value.pop("subtitle", None)
    value.setdefault("upload_type", "publication")
    value.setdefault("publication_type", "article")
    value.setdefault("access_right", "open")
    value.setdefault("license", "cc-by-4.0")
    return value


def stage() -> None:
    access_token = token()
    state = load_state()
    require(state.get("status") in {"PACKAGES_BUILT", "ALL_DRAFTS_STAGED"}, "build packages first")
    papers = read_json(MANIFEST)["papers"]
    state["status"] = "STAGING"
    save_state(state)
    for paper in papers:
        paper_id = paper["paper_id"]
        draft_url = f"{API}/deposit/depositions/{state['papers'][paper_id]['draft_id']}"
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"draft not editable: {paper_id}")
        wanted = expected_map(state, paper)
        for inherited in list(draft.get("files", [])):
            if paper_id == "chemistry" and inherited["filename"] in CHEMISTRY_PRESERVED:
                continue
            api_request("DELETE", inherited["links"]["self"], access_token=access_token)
        bucket = draft["links"]["bucket"].rstrip("/")
        for name, (path, size, checksum) in package_map(state, paper_id).items():
            api_request("PUT", f"{bucket}/{urllib.parse.quote(name, safe='')}", access_token=access_token, data=path.read_bytes(), content_type="application/octet-stream")
            print(f"UPLOADED paper={paper_id} file={name} bytes={size}", flush=True)
        metadata = remote_metadata(paper, draft)
        api_request("PUT", draft_url, access_token=access_token, data=json.dumps({"metadata": metadata}).encode("utf-8"), content_type="application/json")
        verified = api_request("GET", draft_url, access_token=access_token)
        require(verified and file_map(verified, public=False) == wanted, f"staged files mismatch: {paper_id}")
        require(verified.get("metadata", {}).get("version") == paper["version"], f"staged version mismatch: {paper_id}")
        state["papers"][paper_id]["status"] = "DRAFT_STAGED_VERIFIED"
        save_state(state)
        print(f"STAGED_VERIFIED paper={paper_id}", flush=True)
    state["status"] = "ALL_DRAFTS_STAGED"
    save_state(state)


def verify_public_record(paper: dict, item: dict) -> dict:
    record = api_request("GET", f"{API}/records/{item['record_id']}")
    require(record and record.get("doi") == item["reserved_doi"], f"published DOI mismatch: {paper['paper_id']}")
    require(record.get("conceptdoi") == paper["concept_doi"], f"published lineage mismatch: {paper['paper_id']}")
    require(record.get("metadata", {}).get("version") == paper["version"], f"published version mismatch: {paper['paper_id']}")
    require(file_map(record, public=True) == expected_map(load_state(), paper), f"published files mismatch: {paper['paper_id']}")
    return record


def publish() -> None:
    access_token = token()
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_STAGED", "PUBLISHING", "PUBLISHED_VERIFIED"}, "stage every draft first")
    papers = read_json(MANIFEST)["papers"]
    state["status"] = "PUBLISHING"
    save_state(state)
    for paper in papers:
        paper_id = paper["paper_id"]
        item = state["papers"][paper_id]
        if item.get("status") == "PUBLISHED_VERIFIED":
            verify_public_record(paper, item)
            print(f"PUBLISHED_REUSED paper={paper_id} doi={item['doi']}", flush=True)
            continue
        if item.get("record_id"):
            record_id = int(item["record_id"])
        else:
            response = api_request("POST", f"{API}/deposit/depositions/{item['draft_id']}/actions/publish", access_token=access_token)
            record_id = int((response or {}).get("record_id") or (response or {}).get("id") or item["draft_id"])
            item["record_id"] = record_id
            save_state(state)
        record = api_request("GET", f"{API}/records/{record_id}")
        require(record and record.get("doi") == item["reserved_doi"], f"public record unavailable: {paper_id}")
        require(record.get("conceptdoi") == paper["concept_doi"] and record.get("metadata", {}).get("version") == paper["version"], f"public metadata mismatch: {paper_id}")
        require(file_map(record, public=True) == expected_map(state, paper), f"public files mismatch: {paper_id}")
        receipt = {
            "schema": "sft.published_status_correction_zenodo_receipt.v1",
            "paper_id": paper_id,
            "title": paper["title"],
            "version": paper["version"],
            "status": "PUBLISHED_VERIFIED",
            "status_correction_only": True,
            "scientific_changes": False,
            "parent_record_id": paper["parent_record_id"],
            "parent_doi": paper["parent_doi"],
            "record_id": record_id,
            "doi": record["doi"],
            "concept_doi": record["conceptdoi"],
            "published_at_utc": utc_now(),
            "record_url": record.get("links", {}).get("html") or f"https://zenodo.org/records/{record_id}",
            "files": [{"filename": file["key"], "bytes": int(file["size"]), "checksum": file["checksum"]} for file in sorted(record.get("files", []), key=lambda value: value["key"])],
        }
        receipt_path = RECEIPTS / f"{paper_id}-v{paper['version']}.json"
        write_json(receipt_path, receipt)
        item.update({"status": "PUBLISHED_VERIFIED", "record_id": record_id, "doi": record["doi"], "concept_doi": record["conceptdoi"], "receipt": receipt_path.relative_to(ROOT).as_posix(), "receipt_sha256": sha256(receipt_path), "published_at_utc": receipt["published_at_utc"]})
        save_state(state)
        print(f"PUBLISHED_VERIFIED paper={paper_id} version={paper['version']} doi={record['doi']}", flush=True)
    state["status"] = "PUBLISHED_VERIFIED"
    state["completed_at_utc"] = utc_now()
    save_state(state)
    write_aggregate(state, papers)


def write_aggregate(state: dict, papers: list[dict]) -> dict:
    records = []
    for paper in papers:
        item = state["papers"][paper["paper_id"]]
        require(item.get("status") == "PUBLISHED_VERIFIED", f"publication incomplete: {paper['paper_id']}")
        records.append({"paper_id": paper["paper_id"], "title": paper["title"], "version": paper["version"], "doi": item["doi"], "concept_doi": item["concept_doi"], "parent_doi": paper["parent_doi"], "record_id": item["record_id"], "receipt": item["receipt"], "receipt_sha256": item["receipt_sha256"]})
    aggregate = {
        "schema": "sft.published_status_correction_zenodo_record.v1",
        "date": DATE,
        "generated_at_utc": utc_now(),
        "status": "PUBLISHED_VERIFIED",
        "paper_count": 18,
        "status_correction_only": True,
        "scientific_changes": False,
        "manifest": MANIFEST.relative_to(ROOT).as_posix(),
        "manifest_sha256": sha256(MANIFEST),
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "authorization_sha256": sha256(AUTHORIZATION),
        "audit": AUDIT.relative_to(ROOT).as_posix(),
        "audit_sha256": sha256(AUDIT),
        "records": records,
    }
    write_json(AGGREGATE, aggregate)
    return aggregate


def verify() -> None:
    state = load_state()
    require(state.get("status") == "PUBLISHED_VERIFIED", "correction publication is incomplete")
    papers = read_json(MANIFEST)["papers"]
    rows = []
    for paper in papers:
        record = verify_public_record(paper, state["papers"][paper["paper_id"]])
        latest = api_request("GET", record["links"]["latest"])
        require(latest and int(latest["id"]) == int(record["id"]), f"correction is not latest: {paper['paper_id']}")
        rows.append({"paper_id": paper["paper_id"], "version": paper["version"], "doi": record["doi"], "concept_doi": record["conceptdoi"], "status": "PASS"})
    aggregate = write_aggregate(state, papers)
    print(json.dumps({"status": "PASS", "paper_count": len(rows), "aggregate": AGGREGATE.relative_to(ROOT).as_posix(), "aggregate_sha256": sha256(AGGREGATE), "records": rows}, indent=2, sort_keys=True), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("create-drafts", "build-sources", "audit-build-packages", "stage", "publish", "verify"))
    action = parser.parse_args().action
    actions = {
        "create-drafts": create_drafts,
        "build-sources": build_sources,
        "audit-build-packages": audit_and_build_packages,
        "stage": stage,
        "publish": publish,
        "verify": verify,
    }
    try:
        actions[action]()
    except Exception as exc:
        print(f"HALT action={action} error={exc}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
