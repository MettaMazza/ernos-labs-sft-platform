#!/usr/bin/env python3
"""Preserve the complete pre-readmission Chemistry authority surface."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOT = ROOT / "audits/archives/chemistry_pre_readmission_2026-07-27"
MANIFEST_PATH = ARCHIVE_ROOT / "authority_manifest.json"
ZIP_PATH = ARCHIVE_ROOT / "chemistry_pre_readmission_authority_surface.zip"
FIXED_TIME = (2026, 7, 27, 12, 0, 0)
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"
SNAPSHOT_CORRECTIONS = {
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-g02620.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-g02620.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-ht06789.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-ht06789.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-o04308.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-o04308.html",
    "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-s05735.json":
        "experiments/external_sources/chemistry/snapshots/inorg-004-017-family-v1/iupac-s05735.html",
    "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05194.json":
        "experiments/external_sources/chemistry/snapshots/org-001-016-family-v1/iupac-r05194.html",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256:" + digest.hexdigest()


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for item in sorted(path.rglob("*")):
        if item.is_file() and "__pycache__" not in item.parts and item.suffix not in {".pyc", ".pyo"}:
            yield item


def archive_sources(census_rows: list[dict]) -> tuple[Path, ...]:
    sources: list[Path] = [
        ROOT / "census/claims.json",
        ROOT / "census/execution_manifest.json",
        ROOT / "census/branches.json",
        ROOT / "sft/chemistry",
        ROOT / "experiments/chemistry",
    ]
    sources.extend(sorted((ROOT / "claims").glob("SFT-CHEM-*")))
    receipt_paths = {ROOT / row["receipt_path"] for row in census_rows}
    for category in ("model_admitted", "conditional_evidence", "rejected"):
        receipt_paths.update((ROOT / "receipts/engine" / category).glob("SFT-CHEM-*.json"))
    sources.extend(sorted(receipt_paths))
    sources.extend(sorted((ROOT / "tools").glob("*chemistry*")))
    return tuple(sources)


def main() -> None:
    census = json.loads((ROOT / "census/claims.json").read_text(encoding="utf-8"))
    execution_manifest = json.loads((ROOT / "census/execution_manifest.json").read_text(encoding="utf-8"))
    chemistry_rows = [row for row in census["claims"] if row.get("branch") == "chemistry"]
    chemistry_execution_rows = [
        row for row in execution_manifest["claims"]
        if str(row.get("claim_id", "")).startswith("SFT-CHEM-")
    ]
    if len(chemistry_rows) != 176 or len(chemistry_execution_rows) != 176:
        raise RuntimeError("expected the exact 176-row Chemistry authority surface")
    if [row["claim_id"] for row in chemistry_rows] != [row["claim_id"] for row in chemistry_execution_rows]:
        raise RuntimeError("Chemistry census and execution order differ")

    external_root = ROOT / "experiments/external_sources/chemistry"
    external_ledger = []
    for path in iter_files(external_root):
        external_ledger.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        })

    files: dict[str, Path] = {}
    for source in archive_sources(chemistry_rows):
        if not source.exists():
            raise FileNotFoundError(source)
        for path in iter_files(source):
            files[path.relative_to(ROOT).as_posix()] = path

    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    staged = subprocess.check_output(["git", "diff", "--cached", "--name-only"], cwd=ROOT, text=True).splitlines()
    manifest = {
        "schema": "sft-v3-chemistry-pre-readmission-authority-archive/1",
        "archive_date": "2026-07-27",
        "authorization": "Maria Smith explicitly authorized complete Chemistry archival, retirement and clean re-admission on 2026-07-27.",
        "repository_commit": commit,
        "engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "engine_or_protected_validator_edit_authorized": False,
        "existing_receipt_edit_or_deletion_authorized": False,
        "chemistry_claim_count": len(chemistry_rows),
        "chemistry_claim_ids_in_original_order": [row["claim_id"] for row in chemistry_rows],
        "chemistry_census_rows": chemistry_rows,
        "chemistry_execution_rows": chemistry_execution_rows,
        "receipt_hashes_in_original_order": [row["receipt_hash"] for row in chemistry_rows],
        "snapshot_type_corrections": [
            {
                "old_path": old,
                "corrected_path": new,
                "content_type": "text/html",
                "bytes": (ROOT / old).stat().st_size,
                "sha256": sha256(ROOT / old),
                "doctype_html_confirmed": "<!DOCTYPE html>" in (ROOT / old).read_text(encoding="utf-8", errors="strict")[:256],
            }
            for old, new in SNAPSHOT_CORRECTIONS.items()
        ],
        "external_source_file_count": len(external_ledger),
        "external_source_hash_ledger": external_ledger,
        "archived_file_count": len(files),
        "archived_files": [
            {"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for name, path in sorted(files.items())
        ],
        "staged_path_count_before_migration": len(staged),
        "staged_paths_before_migration": staged,
    }

    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with ZipFile(ZIP_PATH, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(files.items()):
            info = ZipInfo(name, FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
        info = ZipInfo("chemistry_pre_readmission_authority_manifest.json", FIXED_TIME)
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, manifest_bytes)
    manifest["archive_zip_path"] = ZIP_PATH.relative_to(ROOT).as_posix()
    manifest["archive_zip_bytes"] = ZIP_PATH.stat().st_size
    manifest["archive_zip_sha256"] = sha256(ZIP_PATH)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Chemistry pre-readmission archive: SEALED claims={len(chemistry_rows)} "
        f"files={len(files)} external_files={len(external_ledger)} zip={manifest['archive_zip_sha256']}"
    )


if __name__ == "__main__":
    main()
