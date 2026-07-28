#!/usr/bin/env python3
"""Build the deterministic local Consciousness foundation archival bundle."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
RELEASE = ROOT / "output/release" / f"consciousness-cognitive-science-{VERSION}"
PDF_NAME = "00_From-Fold-to-Consciousness_Consciousness-and-Cognitive-Science-Foundation-Paper-001-v1.0.pdf"
ZIP_NAME = "01_Ernos-Labs-SFT-Consciousness-and-Cognitive-Science-Foundation-Evidence-and-Source-v1.0.0.zip"
MD_NAME = "02_From-Fold-to-Consciousness_Consciousness-and-Cognitive-Science-Foundation-Paper-001-v1.0.md"
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
        ROOT / "sft/consciousness_cognitive_science",
        ROOT / "docs/branch_roadmaps/10-consciousness-cognitive-science.md",
        ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.json",
        ROOT / "audits/consciousness_v1_v2_initial_atomic_ownership.md",
        ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.json",
        ROOT / "audits/consciousness_v1_v2_atomic_reconciliation.md",
        ROOT / "audits/consciousness_foundation_integration.json",
        ROOT / "audits/consciousness_foundation_integration.md",
        ROOT / "census/consciousness_continuation_checkpoint.json",
        ROOT / "publications/inventories/consciousness_cognitive_science.json",
        ROOT / "publication/consciousness_foundation_publication_gate_spec_v1.json",
        ROOT / "publication/consciousness_foundation_zenodo_metadata.json",
        ROOT / "publication/consciousness_foundation_github_metadata.json",
        ROOT / "publication/consciousness_foundation_github_release_notes.md",
        ROOT / "experiments/consciousness",
        ROOT / "experiments/external_sources/consciousness",
        ROOT / "experiments/sealed_predictions/consciousness_foundation_complete_pre_source.json",
        ROOT / "tests/test_consciousness_foundation.py",
    )
    tools = tuple(sorted((ROOT / "tools").glob("*consciousness*")))
    claims = tuple(sorted((ROOT / "claims").glob("SFT-CONSC-*")))
    receipts = tuple(sorted((ROOT / "receipts/engine/model_admitted").glob("SFT-CONSC-*.json")))
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
        "schema": "sft-v3-consciousness-foundation-evidence-map/1",
        "branch": "consciousness_cognitive_science",
        "version": VERSION,
        "publication_authorized": bool(
            json.loads((ROOT / "publication/consciousness_foundation_zenodo_metadata.json").read_text(encoding="utf-8"))["publication_authorized"]
        ),
        "claim_count": 72,
        "candidate_count": 18_432,
        "unique_survivor_count": 72,
        "control_count": 288,
        "prior_atom_count": 46,
        "external_source_count": 15,
        "registered_external_feature_count": 61,
        "present_external_feature_count": 58,
        "absent_external_feature_count_preserved": 3,
        "transport_or_content_failure_rows_preserved": 18,
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
        info = ZipInfo("consciousness_foundation_evidence_map.json", FIXED_TIME)
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, json.dumps(evidence_map, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return len(files) + 1


def main() -> None:
    metadata_document = json.loads(
        (ROOT / "publication/consciousness_foundation_zenodo_metadata.json").read_text(encoding="utf-8")
    )
    authorized = bool(metadata_document["publication_authorized"])
    doi = str(metadata_document.get("doi", ""))
    zenodo_record = metadata_document.get("zenodo_draft_id")
    if authorized and (not doi or not isinstance(zenodo_record, int)):
        raise RuntimeError("authorized release requires a reserved DOI and Zenodo record")
    RELEASE.mkdir(parents=True, exist_ok=True)
    for existing in RELEASE.iterdir():
        if existing.is_file():
            existing.unlink()
    shutil.copyfile(
        ROOT / "output/pdf/from-fold-to-consciousness-and-cognitive-science-foundation-paper-001-v1.0.pdf",
        RELEASE / PDF_NAME,
    )
    shutil.copyfile(
        ROOT / "publications/current/consciousness_cognitive_science/FROM_FOLD_TO_CONSCIOUSNESS.md",
        RELEASE / MD_NAME,
    )
    bundled_file_count = write_deterministic_zip(RELEASE / ZIP_NAME)
    (RELEASE / SUMS_NAME).write_text(
        "".join(f"{sha256(RELEASE / name)}  {name}\n" for name in (PDF_NAME, ZIP_NAME, MD_NAME)),
        encoding="utf-8",
    )
    manifest = {
        "schema": "sft-v3-published-branch-release/1" if authorized else "sft-v3-local-prepublication-branch-release/1",
        "branch_id": "consciousness_cognitive_science",
        "version": VERSION,
        "publication_date": "2026-07-27",
        "publication_authorized": authorized,
        "github_push_authorized": authorized,
        "zenodo_publish_authorized": authorized,
        "zenodo_record": zenodo_record,
        "doi": doi,
        "foundational_status": "current_evidence_closed_extension_open",
        "full_field_status": "planned",
        "bundled_evidence_file_count": bundled_file_count,
        "files": [
            {"name": name, "sha256": f"sha256:{sha256(RELEASE / name)}"}
            for name in (PDF_NAME, ZIP_NAME, MD_NAME, SUMS_NAME)
        ],
    }
    (ROOT / "publication/consciousness_foundation_release.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(
        f"Consciousness foundation local release: READY files=4 evidence_files={bundled_file_count} "
        f"publication_authorized={str(authorized).lower()}"
    )


if __name__ == "__main__":
    main()
