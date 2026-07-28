#!/usr/bin/env python3
"""Build the deterministic local Earth foundation archival bundle."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
RELEASE = ROOT / "output/release" / f"earth-environment-{VERSION}"
PDF_NAME = "00_From-One-World-to-Earth_Earth-and-Environmental-Sciences-Foundation-Paper-001-v1.0.pdf"
ZIP_NAME = "01_Ernos-Labs-SFT-Earth-and-Environmental-Sciences-Foundation-Evidence-and-Source-v1.0.0.zip"
MD_NAME = "02_From-One-World-to-Earth_Earth-and-Environmental-Sciences-Foundation-Paper-001-v1.0.md"
SUMS_NAME = "99_SHA256SUMS.txt"
FIXED_TIME = (2026, 7, 28, 12, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_paths() -> tuple[Path, ...]:
    explicit = (
        ROOT / "sft/earth_environment",
        ROOT / "docs/branch_roadmaps/11-earth-environment.md",
        ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.json",
        ROOT / "audits/earth_environment_v1_v2_initial_atomic_ownership.md",
        ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.json",
        ROOT / "audits/earth_environment_v1_v2_atomic_reconciliation.md",
        ROOT / "audits/earth_environment_foundation_integration.json",
        ROOT / "audits/earth_environment_foundation_integration.md",
        ROOT / "census/earth_environment_continuation_checkpoint.json",
        ROOT / "publications/inventories/earth_environment.json",
        ROOT / "publication/earth_environment_foundation_publication_gate_spec_v1.json",
        ROOT / "publication/earth_environment_foundation_zenodo_metadata.json",
        ROOT / "publication/earth_environment_foundation_github_metadata.json",
        ROOT / "publication/earth_environment_foundation_github_release_notes.md",
        ROOT / "experiments/earth_environment",
        ROOT / "experiments/external_sources/earth_environment",
        ROOT / "experiments/sealed_predictions/earth_environment_foundation_complete_pre_source.json",
        ROOT / "tests/test_earth_environment_foundation.py",
    )
    tools = tuple(sorted((ROOT / "tools").glob("*earth*")))
    claims = tuple(sorted((ROOT / "claims").glob("SFT-EARTH-*")))
    receipts = tuple(sorted((ROOT / "receipts/engine/model_admitted").glob("SFT-EARTH-*.json")))
    rejected = tuple(sorted((ROOT / "receipts/engine/rejected").glob("SFT-EARTH-*.json")))
    return explicit + tools + claims + receipts + rejected


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
        "schema": "sft-v3-earth-environment-foundation-evidence-map/1",
        "branch": "earth_environment",
        "version": VERSION,
        "publication_authorized": False,
        "claim_count": 74,
        "candidate_count": 18_944,
        "unique_survivor_count": 74,
        "control_count": 296,
        "prior_atom_count": 3,
        "external_source_count": 21,
        "registered_external_feature_count": 91,
        "present_external_feature_count": 67,
        "absent_external_feature_count_preserved": 24,
        "failed_transport_count_preserved": 1,
        "mixed_earthquake_result_adverse_preserved": True,
        "homogeneous_earthquake_holdout_compatible": True,
        "engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "files": [{"path": name, "sha256": f"sha256:{sha256(path)}"} for name, path in sorted(files.items())],
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(files.items()):
            info = ZipInfo(name, FIXED_TIME)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
        info = ZipInfo("earth_environment_foundation_evidence_map.json", FIXED_TIME)
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, json.dumps(evidence_map, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return len(files) + 1


def main() -> None:
    metadata = json.loads((ROOT / "publication/earth_environment_foundation_zenodo_metadata.json").read_text(encoding="utf-8"))
    if metadata["publication_authorized"] or metadata["zenodo_draft_id"] is not None or metadata["doi"]:
        raise RuntimeError("local Earth release must remain unauthorized")
    checkpoint_path = ROOT / "census/earth_environment_continuation_checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    checkpoint.update({
        "status": "foundational_branch_current_evidence_closed_extension_open_local_release_ready",
        "paper_path": "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md",
        "pdf_path": "output/pdf/from-one-world-to-earth-environment-foundation-paper-001-v1.0.pdf",
        "local_release_path": "output/release/earth-environment-1.0.0",
        "publication_authorized": False,
        "remote_publication_authorized": False,
        "next_exact_operation": "stage_earth_branch_artifacts_then_continue_next_foundation_branch_without_remote_action",
    })
    checkpoint_path.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    branches_path = ROOT / "census/branches.json"
    branches = json.loads(branches_path.read_text(encoding="utf-8"))
    for row in branches["branches"]:
        if row.get("branch_id") == "earth_environment":
            row["inventory_status"] = "foundation_current_evidence_closed_extension_open_74_of_74"
            row["paper_status"] = "local_release_ready_unpublished"
    branches_path.write_text(json.dumps(branches, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RELEASE.mkdir(parents=True, exist_ok=True)
    for existing in RELEASE.iterdir():
        if existing.is_file():
            existing.unlink()
    shutil.copyfile(ROOT / "output/pdf/from-one-world-to-earth-environment-foundation-paper-001-v1.0.pdf", RELEASE / PDF_NAME)
    shutil.copyfile(ROOT / "publications/current/earth_environment/FROM_ONE_WORLD_TO_EARTH.md", RELEASE / MD_NAME)
    bundled = write_deterministic_zip(RELEASE / ZIP_NAME)
    (RELEASE / SUMS_NAME).write_text("".join(f"{sha256(RELEASE / name)}  {name}\n" for name in (PDF_NAME, ZIP_NAME, MD_NAME)), encoding="utf-8")
    manifest = {
        "schema": "sft-v3-local-prepublication-branch-release/1",
        "branch_id": "earth_environment",
        "version": VERSION,
        "publication_date": "2026-07-28",
        "publication_authorized": False,
        "github_push_authorized": False,
        "zenodo_publish_authorized": False,
        "zenodo_record": None,
        "doi": "",
        "foundational_status": "current_evidence_closed_extension_open",
        "full_field_status": "planned",
        "bundled_evidence_file_count": bundled,
        "files": [{"name": name, "sha256": f"sha256:{sha256(RELEASE / name)}"} for name in (PDF_NAME, ZIP_NAME, MD_NAME, SUMS_NAME)],
    }
    (ROOT / "publication/earth_environment_foundation_release.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Earth foundation local release: READY files=4 evidence_files={bundled} publication_authorized=false")


if __name__ == "__main__":
    main()
