#!/usr/bin/env python3
"""Build the local, publication-unauthorized Biology foundation release bundle."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
RELEASE = ROOT / "output" / "release" / f"biology-{VERSION}"
PDF_NAME = "00_From-Fold-to-Life_Biology-and-Life-Sciences-Foundation-Paper-001-v1.0.pdf"
ZIP_NAME = "01_Ernos-Labs-SFT-Biology-Foundation-Evidence-and-Source-v1.0.0.zip"
MD_NAME = "02_From-Fold-to-Life_Biology-and-Life-Sciences-Foundation-Paper-001-v1.0.md"
SUMS_NAME = "99_SHA256SUMS.txt"
FIXED_TIME = (2026, 7, 27, 12, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_paths() -> tuple[Path, ...]:
    explicit = (
        ROOT / "sft" / "biology",
        ROOT / "docs" / "branch_roadmaps" / "08-biology.md",
        ROOT / "audits" / "biology_v1_v2_atomic_ownership.json",
        ROOT / "audits" / "biology_v1_v2_atomic_ownership.md",
        ROOT / "census" / "biology_continuation_checkpoint.json",
        ROOT / "census" / "biology_prior_obligations.json",
        ROOT / "publications" / "inventories" / "biology.json",
        ROOT / "publication" / "biology_foundation_zenodo_metadata.json",
        ROOT / "experiments" / "biology",
        ROOT / "experiments" / "external_sources" / "biology",
        ROOT / "experiments" / "sealed_predictions" / "biology_foundation_complete_pre_source.json",
        ROOT / "experiments" / "registrations" / "biology_foundation_authority_source_selection.json",
        ROOT / "experiments" / "registrations" / "biology_foundation_authority_source_transport_addendum_v1.json",
        ROOT / "experiments" / "registrations" / "biology_foundation_family_source_selection_v1.json",
        ROOT / "experiments" / "registrations" / "biology_foundation_pmc_content_transport_addendum_v1.json",
        ROOT / "tests" / "test_biology_foundation.py",
    )
    tools = tuple(sorted((ROOT / "tools").glob("*biology*")))
    claims = tuple(sorted((ROOT / "claims").glob("SFT-BIO-*")))
    receipts = tuple(sorted((ROOT / "receipts" / "engine" / "model_admitted").glob("SFT-BIO-*.json")))
    return explicit + tools + claims + receipts


def iter_files(path: Path):
    if path.is_file():
        yield path
        return
    for item in sorted(path.rglob("*")):
        if item.is_file() and "__pycache__" not in item.parts and item.suffix != ".pyc":
            yield item


def write_deterministic_zip(target: Path) -> int:
    files: dict[str, Path] = {}
    for source in evidence_paths():
        if not source.exists():
            raise FileNotFoundError(source)
        for path in iter_files(source):
            files[path.relative_to(ROOT).as_posix()] = path
    evidence_map = {
        "schema": "sft-v3-biology-foundation-evidence-map/1",
        "branch": "biology",
        "version": VERSION,
        "publication_authorized": False,
        "claim_count": 75,
        "candidate_count": 19_200,
        "control_count": 300,
        "prior_atom_count": 30,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "files": [
            {"path": name, "sha256": f"sha256:{sha256(path)}"}
            for name, path in sorted(files.items())
        ],
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(files.items()):
            info = ZipInfo(name, FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
        info = ZipInfo("biology_foundation_evidence_map.json", FIXED_TIME)
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, json.dumps(evidence_map, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return len(files) + 1


def main() -> None:
    RELEASE.mkdir(parents=True, exist_ok=True)
    pdf = RELEASE / PDF_NAME
    md = RELEASE / MD_NAME
    bundle = RELEASE / ZIP_NAME
    shutil.copyfile(ROOT / "output" / "pdf" / "from-fold-to-life-biology-foundation-paper-001-v1.0.pdf", pdf)
    shutil.copyfile(ROOT / "publications" / "current" / "biology" / "FROM_FOLD_TO_LIFE.md", md)
    bundled_file_count = write_deterministic_zip(bundle)
    sums = RELEASE / SUMS_NAME
    sums.write_text(
        "".join(f"{sha256(RELEASE / name)}  {name}\n" for name in (PDF_NAME, ZIP_NAME, MD_NAME)),
        encoding="utf-8",
    )
    manifest = {
        "schema": "sft-v3-local-prepublication-branch-release/1",
        "branch_id": "biology",
        "version": VERSION,
        "publication_date": "2026-07-27",
        "publication_authorized": False,
        "github_push_authorized": False,
        "zenodo_publish_authorized": False,
        "foundational_status": "current_evidence_closed_extension_open",
        "full_field_status": "planned",
        "bundled_evidence_file_count": bundled_file_count,
        "files": [
            {"name": name, "sha256": f"sha256:{sha256(RELEASE / name)}"}
            for name in (PDF_NAME, ZIP_NAME, MD_NAME, SUMS_NAME)
        ],
    }
    (ROOT / "publication" / "biology_foundation_release.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Biology foundation local release: READY files=4 evidence_files={bundled_file_count} "
        f"publication_authorized=false"
    )


if __name__ == "__main__":
    main()
