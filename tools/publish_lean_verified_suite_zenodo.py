#!/usr/bin/env python3
"""Publish the authorised Lean-verified SFT suite to Zenodo, fail closed.

Seventeen papers are constrained to Zenodo's ``newversion`` action on their
exact existing records.  The standalone Lean paper is the only new concept
record this controller can create.  The two comparison papers without an
existing Zenodo lineage are intentionally outside this controller's scope.

The workflow is deliberately resumable and split into explicit actions:

    preflight -> create-drafts -> build-packages -> stage -> publish -> verify

Every draft identifier and every published result is persisted immediately.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile


ROOT = Path(__file__).resolve().parents[1]
API = "https://zenodo.org/api"
USER_AGENT = "Ernos-Labs-SFT-Lean4-Verified-Publication/1.0"
DATE = "2026-08-02"
AUTHORIZATION = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_MARIA_AUTHORIZATION_2026-08-02.json"
SUITE_MANIFEST = ROOT / "publications/lean4_verification/LEAN4_VERIFIED_PUBLICATION_SUITE_MANIFEST.json"
PDF_MANIFEST = ROOT / "output/pdf/lean4_verified_2026-08-02/PDF_RENDER_MANIFEST.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"
STATE_PATH = ROOT / "audits/LEAN4_VERIFIED_ZENODO_PUBLICATION_STATE_2026-08-02.json"
RELEASE_ROOT = ROOT / "output/release/lean4-verified-2026-08-02"
RECEIPT_ROOT = ROOT / "publications/lean4_verification/zenodo_receipts"
AGGREGATE_RECORD = ROOT / "publications/lean4_verification/LEAN4_VERIFIED_ZENODO_PUBLICATION_RECORD_2026-08-02.json"

GUIDANCE_AUDIT = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_GUIDANCE_AUDIT_2026-08-02.json"
PDF_AUDIT = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_PDF_AUDIT_2026-08-02.json"
VISUAL_AUDIT = ROOT / "audits/LEAN4_VERIFIED_PUBLICATION_VISUAL_QA_2026-08-02.json"

LEAN_PAPER_ID = "lean4_whole_model_verification"
EXCLUDED_PAPER_IDS = {
    "formal_verification_counterpaper",
    "strict_openai_comparison",
}
CHEMISTRY_PRESERVED = (
    "04_Catalytic-Turnover-Complete-Supplementary-Data.zip",
    "05_USPTO-Full-Remapped-Reaction-Source.csv",
)


@dataclass(frozen=True)
class Lineage:
    paper_id: str
    source_record: int
    source_doi: str
    concept_doi: str
    current_version: str
    preserve_inherited: tuple[str, ...] = ()


LINEAGES = {
    item.paper_id: item
    for item in (
        Lineage("theory_of_everything", 21717584, "10.5281/zenodo.21717584", "10.5281/zenodo.21717583", "0.1.0"),
        Lineage("methods", 21627646, "10.5281/zenodo.21627646", "10.5281/zenodo.21514889", "0.3.0"),
        Lineage("foundation", 21627656, "10.5281/zenodo.21627656", "10.5281/zenodo.21515628", "1.3.0"),
        Lineage("mathematics", 21688766, "10.5281/zenodo.21688766", "10.5281/zenodo.21516145", "1.5.0"),
        Lineage("information_science", 21688817, "10.5281/zenodo.21688817", "10.5281/zenodo.21516915", "1.4.0"),
        Lineage("computation", 21688837, "10.5281/zenodo.21688837", "10.5281/zenodo.21518310", "1.4.0"),
        Lineage("quantum_computation", 21688860, "10.5281/zenodo.21688860", "10.5281/zenodo.21518312", "1.4.0"),
        Lineage("physics", 21688879, "10.5281/zenodo.21688879", "10.5281/zenodo.21520880", "1.3.0"),
        Lineage("chemistry", 21688899, "10.5281/zenodo.21688899", "10.5281/zenodo.21531454", "1.3.0", CHEMISTRY_PRESERVED),
        Lineage("materials", 21688923, "10.5281/zenodo.21688923", "10.5281/zenodo.21532481", "1.3.0"),
        Lineage("biology", 21630203, "10.5281/zenodo.21630203", "10.5281/zenodo.21630202", "1.0.0"),
        Lineage("medicine", 21630785, "10.5281/zenodo.21630785", "10.5281/zenodo.21630784", "1.0.0"),
        Lineage("consciousness_cognitive_science", 21636397, "10.5281/zenodo.21636397", "10.5281/zenodo.21636396", "1.0.0"),
        Lineage("earth_environment", 21640810, "10.5281/zenodo.21640810", "10.5281/zenodo.21640809", "1.0.0"),
        Lineage("astronomy_cosmology", 21640812, "10.5281/zenodo.21640812", "10.5281/zenodo.21640811", "1.0.0"),
        Lineage("social_collective_systems", 21640814, "10.5281/zenodo.21640814", "10.5281/zenodo.21640813", "1.0.0"),
        Lineage("engineering_translation", 21640816, "10.5281/zenodo.21640816", "10.5281/zenodo.21640815", "1.0.0"),
    )
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> dict:
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
    path = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    value = path.read_text(encoding="utf-8").strip()
    require(bool(value), "Zenodo token file is empty")
    return value


def api_request(
    method: str,
    url: str,
    *,
    access_token: str | None = None,
    data: bytes | None = None,
    content_type: str | None = None,
    attempts: int = 5,
) -> dict | None:
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if content_type:
        headers["Content-Type"] = content_type
    for attempt in range(attempts):
        call = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(call, timeout=600) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            retryable = exc.code in {408, 409, 425, 429, 500, 502, 503, 504}
            if retryable and attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 16))
                continue
            raise RuntimeError(f"Zenodo {method} {url} failed with HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt + 1 < attempts:
                time.sleep(min(2 ** attempt, 16))
                continue
            raise RuntimeError(f"Zenodo {method} {url} failed: {exc}") from exc
    raise AssertionError("unreachable")


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_state() -> dict:
    if STATE_PATH.is_file():
        return read_json(STATE_PATH)
    return {
        "schema": "sft.lean4_verified_zenodo_publication_state.v1",
        "date": DATE,
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
        "status": "INITIALIZED",
        "papers": {},
    }


def save_state(state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    write_json(STATE_PATH, state)


def suite_papers() -> tuple[list[dict], dict[str, dict], dict[str, dict]]:
    suite = read_json(SUITE_MANIFEST)
    papers = suite["papers"]
    by_id = {row["paper_id"]: row for row in papers}
    pdfs = {row["paper_id"]: row for row in read_json(PDF_MANIFEST)["papers"]}
    return papers, by_id, pdfs


def included_papers() -> list[dict]:
    papers, _, _ = suite_papers()
    return [row for row in papers if row["paper_id"] in LINEAGES or row["paper_id"] == LEAN_PAPER_ID]


def verify_local_authority() -> dict:
    authorization = read_json(AUTHORIZATION)
    require(authorization.get("authorized") is True and authorization.get("authorizer") == "Maria Smith", "publication authorization is absent")
    for name, bound in authorization["bound_local_evidence"].items():
        path = ROOT / bound["path"]
        require(path.is_file(), f"authorization-bound evidence is missing: {name}")
        require(sha256(path) == bound["sha256"], f"authorization-bound evidence changed: {name}")

    guidance = read_json(GUIDANCE_AUDIT)
    pdf_audit = read_json(PDF_AUDIT)
    visual = read_json(VISUAL_AUDIT)
    report = read_json(LEAN_REPORT)
    require(guidance.get("status") == "PASS" and guidance["summary"]["passes"] == 20 and guidance["summary"]["halts"] == 0, "publication-guidance audit is not a clean 20/20 PASS")
    require(pdf_audit.get("status") == "PASS" and pdf_audit["summary"]["paper_count"] == 20 and pdf_audit["summary"]["page_count"] == 13508 and pdf_audit["summary"]["failure_count"] == 0, "PDF audit is not a clean 20-paper PASS")
    require(visual.get("status") == "PASS" and visual.get("paper_count") == 20 and visual.get("page_count") == 13508 and visual.get("finding_count") == 0, "visual QA audit is not a clean 20-paper PASS")
    require(visual.get("publication_authorized") is True and visual.get("confirmation_received") is True, "visual QA publication confirmation is absent")
    expected_result = {
        "status": "PASS",
        "claim_count": 2777,
        "accepted_claim_count": 2777,
        "source_binding_passed_claim_count": 2777,
        "candidate_count": 898902,
        "decision_count": 898902,
        "control_count": 11108,
        "branch_count": 17,
        "issue_count": 0,
    }
    for key, expected in expected_result.items():
        require(report.get(key) == expected, f"Lean report mismatch: {key}")

    papers, by_id, pdfs = suite_papers()
    require(len(papers) == 20 and len(by_id) == 20 and len(pdfs) == 20, "publication suite is not exactly 20 papers")
    require(set(by_id) == set(pdfs), "manuscript/PDF suite identities differ")
    require(set(LINEAGES) | {LEAN_PAPER_ID} | EXCLUDED_PAPER_IDS == set(by_id), "publication scope differs from the authorized 17+1+2 partition")
    for paper_id, row in by_id.items():
        source = ROOT / row["output"]
        evidence = ROOT / row["evidence_map"]
        pdf = ROOT / pdfs[paper_id]["pdf"]
        require(source.is_file() and evidence.is_file() and pdf.is_file(), f"publication artifact missing: {paper_id}")
        require(sha256(source) == row["output_sha256"] == pdfs[paper_id]["source_sha256"], f"manuscript identity mismatch: {paper_id}")
        require(sha256(evidence) == row["evidence_map_sha256"], f"evidence-map identity mismatch: {paper_id}")
        require(sha256(pdf) == pdfs[paper_id]["pdf_sha256"], f"PDF identity mismatch: {paper_id}")
        require(row["version"] == pdfs[paper_id]["version"], f"version mismatch: {paper_id}")
    return {
        "status": "PASS",
        "authorized_candidate_manifest_sha256": sha256(SUITE_MANIFEST),
        "paper_count": 20,
        "existing_lineage_update_count": 17,
        "new_standalone_count": 1,
        "excluded_no_lineage_count": 2,
        "page_count": 13508,
        "lean_result": expected_result,
    }


def deposition_file_map(deposition: dict) -> dict[str, tuple[int, str]]:
    return {
        item["filename"]: (int(item["filesize"]), item["checksum"].removeprefix("md5:"))
        for item in deposition.get("files", [])
    }


def record_file_map(record: dict) -> dict[str, tuple[int, str]]:
    return {
        item["key"]: (int(item["size"]), item["checksum"].removeprefix("md5:"))
        for item in record.get("files", [])
    }


def remote_preflight(access_token: str, state: dict) -> dict:
    rows = []
    for paper_id, lineage in LINEAGES.items():
        public = api_request("GET", f"{API}/records/{lineage.source_record}")
        require(public and public.get("id") == lineage.source_record, f"published source record missing: {paper_id}")
        latest = api_request("GET", public["links"]["latest"])
        require(latest and latest.get("id") == lineage.source_record, f"configured source is no longer latest: {paper_id}")
        require(public.get("doi") == lineage.source_doi and public.get("conceptdoi") == lineage.concept_doi, f"public DOI lineage changed: {paper_id}")
        require(public.get("metadata", {}).get("version") == lineage.current_version, f"public parent version changed: {paper_id}")
        source = api_request("GET", f"{API}/deposit/depositions/{lineage.source_record}", access_token=access_token)
        require(source and source.get("submitted") is True, f"authenticated source is not published: {paper_id}")
        latest_draft = source.get("links", {}).get("latest_draft", "").rstrip("/").rsplit("/", 1)[-1]
        known_draft = str(state.get("papers", {}).get(paper_id, {}).get("draft_id", ""))
        require(latest_draft in {str(lineage.source_record), known_draft}, f"unrecognized successor draft already exists: {paper_id}: {latest_draft}")
        present = set(deposition_file_map(source))
        require(set(lineage.preserve_inherited).issubset(present), f"required inherited chemistry evidence is missing: {paper_id}")
        rows.append({
            "paper_id": paper_id,
            "source_record": lineage.source_record,
            "source_doi": lineage.source_doi,
            "concept_doi": lineage.concept_doi,
            "current_version": lineage.current_version,
            "status": "PASS",
        })

    if not state.get("papers", {}).get(LEAN_PAPER_ID, {}).get("draft_id"):
        title = next(row["title"] for row in included_papers() if row["paper_id"] == LEAN_PAPER_ID)
        query = urllib.parse.urlencode({"q": f'title:\"{title}\"', "size": 25})
        search = api_request("GET", f"{API}/records?{query}") or {}
        exact = [
            hit for hit in search.get("hits", {}).get("hits", [])
            if hit.get("metadata", {}).get("title") == title
            and hit.get("metadata", {}).get("version") == "1.0.0"
            and any(c.get("name") == "Smith, Maria" for c in hit.get("metadata", {}).get("creators", []))
        ]
        require(not exact, "a published Lean 1.0.0 record already exists but is not in the publication state")
    return {"status": "PASS", "existing_lineages": rows, "lean_duplicate_count": 0}


def preflight() -> dict:
    local = verify_local_authority()
    state = load_state()
    remote = remote_preflight(token(), state)
    result = {"status": "PASS", "mode": "authenticated-read-only", "local": local, "remote": remote, "remote_action_performed": False}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def create_drafts() -> dict:
    authority = verify_local_authority()
    access_token = token()
    state = load_state()
    remote_preflight(access_token, state)
    _, by_id, _ = suite_papers()
    state["authorized_candidate_manifest_sha256"] = authority["authorized_candidate_manifest_sha256"]
    state["status"] = "CREATING_DRAFTS"
    save_state(state)
    for paper in included_papers():
        paper_id = paper["paper_id"]
        existing = state["papers"].get(paper_id, {})
        if existing.get("draft_id"):
            draft = api_request("GET", f"{API}/deposit/depositions/{existing['draft_id']}", access_token=access_token)
            require(draft is not None, f"recorded draft is unavailable: {paper_id}")
            print(f"DRAFT_REUSED paper={paper_id} draft={existing['draft_id']}", flush=True)
            continue
        if paper_id in LINEAGES:
            lineage = LINEAGES[paper_id]
            created = api_request("POST", f"{API}/deposit/depositions/{lineage.source_record}/actions/newversion", access_token=access_token)
            draft_url = created.get("links", {}).get("latest_draft") if created else None
            require(bool(draft_url), f"Zenodo returned no successor draft: {paper_id}")
            draft = api_request("GET", draft_url, access_token=access_token)
            require(draft and draft.get("submitted") is False, f"successor draft invalid: {paper_id}")
            concept = draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")
            require(concept == lineage.concept_doi, f"successor concept DOI mismatch: {paper_id}")
            mode = "newversion"
        else:
            draft = api_request("POST", f"{API}/deposit/depositions", access_token=access_token, data=b"{}", content_type="application/json")
            require(draft and draft.get("submitted") is False, "Lean draft creation failed")
            mode = "new_standalone_record"
        draft_id = int(draft["id"])
        reserved_doi = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi")
        require(bool(reserved_doi), f"reserved DOI absent: {paper_id}")
        state["papers"][paper_id] = {
            "paper_id": paper_id,
            "title": by_id[paper_id]["title"],
            "version": by_id[paper_id]["version"],
            "mode": mode,
            "draft_id": draft_id,
            "reserved_doi": reserved_doi,
            "created_at_utc": utc_now(),
            "status": "DRAFT_CREATED",
        }
        save_state(state)
        print(f"DRAFT_CREATED paper={paper_id} draft={draft_id} doi={reserved_doi} mode={mode}", flush=True)
    require(len(state["papers"]) == 18, "not all 18 authorized drafts were created")
    state["status"] = "ALL_DRAFTS_CREATED"
    save_state(state)
    result = {"status": state["status"], "papers": state["papers"]}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def copy_file(source: Path, destination: Path) -> None:
    require(source.is_file(), f"package source missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def build_lean_archive(destination: Path) -> None:
    sources: set[Path] = set()
    lean_root = ROOT / "generated/lean4_validation"
    for path in lean_root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(lean_root)
        if any(part in {".elan", ".lake", "source_mismatch_backup_2026-08-02"} for part in relative.parts):
            continue
        sources.add(path)
    for relative in (
        "census/claims.json",
        "census/execution_manifest.json",
        "publication guidance.md",
        "audits/LEAN4_WHOLE_MODEL_VERIFICATION_2026-08-02.md",
        "audits/LEAN4_VERIFIED_PUBLICATION_GUIDANCE_AUDIT_2026-08-02.json",
        "audits/LEAN4_VERIFIED_PUBLICATION_GUIDANCE_AUDIT_2026-08-02.md",
        "audits/LEAN4_VERIFIED_PUBLICATION_PDF_AUDIT_2026-08-02.json",
        "audits/LEAN4_VERIFIED_PUBLICATION_PDF_AUDIT_2026-08-02.md",
        "audits/LEAN4_VERIFIED_PUBLICATION_VISUAL_QA_2026-08-02.json",
        "audits/LEAN4_VERIFIED_PUBLICATION_VISUAL_QA_2026-08-02.md",
        "audits/LEAN4_VERIFIED_PUBLICATION_MARIA_AUTHORIZATION_2026-08-02.json",
        "tools/build_lean_verified_publication_suite.py",
        "tools/audit_lean_verified_publication_guidance.py",
        "tools/audit_lean_verified_publication_pdfs.py",
        "tools/render_lean_verified_publication_suite.py",
    ):
        path = ROOT / relative
        require(path.is_file(), f"Lean archive input missing: {relative}")
        sources.add(path)
    fixed_time = (2026, 8, 2, 0, 0, 0)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(sources):
            relative = source.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(relative, fixed_time)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o644 & 0xFFFF) << 16
            archive.writestr(info, source.read_bytes())


def build_packages() -> dict:
    authority = verify_local_authority()
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_CREATED", "PACKAGES_BUILT", "ALL_DRAFTS_STAGED", "PUBLISHING", "PUBLISHED_VERIFIED"}, "create all drafts before building DOI-bound packages")
    require(len(state.get("papers", {})) == 18, "publication state does not contain 18 drafts")
    _, by_id, pdfs = suite_papers()
    lean_doi = state["papers"][LEAN_PAPER_ID]["reserved_doi"]
    cff = ROOT / "publications/lean4_verification/CITATION.cff"
    require(lean_doi in cff.read_text(encoding="utf-8"), "Lean CITATION.cff must contain the reserved DOI before packages are built")
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    built = []
    common = (
        ("04_SFT-Lean4-Whole-Model-Validation.json", LEAN_REPORT),
        ("05_Publication-Guidance-Audit.json", GUIDANCE_AUDIT),
        ("06_Publication-PDF-Audit.json", PDF_AUDIT),
        ("07_Publication-Visual-QA-Audit.json", VISUAL_AUDIT),
        ("08_Maria-Smith-Publication-Authorization.json", AUTHORIZATION),
    )
    for paper in included_papers():
        paper_id = paper["paper_id"]
        version = paper["version"]
        slug = paper_id.replace("_", "-")
        directory = RELEASE_ROOT / f"{slug}-v{version}"
        directory.mkdir(parents=True, exist_ok=True)
        files: list[tuple[str, Path]] = [
            (f"01_{slug}-v{version}.pdf", ROOT / pdfs[paper_id]["pdf"]),
            (f"02_{slug}-v{version}.md", ROOT / paper["output"]),
            (f"03_{slug}-v{version}-Evidence-Map.json", ROOT / paper["evidence_map"]),
            *common,
        ]
        if paper_id == "theory_of_everything":
            files.extend((
                ("09_Authoritative-Corpus-Inventory.json", ROOT / paper["inventory"]),
                ("10_Exhaustive-ToE-Content-Matrix.json", ROOT / paper["matrix"]),
            ))
        if paper_id == LEAN_PAPER_ID:
            files.append(("09_CITATION.cff", cff))
            archive_path = directory / f"10_SFT-Lean4-Verification-Source-and-Evidence-v{version}.zip"
            build_lean_archive(archive_path)
            files.append((archive_path.name, archive_path))
        copied: list[Path] = []
        for public_name, source in files:
            destination = directory / public_name
            if source != destination:
                copy_file(source, destination)
            copied.append(destination)
        lineage = LINEAGES.get(paper_id)
        package_manifest = {
            "schema": "sft.lean4_verified_zenodo_package.v1",
            "paper_id": paper_id,
            "title": paper["title"],
            "version": version,
            "publication_date": DATE,
            "publication_mode": "newversion" if lineage else "new_standalone_record",
            "reserved_doi": state["papers"][paper_id]["reserved_doi"],
            "source_record": lineage.source_record if lineage else None,
            "source_doi": lineage.source_doi if lineage else None,
            "concept_doi": lineage.concept_doi if lineage else None,
            "preserved_inherited_files": list(lineage.preserve_inherited) if lineage else [],
            "authorized_candidate_manifest": SUITE_MANIFEST.relative_to(ROOT).as_posix(),
            "authorized_candidate_manifest_sha256": authority["authorized_candidate_manifest_sha256"],
            "lean_report": LEAN_REPORT.relative_to(ROOT).as_posix(),
            "lean_report_sha256": sha256(LEAN_REPORT),
            "lean_result": authority["lean_result"],
            "files": [
                {"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256(path), "md5": md5(path)}
                for path in copied
            ],
        }
        manifest_path = directory / "98_PACKAGE_MANIFEST.json"
        write_json(manifest_path, package_manifest)
        copied.append(manifest_path)
        sums_path = directory / "99_SHA256SUMS.txt"
        sums_path.write_text("".join(f"{sha256(path).removeprefix('sha256:')}  {path.name}\n" for path in sorted(copied)), encoding="utf-8")
        copied.append(sums_path)
        state["papers"][paper_id]["package_dir"] = directory.relative_to(ROOT).as_posix()
        state["papers"][paper_id]["package_files"] = [
            {"filename": path.name, "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path), "md5": md5(path)}
            for path in sorted(copied)
        ]
        state["papers"][paper_id]["status"] = "PACKAGE_BUILT"
        state["papers"][paper_id]["package_built_at_utc"] = utc_now()
        save_state(state)
        built.append({"paper_id": paper_id, "files": len(copied), "bytes": sum(path.stat().st_size for path in copied)})
        print(f"PACKAGE_BUILT paper={paper_id} files={len(copied)} bytes={built[-1]['bytes']}", flush=True)
    state["status"] = "PACKAGES_BUILT"
    save_state(state)
    result = {"status": state["status"], "packages": built, "total_bytes": sum(row["bytes"] for row in built)}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def package_file_map(state: dict, paper_id: str) -> dict[str, tuple[Path, int, str]]:
    rows = state["papers"][paper_id].get("package_files", [])
    require(bool(rows), f"package state missing: {paper_id}")
    result = {}
    for row in rows:
        path = ROOT / row["path"]
        require(path.is_file(), f"package file missing: {paper_id}: {row['filename']}")
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"] and md5(path) == row["md5"], f"package file changed: {paper_id}: {row['filename']}")
        result[row["filename"]] = (path, row["bytes"], row["md5"])
    return result


def complete_expected_map(state: dict, paper_id: str) -> dict[str, tuple[int, str]]:
    expected = {name: (size, digest) for name, (_, size, digest) in package_file_map(state, paper_id).items()}
    lineage = LINEAGES.get(paper_id)
    if lineage and lineage.preserve_inherited:
        source = api_request("GET", f"{API}/records/{lineage.source_record}")
        require(source is not None, f"published chemistry source missing: {paper_id}")
        published = record_file_map(source)
        for name in lineage.preserve_inherited:
            require(name in published and name not in expected, f"preserved evidence conflict: {paper_id}: {name}")
            expected[name] = published[name]
    return expected


def candidate_metadata(paper: dict) -> dict:
    document = read_json(ROOT / paper["metadata"])
    metadata = dict(document["metadata"])
    require(metadata.get("version") == paper["version"], f"candidate metadata version mismatch: {paper['paper_id']}")
    return metadata


def remote_metadata(paper: dict, draft: dict) -> dict:
    paper_id = paper["paper_id"]
    server_only = {"prereserve_doi", "doi", "conceptdoi"}
    value = {key: val for key, val in draft.get("metadata", {}).items() if key not in server_only}
    candidate = candidate_metadata(paper)
    subtitle = candidate.pop("subtitle", None)
    value.update(candidate)
    value["title"] = paper["title"]
    value["version"] = paper["version"]
    value.setdefault("upload_type", "publication")
    value.setdefault("publication_type", "article")
    value.setdefault("access_right", "open")
    value.setdefault("license", "cc-by-4.0")
    value.setdefault("publication_date", DATE)
    if not value.get("description"):
        value["description"] = subtitle or paper["title"]
    if subtitle and subtitle not in value["description"]:
        value["description"] = f"{value['description']}\n\n{subtitle}"
    lineage = LINEAGES.get(paper_id)
    if lineage:
        non_version_relations = [
            row for row in value.get("related_identifiers", [])
            if row.get("relation") not in {"isNewVersionOf", "isVersionOf"}
        ]
        value["related_identifiers"] = non_version_relations + [
            {"identifier": lineage.source_doi, "relation": "isNewVersionOf", "scheme": "doi"}
        ]
        value["notes"] = (
            "Publication explicitly authorised by Maria Smith on 2 August 2026. "
            f"This deposit is a new version of {lineage.source_doi} in the existing "
            f"{lineage.concept_doi} concept DOI lineage. The release is bound to the "
            "Lean 4 whole-model PASS and the included publication audits."
        )
    else:
        value.pop("related_identifiers", None)
        value["notes"] = (
            "Standalone Lean 4 verification paper explicitly authorised for publication "
            "by Maria Smith on 2 August 2026. The release includes the proof sources, "
            "machine report, evidence map, and publication audits."
        )
    return value


def stage() -> dict:
    verify_local_authority()
    access_token = token()
    state = load_state()
    require(state.get("status") in {"PACKAGES_BUILT", "ALL_DRAFTS_STAGED"}, "build all DOI-bound packages before staging")
    _, by_id, _ = suite_papers()
    state["status"] = "STAGING"
    save_state(state)
    for paper in included_papers():
        paper_id = paper["paper_id"]
        draft_id = int(state["papers"][paper_id]["draft_id"])
        draft_url = f"{API}/deposit/depositions/{draft_id}"
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"draft is not editable: {paper_id}")
        lineage = LINEAGES.get(paper_id)
        if lineage:
            concept = draft.get("conceptdoi") or draft.get("metadata", {}).get("conceptdoi")
            require(concept == lineage.concept_doi, f"draft lineage mismatch: {paper_id}")
        expected = complete_expected_map(state, paper_id)
        preserved: dict[str, tuple[int, str]] = {}
        for inherited in list(draft.get("files", [])):
            name = inherited["filename"]
            if lineage and name in lineage.preserve_inherited:
                present = (int(inherited["filesize"]), inherited["checksum"].removeprefix("md5:"))
                require(present == expected[name], f"preserved evidence checksum mismatch: {paper_id}: {name}")
                preserved[name] = present
            else:
                api_request("DELETE", inherited["links"]["self"], access_token=access_token)
        bucket = draft["links"]["bucket"].rstrip("/")
        for name, (path, size, digest) in package_file_map(state, paper_id).items():
            encoded = urllib.parse.quote(name, safe="")
            api_request("PUT", f"{bucket}/{encoded}", access_token=access_token, data=path.read_bytes(), content_type="application/octet-stream")
            print(f"UPLOADED paper={paper_id} file={name} bytes={size} md5={digest}", flush=True)
        metadata = remote_metadata(by_id[paper_id], draft)
        api_request("PUT", draft_url, access_token=access_token, data=json.dumps({"metadata": metadata}).encode("utf-8"), content_type="application/json")
        verified = api_request("GET", draft_url, access_token=access_token)
        require(verified and deposition_file_map(verified) == expected, f"staged file inventory mismatch: {paper_id}")
        verified_metadata = verified.get("metadata", {})
        require(verified_metadata.get("title") == paper["title"] and verified_metadata.get("version") == paper["version"], f"staged metadata mismatch: {paper_id}")
        state["papers"][paper_id]["status"] = "DRAFT_STAGED_VERIFIED"
        state["papers"][paper_id]["staged_at_utc"] = utc_now()
        state["papers"][paper_id]["staged_file_count"] = len(expected)
        save_state(state)
        print(f"STAGED_VERIFIED paper={paper_id} draft={draft_id} files={len(expected)}", flush=True)
    state["status"] = "ALL_DRAFTS_STAGED"
    save_state(state)
    result = {"status": state["status"], "paper_count": 18}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def verify_all_staged(state: dict, access_token: str) -> None:
    for paper in included_papers():
        paper_id = paper["paper_id"]
        require(state["papers"][paper_id].get("status") in {"DRAFT_STAGED_VERIFIED", "PUBLISHED_VERIFIED"}, f"paper is not staged: {paper_id}")
        if state["papers"][paper_id].get("status") == "PUBLISHED_VERIFIED":
            continue
        if state["papers"][paper_id].get("publish_response_record_id"):
            public_record_verified(paper, int(state["papers"][paper_id]["publish_response_record_id"]), state)
            continue
        draft = api_request("GET", f"{API}/deposit/depositions/{state['papers'][paper_id]['draft_id']}", access_token=access_token)
        require(draft and draft.get("submitted") is False, f"staged draft unavailable: {paper_id}")
        require(deposition_file_map(draft) == complete_expected_map(state, paper_id), f"staged draft changed: {paper_id}")
        require(draft.get("metadata", {}).get("version") == paper["version"], f"staged version changed: {paper_id}")


def published_receipt(state: dict, paper: dict, record: dict) -> dict:
    paper_id = paper["paper_id"]
    lineage = LINEAGES.get(paper_id)
    files = [
        {"filename": item["key"], "bytes": int(item["size"]), "checksum": item["checksum"]}
        for item in sorted(record.get("files", []), key=lambda row: row["key"])
    ]
    return {
        "schema": "sft.lean4_verified_zenodo_publication_receipt.v1",
        "paper_id": paper_id,
        "title": record.get("metadata", {}).get("title"),
        "version": record.get("metadata", {}).get("version"),
        "publication_date": record.get("metadata", {}).get("publication_date"),
        "published_at_utc": utc_now(),
        "status": "PUBLISHED_VERIFIED",
        "publication_mode": "newversion" if lineage else "new_standalone_record",
        "source_record": lineage.source_record if lineage else None,
        "source_doi": lineage.source_doi if lineage else None,
        "record_id": int(record["id"]),
        "doi": record.get("doi"),
        "concept_doi": record.get("conceptdoi"),
        "same_existing_concept_lineage": bool(lineage and record.get("conceptdoi") == lineage.concept_doi),
        "new_concept_record_created": lineage is None,
        "record_url": record.get("links", {}).get("html") or f"https://zenodo.org/records/{record['id']}",
        "files": files,
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "authorization_sha256": sha256(AUTHORIZATION),
        "authorized_candidate_manifest_sha256": state["authorized_candidate_manifest_sha256"],
        "lean_report": LEAN_REPORT.relative_to(ROOT).as_posix(),
        "lean_report_sha256": sha256(LEAN_REPORT),
    }


def public_record_verified(paper: dict, record_id: int, state: dict) -> dict:
    record = api_request("GET", f"{API}/records/{record_id}")
    require(record and int(record["id"]) == record_id, f"published record unavailable: {paper['paper_id']}")
    require(record.get("doi") == state["papers"][paper["paper_id"]]["reserved_doi"], f"published DOI differs from reservation: {paper['paper_id']}")
    require(record.get("metadata", {}).get("version") == paper["version"] and record.get("metadata", {}).get("title") == paper["title"], f"published metadata mismatch: {paper['paper_id']}")
    require(record_file_map(record) == complete_expected_map(state, paper["paper_id"]), f"published file inventory mismatch: {paper['paper_id']}")
    lineage = LINEAGES.get(paper["paper_id"])
    if lineage:
        require(record.get("conceptdoi") == lineage.concept_doi, f"published concept lineage mismatch: {paper['paper_id']}")
    else:
        require(bool(record.get("conceptdoi")), "Lean concept DOI is missing")
    return record


def write_aggregate(state: dict) -> dict:
    rows = []
    for paper in included_papers():
        item = state["papers"][paper["paper_id"]]
        require(item.get("status") == "PUBLISHED_VERIFIED", f"publication incomplete: {paper['paper_id']}")
        rows.append({
            "paper_id": paper["paper_id"],
            "title": paper["title"],
            "version": paper["version"],
            "publication_mode": item["mode"],
            "source_doi": LINEAGES[paper["paper_id"]].source_doi if paper["paper_id"] in LINEAGES else None,
            "record_id": item["record_id"],
            "doi": item["doi"],
            "concept_doi": item["concept_doi"],
            "receipt": item["receipt"],
            "receipt_sha256": item["receipt_sha256"],
        })
    value = {
        "schema": "sft.lean4_verified_zenodo_publication_record.v1",
        "date": DATE,
        "generated_at_utc": utc_now(),
        "status": "PUBLISHED_VERIFIED",
        "existing_lineage_update_count": 17,
        "new_standalone_lean_record_count": 1,
        "excluded_no_lineage_new_record_count": 2,
        "excluded_no_lineage_papers": sorted(EXCLUDED_PAPER_IDS),
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "authorization_sha256": sha256(AUTHORIZATION),
        "authorized_candidate_manifest_sha256": state["authorized_candidate_manifest_sha256"],
        "lean_report_sha256": sha256(LEAN_REPORT),
        "records": rows,
    }
    write_json(AGGREGATE_RECORD, value)
    return value


def publish() -> dict:
    verify_local_authority()
    access_token = token()
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_STAGED", "PUBLISHING", "PUBLISHED_VERIFIED"}, "all 18 drafts must be staged before publishing")
    verify_all_staged(state, access_token)
    state["status"] = "PUBLISHING"
    save_state(state)
    for paper in included_papers():
        paper_id = paper["paper_id"]
        item = state["papers"][paper_id]
        if item.get("status") == "PUBLISHED_VERIFIED":
            public_record_verified(paper, int(item["record_id"]), state)
            print(f"PUBLISHED_REUSED paper={paper_id} doi={item['doi']}", flush=True)
            continue
        if item.get("publish_response_record_id"):
            record_id = int(item["publish_response_record_id"])
        else:
            draft_id = int(item["draft_id"])
            published = api_request("POST", f"{API}/deposit/depositions/{draft_id}/actions/publish", access_token=access_token)
            record_id = int((published or {}).get("record_id") or (published or {}).get("id") or draft_id)
            item["publish_response_record_id"] = record_id
            item["publish_requested_at_utc"] = utc_now()
            save_state(state)
        record = public_record_verified(paper, record_id, state)
        receipt = published_receipt(state, paper, record)
        receipt_path = RECEIPT_ROOT / f"{paper_id}-v{paper['version']}.json"
        write_json(receipt_path, receipt)
        item.update({
            "status": "PUBLISHED_VERIFIED",
            "record_id": record_id,
            "doi": record.get("doi"),
            "concept_doi": record.get("conceptdoi"),
            "record_url": receipt["record_url"],
            "published_at_utc": receipt["published_at_utc"],
            "receipt": receipt_path.relative_to(ROOT).as_posix(),
            "receipt_sha256": sha256(receipt_path),
        })
        save_state(state)
        print(f"PUBLISHED_VERIFIED paper={paper_id} record={record_id} doi={item['doi']} conceptdoi={item['concept_doi']}", flush=True)
    state["status"] = "PUBLISHED_VERIFIED"
    state["completed_at_utc"] = utc_now()
    save_state(state)
    aggregate = write_aggregate(state)
    print(json.dumps(aggregate, indent=2, sort_keys=True), flush=True)
    return aggregate


def verify_published() -> dict:
    state = load_state()
    require(state.get("status") == "PUBLISHED_VERIFIED", "publication state is not complete")
    rows = []
    for paper in included_papers():
        item = state["papers"][paper["paper_id"]]
        record = public_record_verified(paper, int(item["record_id"]), state)
        receipt_path = ROOT / item["receipt"]
        require(receipt_path.is_file() and sha256(receipt_path) == item["receipt_sha256"], f"receipt identity mismatch: {paper['paper_id']}")
        rows.append({"paper_id": paper["paper_id"], "record_id": record["id"], "doi": record["doi"], "concept_doi": record["conceptdoi"], "version": record["metadata"]["version"], "status": "PASS"})
    aggregate = write_aggregate(state)
    result = {"status": "PASS", "record_count": len(rows), "records": rows, "aggregate_record": AGGREGATE_RECORD.relative_to(ROOT).as_posix(), "aggregate_record_sha256": sha256(AGGREGATE_RECORD)}
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("preflight", "create-drafts", "build-packages", "stage", "publish", "verify"))
    args = parser.parse_args()
    actions = {
        "preflight": preflight,
        "create-drafts": create_drafts,
        "build-packages": build_packages,
        "stage": stage,
        "publish": publish,
        "verify": verify_published,
    }
    try:
        actions[args.action]()
    except Exception as exc:
        print(f"HALT action={args.action} error={exc}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    main()
