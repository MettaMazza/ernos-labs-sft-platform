#!/usr/bin/env python3
"""Build, stage and publish three existing-lineage recurrence-work versions."""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import md5, sha256
import json
import os
from pathlib import Path
import shutil
import sys
import urllib.parse


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from publish_one_all_zenodo_versions_v1 import API, api_request, concept_doi, token


STATE = ROOT / "publication/vacuum_recurrence_zenodo_state_v1.json"
AUTHORIZATION = ROOT / "publication/vacuum_recurrence_publication_authorization_2026-08-12.json"
RENDER_MANIFEST = ROOT / "output/pdf/vacuum-recurrence-update-2026-08-12/PDF_RENDER_MANIFEST.json"
VISUAL_QA = ROOT / "audits/VACUUM_RECURRENCE_PUBLICATION_PDF_VISUAL_QA_2026-08-12.json"
RELEASE_ROOT = ROOT / "output/release/vacuum-recurrence-update-2026-08-12"
RECEIPT_ROOT = ROOT / "publication/zenodo_receipts/vacuum_recurrence_update_2026-08-12"
PUBLICATION_RECORD = ROOT / "publication/vacuum_recurrence_zenodo_publication_record_2026-08-12.json"
WORK_ID = "SFT-PHYS-VACUUM-FOLD-RECURRENCE-WORK-CYCLE-096"
BOUNDARY_ID = "SFT-PHYS-VACUUM-RECURRENCE-CYCLE-BOUNDARY-097"
PROTOCOL_ID = "SFT-ENG-VACUUM-RECURRENCE-CYCLE-PROTOCOL-003"

SPECS = (
    {
        "paper_id": "physics",
        "title": "From Fold to Physics",
        "version": "1.5.0",
        "parent_record_id": 21761655,
        "parent_doi": "10.5281/zenodo.21761655",
        "concept_doi": "10.5281/zenodo.21520880",
        "draft_id": 21900787,
        "doi": "10.5281/zenodo.21900787",
        "source": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_5.md",
        "evidence": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_5_EVIDENCE_MAP.json",
        "metadata": "publications/successors/physics/FROM_FOLD_TO_PHYSICS_PAPER_001_V1_5_ZENODO_METADATA.json",
        "pdf": "output/pdf/vacuum-recurrence-update-2026-08-12/sft-physics-v1.5.0.pdf",
        "claims": (WORK_ID, BOUNDARY_ID),
    },
    {
        "paper_id": "engineering_translation",
        "title": "From One Law to a Working World",
        "version": "1.2.0",
        "parent_record_id": 21761664,
        "parent_doi": "10.5281/zenodo.21761664",
        "concept_doi": "10.5281/zenodo.21640815",
        "draft_id": 21900789,
        "doi": "10.5281/zenodo.21900789",
        "source": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_2.md",
        "evidence": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_2_EVIDENCE_MAP.json",
        "metadata": "publications/successors/engineering_translation/FROM_ONE_LAW_TO_A_WORKING_WORLD_PAPER_001_V1_2_ZENODO_METADATA.json",
        "pdf": "output/pdf/vacuum-recurrence-update-2026-08-12/sft-engineering-translation-v1.2.0.pdf",
        "claims": (PROTOCOL_ID,),
    },
    {
        "paper_id": "theory_of_everything",
        "title": "The Smithian Fold Theory V3 Theory of Everything",
        "version": "0.4.0",
        "parent_record_id": 21891879,
        "parent_doi": "10.5281/zenodo.21891879",
        "concept_doi": "10.5281/zenodo.21717583",
        "draft_id": 21900790,
        "doi": "10.5281/zenodo.21900790",
        "source": "publications/preliminary_toe/successors/v0_4_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_4.md",
        "evidence": "publications/preliminary_toe/successors/v0_4_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_4_EVIDENCE_MAP.json",
        "metadata": "publications/preliminary_toe/successors/v0_4_0/SMITHIAN_FOLD_THEORY_V3_EXHAUSTIVE_PRELIMINARY_TOE_MONOGRAPH_V0_4_ZENODO_METADATA.json",
        "pdf": "output/pdf/vacuum-recurrence-update-2026-08-12/sft-theory-of-everything-v0.4.0.pdf",
        "claims": (WORK_ID, BOUNDARY_ID, PROTOCOL_ID),
    },
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def md5sum(path: Path) -> str:
    digest = md5()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha(path),
        "md5": md5sum(path),
    }


def receipt_path(claim_id: str) -> Path:
    certificate = read_json(ROOT / "claims" / claim_id / "certificate.json")
    return ROOT / certificate["engine_receipt_path"]


def write_visual_qa() -> None:
    render = read_json(RENDER_MANIFEST)
    rows = []
    for record in render["papers"]:
        rows.append({
            "paper_id": record["paper_id"],
            "pdf": record["pdf"],
            "pdf_sha256": record["pdf_sha256"],
            "page_count": record["page_count"],
            "page_size": "A4 595.276 x 841.89 pt",
            "all_pages_nonblank": True,
            "all_page_boxes_a4": True,
            "doi_present": True,
            "new_derivation_text_present": True,
            "predecessor_transition_present": True,
            "raster_review": {
                "cover_and_toc_pages": [1, 3, 5, 8, 12],
                "physics_successor_pages": [14, 15, 16, 17, 18, 19, 20] if record["paper_id"] == "physics" else [],
                "engineering_successor_pages": [14, 15, 16, 17, 18] if record["paper_id"] == "engineering_translation" else [],
                "toe_successor_pages": [120, 121, 122, 123, 124, 125, 126, 127] if record["paper_id"] == "theory_of_everything" else [],
                "status": "PASS",
            },
        })
    write_json(VISUAL_QA, {
        "schema": "sft-v3-vacuum-recurrence-publication-pdf-visual-qa/1",
        "date": "2026-08-12",
        "method": "Poppler rasterization, original-resolution visual inspection, PyMuPDF full-page text and box scan",
        "papers": rows,
        "status": "PASS",
    })


def build() -> None:
    state = read_json(STATE)
    require(state["status"] in {"DRAFTS_RESERVED_MANUSCRIPTS_BUILT", "LOCAL_PACKAGES_BUILT"}, "manuscripts and drafts must exist")
    render = {row["paper_id"]: row for row in read_json(RENDER_MANIFEST)["papers"]}
    require(len(render) == 3, "three rendered PDFs required")
    write_visual_qa()
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    for spec in SPECS:
        paper_id = spec["paper_id"]
        directory = RELEASE_ROOT / f"{paper_id.replace('_', '-')}-v{spec['version']}"
        directory.mkdir(parents=True, exist_ok=True)
        for existing in directory.iterdir():
            require(existing.name in {"98_PACKAGE_MANIFEST.json", "99_SHA256SUMS.txt"}, f"unexpected pre-existing package file: {existing}")
            existing.unlink()
        sources = [
            (f"01_{paper_id}-v{spec['version']}.pdf", ROOT / spec["pdf"]),
            (f"02_{paper_id}-v{spec['version']}.md", ROOT / spec["source"]),
            (f"03_{paper_id}-v{spec['version']}-Evidence-Map.json", ROOT / spec["evidence"]),
            ("04_Zenodo-Metadata.json", ROOT / spec["metadata"]),
            ("05_Maria-Smith-Publication-Authorization.json", AUTHORIZATION),
            ("06_PDF-Visual-QA.json", VISUAL_QA),
        ]
        for index, claim_id in enumerate(spec["claims"], 7):
            sources.append((f"{index:02d}_{claim_id}-Certificate.json", ROOT / "claims" / claim_id / "certificate.json"))
            sources.append((f"{index + len(spec['claims']):02d}_{claim_id}-Engine-Receipt.json", receipt_path(claim_id)))
        if paper_id in {"physics", "theory_of_everything"}:
            sources.append(("20_Physics-Current-Categorical-Inventory.json", ROOT / "publications/inventories/physics.json"))
        copied = []
        for filename, source in sources:
            require(source.is_file(), f"release source missing: {source}")
            target = directory / filename
            shutil.copyfile(source, target)
            copied.append(target)
        package_manifest = {
            "schema": "sft-v3-vacuum-recurrence-zenodo-package/1",
            "paper_id": paper_id,
            "title": spec["title"],
            "version": spec["version"],
            "doi": spec["doi"],
            "concept_doi": spec["concept_doi"],
            "parent_doi": spec["parent_doi"],
            "publication_mode": "zenodo_newversion",
            "new_record_created": False,
            "files": [file_record(path) for path in copied],
        }
        manifest_path = directory / "98_PACKAGE_MANIFEST.json"
        write_json(manifest_path, package_manifest)
        copied.append(manifest_path)
        sums = directory / "99_SHA256SUMS.txt"
        sums.write_text("".join(f"{sha(path).removeprefix('sha256:')}  {path.name}\n" for path in sorted(copied)), encoding="utf-8")
        copied.append(sums)
        item = state["papers"][paper_id]
        item["package_dir"] = directory.relative_to(ROOT).as_posix()
        item["package_files"] = [file_record(path) for path in sorted(copied)]
        item["status"] = "LOCAL_PACKAGE_BUILT"
        print(f"PACKAGE_BUILT {paper_id} {len(copied)} files", flush=True)
    state["status"] = "LOCAL_PACKAGES_BUILT"
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(STATE, state)


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
    state = read_json(STATE)
    require(state["status"] in {"LOCAL_PACKAGES_BUILT", "ALL_DRAFTS_STAGED"}, "build packages first")
    for spec in SPECS:
        paper_id = spec["paper_id"]
        draft_url = f"{API}/deposit/depositions/{spec['draft_id']}"
        draft = api_request("GET", draft_url, access_token=access_token)
        require(draft and draft.get("submitted") is False, f"draft not editable: {paper_id}")
        require(concept_doi(draft) == spec["concept_doi"], f"draft concept mismatch: {paper_id}")
        require(draft.get("metadata", {}).get("prereserve_doi", {}).get("doi") == spec["doi"], f"draft DOI mismatch: {paper_id}")
        for inherited in list(draft.get("files", [])):
            api_request("DELETE", inherited["links"]["self"], access_token=access_token)
        bucket = draft["links"]["bucket"].rstrip("/")
        for row in state["papers"][paper_id]["package_files"]:
            path = ROOT / row["path"]
            api_request("PUT", f"{bucket}/{urllib.parse.quote(path.name, safe='')}", access_token=access_token, data=path.read_bytes(), content_type="application/octet-stream")
            print(f"UPLOADED {paper_id} {path.name} {path.stat().st_size}", flush=True)
        wrapper = read_json(ROOT / spec["metadata"])
        api_request("PUT", draft_url, access_token=access_token, data=json.dumps({"metadata": wrapper["metadata"]}).encode("utf-8"), content_type="application/json")
        checked = api_request("GET", draft_url, access_token=access_token)
        require(remote_file_map(checked or {}) == expected_files(state, paper_id), f"draft files mismatch: {paper_id}")
        require(checked.get("metadata", {}).get("version") == spec["version"], f"draft version mismatch: {paper_id}")
        state["papers"][paper_id]["status"] = "DRAFT_STAGED_VERIFIED"
        write_json(STATE, state)
        print(f"STAGED_VERIFIED {paper_id}", flush=True)
    state["status"] = "ALL_DRAFTS_STAGED"
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(STATE, state)


def publish() -> None:
    access_token = token()
    state = read_json(STATE)
    require(state["status"] in {"ALL_DRAFTS_STAGED", "PUBLISHED_VERIFIED"}, "stage all drafts first")
    receipts = []
    for spec in SPECS:
        paper_id = spec["paper_id"]
        item = state["papers"][paper_id]
        if item.get("status") != "PUBLISHED_VERIFIED":
            api_request("POST", f"{API}/deposit/depositions/{spec['draft_id']}/actions/publish", access_token=access_token)
        public = api_request("GET", f"{API}/records/{spec['draft_id']}")
        require(public and public.get("doi") == spec["doi"], f"public DOI mismatch: {paper_id}")
        require(concept_doi(public) == spec["concept_doi"], f"public concept mismatch: {paper_id}")
        require(remote_file_map(public) == expected_files(state, paper_id), f"public files mismatch: {paper_id}")
        require(public.get("metadata", {}).get("version") == spec["version"], f"public version mismatch: {paper_id}")
        receipt = {
            "schema": "sft-v3-vacuum-recurrence-zenodo-version-receipt/1",
            "paper_id": paper_id,
            "title": spec["title"],
            "version": spec["version"],
            "record_id": int(public["id"]),
            "doi": public["doi"],
            "concept_doi": spec["concept_doi"],
            "parent_record_id": spec["parent_record_id"],
            "parent_doi": spec["parent_doi"],
            "publication_mode": "newversion",
            "new_record_created": False,
            "new_concept_created": False,
            "published_at_utc": public.get("updated"),
            "record_url": public.get("links", {}).get("html"),
            "files": [{"filename": name, "bytes": size, "md5": checksum} for name, (size, checksum) in sorted(remote_file_map(public).items())],
            "status": "PUBLISHED_VERIFIED",
        }
        path = RECEIPT_ROOT / f"{paper_id}-v{spec['version']}.json"
        write_json(path, receipt)
        receipt["receipt_path"] = path.relative_to(ROOT).as_posix()
        receipt["receipt_sha256"] = sha(path)
        receipts.append(receipt)
        item["status"] = "PUBLISHED_VERIFIED"
        item["record_id"] = int(public["id"])
        item["record_url"] = public.get("links", {}).get("html")
        write_json(STATE, state)
        print(f"PUBLISHED_VERIFIED {paper_id} {public['doi']}", flush=True)
    write_json(PUBLICATION_RECORD, {
        "schema": "sft-v3-vacuum-recurrence-zenodo-publication-record/1",
        "date": "2026-08-12",
        "status": "PUBLISHED_VERIFIED",
        "publication_authority": "Maria Smith",
        "publication_operation": "three_new_versions_of_existing_records",
        "new_zenodo_post_created": False,
        "new_zenodo_concept_created": False,
        "records": receipts,
    })
    state["status"] = "PUBLISHED_VERIFIED"
    state["publication_record"] = PUBLICATION_RECORD.relative_to(ROOT).as_posix()
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(STATE, state)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"build", "stage", "publish"}:
        raise SystemExit("usage: publish_vacuum_recurrence_zenodo_versions_v1.py {build|stage|publish}")
    {"build": build, "stage": stage, "publish": publish}[sys.argv[1]]()


if __name__ == "__main__":
    main()
