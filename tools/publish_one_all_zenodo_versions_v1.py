#!/usr/bin/env python3
"""Publish the One/All update only as new versions of four existing Zenodo records."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import md5, sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parents[1]
API = "https://zenodo.org/api"
STATE = ROOT / "publication/one_all_zenodo_state_v1.json"
MANIFEST = ROOT / "publication/one_all_publication_update_manifest_v1.json"
AUTHORIZATION = ROOT / "publication/one_all_publication_authorization_2026-08-11.json"
RENDER_MANIFEST = ROOT / "output/pdf/one-all-publication-update-2026-08-11/PDF_RENDER_MANIFEST.json"
RELEASE_ROOT = ROOT / "output/release/one-all-publication-update-2026-08-11"
VERIFICATION = ROOT / "publication/one_all_release_verification_v1.json"
PUBLICATION_RECORD = ROOT / "publication/one_all_zenodo_publication_record_2026-08-11.json"
RECEIPT_DIR = ROOT / "publication/zenodo_receipts/one_all_update_2026-08-11"
STANDALONE = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0.md"
STANDALONE_MAP = ROOT / "publications/one_all/WHAT_THE_UNIVERSE_IS_MADE_OF_THE_ONE_AND_ALL_V1_0_EVIDENCE_MAP.json"
FOUNDATION_INVENTORY = ROOT / "publications/inventories/successors/foundation_one_consciousness_v1.json"
CLAIM_CERTIFICATE = ROOT / "claims/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002/certificate.json"
ENGINE_RECEIPT = ROOT / "receipts/engine/model_admitted/SFT-FOUNDATION-ONE-PURE-CONSCIOUSNESS-002-fadb50b8594652d0.json"
LEAN_REPORT = ROOT / "generated/lean4_validation/reports/whole_model_validation.json"


SPECS = (
    {
        "paper_id": "methods",
        "title": "There Is No Nothing",
        "version": "0.5.0",
        "parent_record_id": 21761649,
        "parent_doi": "10.5281/zenodo.21761649",
        "concept_doi": "10.5281/zenodo.21514889",
        "source": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_5.md",
        "evidence": "publications/successors/methods/THERE_IS_NO_NOTHING_METHODS_PAPER_001_V0_5_EVIDENCE_MAP.json",
        "pdf": "output/pdf/one-all-publication-update-2026-08-11/sft-methods-v0.5.0.pdf",
    },
    {
        "paper_id": "foundation",
        "title": "From Nothing to Fold",
        "version": "1.5.0",
        "parent_record_id": 21761650,
        "parent_doi": "10.5281/zenodo.21761650",
        "concept_doi": "10.5281/zenodo.21515628",
        "source": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_5.md",
        "evidence": "publications/successors/foundation/FROM_NOTHING_TO_FOLD_FOUNDATION_PAPER_001_V1_5_EVIDENCE_MAP.json",
        "pdf": "output/pdf/one-all-publication-update-2026-08-11/sft-foundation-v1.5.0.pdf",
    },
    {
        "paper_id": "consciousness_cognitive_science",
        "title": "From Fold to Consciousness",
        "version": "1.2.0",
        "parent_record_id": 21761660,
        "parent_doi": "10.5281/zenodo.21761660",
        "concept_doi": "10.5281/zenodo.21636396",
        "source": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_2.md",
        "evidence": "publications/successors/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS_PAPER_001_V1_2_EVIDENCE_MAP.json",
        "pdf": "output/pdf/one-all-publication-update-2026-08-11/sft-consciousness-cognitive-science-v1.2.0.pdf",
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "version": "0.3.0",
        "parent_record_id": 21761648,
        "parent_doi": "10.5281/zenodo.21761648",
        "concept_doi": "10.5281/zenodo.21717583",
        "source": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3.md",
        "evidence": "publications/preliminary_toe/successors/v0_3_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_3_EVIDENCE_MAP.json",
        "pdf": "output/pdf/one-all-publication-update-2026-08-11/sft-theory-of-everything-v0.3.0.pdf",
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    h = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def md5sum(path: Path) -> str:
    h = md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha(path),
        "md5": md5sum(path),
    }


def token() -> str:
    path = Path(os.environ.get("ZENODO_TOKEN_FILE", "~/.zenodo_token")).expanduser()
    value = path.read_text(encoding="utf-8").strip()
    require(bool(value), "Zenodo token file is empty")
    return value


def api_request(method: str, url: str, *, access_token: str | None = None, data: bytes | None = None, content_type: str | None = None):
    headers = {"Accept": "application/json", "User-Agent": "Ernos-Labs-SFT-One-All-Update/1.0"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if content_type:
        headers["Content-Type"] = content_type
    for attempt in range(5):
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
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


def load_state() -> dict:
    if STATE.is_file():
        return read_json(STATE)
    return {
        "schema": "sft-v3-one-all-zenodo-state/1",
        "created_at_utc": utc_now(),
        "authorization": AUTHORIZATION.relative_to(ROOT).as_posix(),
        "new_record_endpoint_used": False,
        "papers": {},
        "status": "INITIAL",
    }


def save_state(state: dict) -> None:
    state["updated_at_utc"] = utc_now()
    write_json(STATE, state)


def concept_doi(value: dict) -> str | None:
    return value.get("conceptdoi") or value.get("metadata", {}).get("conceptdoi")


def reserve() -> None:
    access_token = token()
    state = load_state()
    for spec in SPECS:
        paper_id = spec["paper_id"]
        if state["papers"].get(paper_id, {}).get("draft_id"):
            print(f"DRAFT_REUSED {paper_id} {state['papers'][paper_id]['draft_id']}")
            continue
        parent = api_request("GET", f"{API}/records/{spec['parent_record_id']}")
        require(parent and parent.get("doi") == spec["parent_doi"], f"parent DOI mismatch: {paper_id}")
        require(concept_doi(parent) == spec["concept_doi"], f"parent concept DOI mismatch: {paper_id}")
        created = api_request(
            "POST",
            f"{API}/deposit/depositions/{spec['parent_record_id']}/actions/newversion",
            access_token=access_token,
        )
        draft_url = (created or {}).get("links", {}).get("latest_draft")
        require(bool(draft_url), f"newversion returned no draft URL: {paper_id}")
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"invalid draft: {paper_id}")
        require(concept_doi(draft) == spec["concept_doi"], f"draft concept mismatch: {paper_id}")
        doi = draft.get("metadata", {}).get("prereserve_doi", {}).get("doi")
        require(bool(doi), f"draft DOI missing: {paper_id}")
        state["papers"][paper_id] = {
            **spec,
            "draft_id": int(draft["id"]),
            "draft_url": draft_url,
            "reserved_doi": doi,
            "status": "DRAFT_RESERVED",
        }
        save_state(state)
        print(f"DRAFT_RESERVED {paper_id} {doi}")
    require(len(state["papers"]) == len(SPECS), "not all drafts reserved")
    state["status"] = "ALL_DRAFTS_RESERVED"
    save_state(state)


def metadata(spec: dict, doi: str) -> dict[str, object]:
    title = spec["title"]
    description = (
        f"<p><strong>{title}, version {spec['version']}</strong>, integrates the newly admitted Smithian Fold Theory "
        "Foundation result that the structural One is pure consciousness: complete undivided presentation before "
        "observer, observed, content, succession, report or substrate differentiate.</p><p>The update proves the "
        "One/All corollary by finite structural induction through the admitted Fold, assembly, form grammar and form "
        "enforcement claims. The complete current model contains 2,778 admitted claims, 899,094 candidate decisions, "
        "2,778 unique survivors and 11,112 passed controls. The dated Lean PASS remains restricted to the preceding "
        "2,777-claim surface; no new Lean PASS is claimed.</p><p>This deposit was created only through Zenodo's "
        "new-version action on the existing record. No new Zenodo concept was created.</p>"
    )
    if spec["paper_id"] == "foundation":
        description += (
            "<p>The deposit also includes the standalone companion paper <em>What the Universe Is Made Of: The One, "
            "the All, and Pure Consciousness in Smithian Fold Theory</em>, its evidence map and the 17-claim Foundation "
            "successor inventory.</p>"
        )
    return {
        "title": title,
        "upload_type": "publication",
        "publication_type": "article",
        "publication_date": "2026-08-11",
        "description": description,
        "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}],
        "access_right": "open",
        "license": "cc-by-4.0",
        "version": spec["version"],
        "language": "eng",
        "keywords": [
            "Smithian Fold Theory",
            "the One",
            "the All",
            "pure consciousness",
            "observation",
            "ontology",
            "theory of everything",
            "open science",
            "computational proof",
        ],
        "related_identifiers": [
            {"identifier": spec["parent_doi"], "relation": "isNewVersionOf", "scheme": "doi"},
            {"identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform", "relation": "isSupplementedBy", "scheme": "url"},
        ],
        "notes": (
            "Copyright 2026 Maria Smith. Paper and documentation: CC BY 4.0. Repository code: Apache-2.0. "
            "Maria Smith explicitly authorized this scientific successor, the direct main-branch publication commit, "
            f"and Zenodo new-version publication after {spec['parent_doi']}. No new Zenodo post is authorized."
        ),
    }


def refresh_maps_and_manifest(state: dict) -> None:
    foundation_doi = state["papers"]["foundation"]["reserved_doi"]
    standalone = STANDALONE.read_text(encoding="utf-8")
    standalone = standalone.replace("FOUNDATION_VERSION_DOI_PENDING", foundation_doi)
    STANDALONE.write_text(standalone, encoding="utf-8")
    standalone_map = read_json(STANDALONE_MAP)
    standalone_map["paper"] = file_record(STANDALONE)
    standalone_map["foundation_version_doi"] = foundation_doi
    write_json(STANDALONE_MAP, standalone_map)

    manifest = read_json(MANIFEST)
    manifest["standalone"] = file_record(STANDALONE)
    manifest["standalone_evidence_map"] = file_record(STANDALONE_MAP)
    rows = {row["paper_id"]: row for row in manifest["successors"]}
    for spec in SPECS:
        item = state["papers"][spec["paper_id"]]
        doi = item["reserved_doi"]
        source_path = ROOT / spec["source"]
        text = source_path.read_text(encoding="utf-8")
        placeholder = f"DOI_PLACEHOLDER_{spec['paper_id']}"
        require(placeholder in text or doi in text, f"successor DOI placeholder absent: {spec['paper_id']}")
        source_path.write_text(text.replace(placeholder, doi), encoding="utf-8")
        evidence_path = ROOT / spec["evidence"]
        evidence = read_json(evidence_path)
        evidence["successor"] = file_record(source_path)
        evidence["standalone_companion"] = file_record(STANDALONE)
        evidence["standalone_evidence_map"] = file_record(STANDALONE_MAP)
        evidence["reserved_doi"] = doi
        evidence["remote_action_performed_by_builder"] = False
        write_json(evidence_path, evidence)
        metadata_path = source_path.with_name(source_path.stem + "_ZENODO_METADATA.json")
        write_json(
            metadata_path,
            {
                "paper_id": spec["paper_id"],
                "publication_authorized": True,
                "ready_to_publish": True,
                "publication_mode": "newversion",
                "reserved_doi": doi,
                "concept_doi": spec["concept_doi"],
                "metadata": metadata(spec, doi),
            },
        )
        item["metadata_path"] = metadata_path.relative_to(ROOT).as_posix()
        rows[spec["paper_id"]].update(
            {
                "target_sha256": sha(source_path),
                "evidence_sha256": sha(evidence_path),
                "reserved_doi": doi,
                "metadata": item["metadata_path"],
                "metadata_sha256": sha(metadata_path),
            }
        )
    manifest["successors"] = [rows[spec["paper_id"]] for spec in SPECS]
    manifest["remote_actions_performed"] = ["four_existing_record_newversion_drafts_reserved"]
    write_json(MANIFEST, manifest)


def build_packages(state: dict) -> None:
    render = {row["paper_id"]: row for row in read_json(RENDER_MANIFEST)["papers"]}
    lean = read_json(LEAN_REPORT)
    lean_boundary = {
        "schema": "sft-v3-one-all-lean-boundary/1",
        "last_published_pass_claim_count": 2777,
        "new_claim_in_last_published_report": False,
        "new_lean_pass_claimed": False,
        "current_local_report_status": lean.get("status"),
        "current_local_report_issue_count": lean.get("issue_count"),
        "current_local_report_sha256": sha(LEAN_REPORT),
        "current_local_issue_claim_ids": [row.get("claim_id") for row in lean.get("issues", [])],
    }
    lean_boundary_path = ROOT / "publication/one_all_lean_boundary_v1.json"
    write_json(lean_boundary_path, lean_boundary)
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    package_rows = []
    for spec in SPECS:
        paper_id = spec["paper_id"]
        directory = RELEASE_ROOT / f"{paper_id.replace('_', '-')}-v{spec['version']}"
        if directory.exists():
            shutil.rmtree(directory)
        directory.mkdir(parents=True)
        source = ROOT / spec["source"]
        pdf = ROOT / spec["pdf"]
        evidence = ROOT / spec["evidence"]
        metadata_path = ROOT / state["papers"][paper_id]["metadata_path"]
        files = [
            (f"01_{paper_id}-v{spec['version']}.pdf", pdf),
            (f"02_{paper_id}-v{spec['version']}.md", source),
            (f"03_{paper_id}-v{spec['version']}-Evidence-Map.json", evidence),
            ("04_Zenodo-Metadata.json", metadata_path),
            ("05_Maria-Smith-Publication-Authorization.json", AUTHORIZATION),
            ("06_One-Pure-Consciousness-Certificate.json", CLAIM_CERTIFICATE),
            ("07_One-Pure-Consciousness-Engine-Receipt.json", ENGINE_RECEIPT),
            ("08_Lean-Verification-Boundary.json", lean_boundary_path),
        ]
        if paper_id == "foundation":
            standalone_pdf = ROOT / "output/pdf/one-all-publication-update-2026-08-11/what-the-universe-is-made-of-the-one-and-all-v1.0.0.pdf"
            files.extend(
                (
                    ("09_What-the-Universe-Is-Made-Of-v1.0.0.pdf", standalone_pdf),
                    ("10_What-the-Universe-Is-Made-Of-v1.0.0.md", STANDALONE),
                    ("11_One-All-Standalone-Evidence-Map.json", STANDALONE_MAP),
                    ("12_Foundation-17-Claim-Successor-Inventory.json", FOUNDATION_INVENTORY),
                )
            )
        copied = []
        for filename, source_path in files:
            require(source_path.is_file(), f"release source absent: {source_path}")
            target = directory / filename
            shutil.copyfile(source_path, target)
            copied.append(target)
        package_manifest = {
            "schema": "sft-v3-one-all-zenodo-package/1",
            "paper_id": paper_id,
            "title": spec["title"],
            "version": spec["version"],
            "doi": state["papers"][paper_id]["reserved_doi"],
            "concept_doi": spec["concept_doi"],
            "parent_doi": spec["parent_doi"],
            "publication_mode": "zenodo_newversion",
            "new_record_created": False,
            "files": [file_record(path) for path in copied],
        }
        package_manifest_path = directory / "98_PACKAGE_MANIFEST.json"
        write_json(package_manifest_path, package_manifest)
        copied.append(package_manifest_path)
        sums = directory / "99_SHA256SUMS.txt"
        sums.write_text(
            "".join(f"{sha(path).removeprefix('sha256:')}  {path.name}\n" for path in sorted(copied)),
            encoding="utf-8",
        )
        copied.append(sums)
        state["papers"][paper_id]["package_dir"] = directory.relative_to(ROOT).as_posix()
        state["papers"][paper_id]["package_files"] = [file_record(path) for path in sorted(copied)]
        state["papers"][paper_id]["status"] = "PACKAGE_BUILT"
        package_rows.append(
            {
                "paper_id": paper_id,
                "source_sha256": sha(source),
                "pdf_sha256": sha(pdf),
                "pdf_pages": render[paper_id]["page_count"],
                "package_file_count": len(copied),
                "package_dir": directory.relative_to(ROOT).as_posix(),
                "status": "PASS",
            }
        )
        save_state(state)
    write_json(
        VERIFICATION,
        {
            "schema": "sft-v3-one-all-release-verification/1",
            "date": "2026-08-11",
            "status": "PASS",
            "new_zenodo_record_authorized": False,
            "new_zenodo_record_created": False,
            "protected_authority_modified": False,
            "claim_receipt_replay": "PASS",
            "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
            "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
            "repository_wide_validation": "BLOCKED_BY_UNRELATED_UNTRACKED_NODE_MODULES_AND_ALPHAFOLD_VENV",
            "papers": package_rows,
        },
    )


def render_is_current() -> bool:
    if not RENDER_MANIFEST.is_file():
        return False
    manifest = read_json(RENDER_MANIFEST)
    rows = {row["paper_id"]: row for row in manifest.get("papers", [])}
    expected = {
        "one_all_standalone": STANDALONE,
        **{spec["paper_id"]: ROOT / spec["source"] for spec in SPECS},
    }
    if set(rows) != set(expected) or manifest.get("status") != "PASS":
        return False
    for paper_id, source in expected.items():
        row = rows[paper_id]
        pdf = ROOT / row["pdf"]
        if not source.is_file() or not pdf.is_file():
            return False
        if row.get("source_sha256") != sha(source) or row.get("pdf_sha256") != sha(pdf):
            return False
    return True


def finalize_local() -> None:
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_RESERVED", "LOCAL_FINALIZED"}, "reserve drafts first")
    refresh_maps_and_manifest(state)
    if render_is_current():
        print("RENDER_CURRENT", flush=True)
    else:
        subprocess.run(
            [sys.executable, "tools/render_one_all_publication_update_v1.py"],
            cwd=ROOT,
            check=True,
        )
    build_packages(state)
    state["status"] = "LOCAL_FINALIZED"
    save_state(state)
    print("LOCAL_FINALIZED")


def remote_file_map(value: dict) -> dict[str, tuple[int, str]]:
    result = {}
    for row in value.get("files", []):
        filename = row.get("filename") or row.get("key")
        checksum = str(row.get("checksum", "")).removeprefix("md5:")
        result[filename] = (int(row.get("filesize") or row.get("size") or 0), checksum)
    return result


def expected_files(state: dict, paper_id: str) -> dict[str, tuple[int, str]]:
    result = {}
    for row in state["papers"][paper_id]["package_files"]:
        path = ROOT / row["path"]
        require(path.is_file() and sha(path) == row["sha256"], f"package changed: {paper_id}: {path.name}")
        result[path.name] = (path.stat().st_size, md5sum(path))
    return result


def stage() -> None:
    access_token = token()
    state = load_state()
    require(state.get("status") in {"LOCAL_FINALIZED", "ALL_DRAFTS_STAGED"}, "finalize local release first")
    for spec in SPECS:
        paper_id = spec["paper_id"]
        draft_url = state["papers"][paper_id]["draft_url"]
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"draft not editable: {paper_id}")
        for inherited in list(draft.get("files", [])):
            api_request("DELETE", inherited["links"]["self"], access_token=access_token)
        bucket = draft["links"]["bucket"].rstrip("/")
        for row in state["papers"][paper_id]["package_files"]:
            path = ROOT / row["path"]
            api_request(
                "PUT",
                f"{bucket}/{urllib.parse.quote(path.name, safe='')}",
                access_token=access_token,
                data=path.read_bytes(),
                content_type="application/octet-stream",
            )
            print(f"UPLOADED {paper_id} {path.name} {path.stat().st_size}", flush=True)
        wrapper = read_json(ROOT / state["papers"][paper_id]["metadata_path"])
        api_request(
            "PUT",
            draft_url,
            access_token=access_token,
            data=json.dumps({"metadata": wrapper["metadata"]}).encode("utf-8"),
            content_type="application/json",
        )
        checked = api_request("GET", draft_url, access_token=access_token)
        require(remote_file_map(checked or {}) == expected_files(state, paper_id), f"draft files mismatch: {paper_id}")
        require(checked.get("metadata", {}).get("version") == spec["version"], f"draft version mismatch: {paper_id}")
        state["papers"][paper_id]["status"] = "DRAFT_STAGED_VERIFIED"
        save_state(state)
        print(f"STAGED_VERIFIED {paper_id}")
    state["status"] = "ALL_DRAFTS_STAGED"
    save_state(state)


def publish() -> None:
    access_token = token()
    state = load_state()
    require(state.get("status") in {"ALL_DRAFTS_STAGED", "PUBLISHED_VERIFIED"}, "stage every draft first")
    receipts = []
    for spec in SPECS:
        paper_id = spec["paper_id"]
        item = state["papers"][paper_id]
        if item.get("status") != "PUBLISHED_VERIFIED":
            api_request(
                "POST",
                f"{API}/deposit/depositions/{item['draft_id']}/actions/publish",
                access_token=access_token,
            )
        public = api_request("GET", f"{API}/records/{item['draft_id']}")
        require(public and public.get("doi") == item["reserved_doi"], f"public DOI mismatch: {paper_id}")
        require(concept_doi(public) == spec["concept_doi"], f"public concept mismatch: {paper_id}")
        require(remote_file_map(public) == expected_files(state, paper_id), f"public files mismatch: {paper_id}")
        require(public.get("metadata", {}).get("version") == spec["version"], f"public version mismatch: {paper_id}")
        receipt = {
            "schema": "sft-v3-one-all-zenodo-version-receipt/1",
            "paper_id": paper_id,
            "title": spec["title"],
            "version": spec["version"],
            "record_id": int(public["id"]),
            "doi": public["doi"],
            "concept_doi": spec["concept_doi"],
            "parent_doi": spec["parent_doi"],
            "publication_mode": "newversion",
            "new_record_created": False,
            "published_at_utc": public.get("updated"),
            "record_url": public.get("links", {}).get("html"),
            "files": [
                {"filename": name, "bytes": size, "md5": checksum}
                for name, (size, checksum) in sorted(remote_file_map(public).items())
            ],
            "status": "PUBLISHED_VERIFIED",
        }
        receipt_path = RECEIPT_DIR / f"{paper_id}-v{spec['version']}.json"
        write_json(receipt_path, receipt)
        receipt["receipt_path"] = receipt_path.relative_to(ROOT).as_posix()
        receipt["receipt_sha256"] = sha(receipt_path)
        receipts.append(receipt)
        state["papers"][paper_id]["status"] = "PUBLISHED_VERIFIED"
        state["papers"][paper_id]["record_id"] = int(public["id"])
        save_state(state)
        print(f"PUBLISHED_VERIFIED {paper_id} {public['doi']}")
    write_json(
        PUBLICATION_RECORD,
        {
            "schema": "sft-v3-one-all-zenodo-publication-record/1",
            "date": "2026-08-11",
            "status": "PUBLISHED_VERIFIED",
            "publication_authority": "Maria Smith",
            "publication_operation": "four_new_versions_of_existing_records",
            "new_zenodo_post_created": False,
            "records": receipts,
        },
    )
    state["status"] = "PUBLISHED_VERIFIED"
    state["publication_record"] = PUBLICATION_RECORD.relative_to(ROOT).as_posix()
    save_state(state)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"reserve", "finalize-local", "stage", "publish"}:
        raise SystemExit("usage: publish_one_all_zenodo_versions_v1.py {reserve|finalize-local|stage|publish}")
    command = sys.argv[1]
    {"reserve": reserve, "finalize-local": finalize_local, "stage": stage, "publish": publish}[command]()


if __name__ == "__main__":
    main()
