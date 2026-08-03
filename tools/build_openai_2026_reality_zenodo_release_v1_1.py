#!/usr/bin/env python3
"""Build the deterministic Zenodo v1.1 release for the OpenAI reality counterpaper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"
DOI = "10.5281/zenodo.21768714"
CONCEPT_DOI = "10.5281/zenodo.21760207"
PRIOR_DOI = "10.5281/zenodo.21760208"
RELEASE_DIR = ROOT / "output/release/openai-ten-mathematical-advances-fail-reality-test-1.1.0"
PDF = ROOT / "output/pdf/openai-ten-mathematical-advances-fail-the-reality-test-sft-counterpaper-v1.1.pdf"
PAPER = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1.md"
BLOG = ROOT / "publications/essays/THE_VALUE_IN_THE_HUMAN_DESIRE_TO_KNOW_AND_THE_RESULTING_DISCOVERY.md"
EVIDENCE_MAP = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1_EVIDENCE_MAP.json"
METADATA = ROOT / "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1_ZENODO_METADATA.json"

PDF_PUBLIC = RELEASE_DIR / "00_OpenAI-Ten-Mathematical-Advances-Fail-the-Reality-Test_v1.1.0.pdf"
ZIP_PATH = RELEASE_DIR / "01_OpenAI-Ten-Mathematical-Advances-Fail-the-Reality-Test_Evidence-and-Source_v1.1.0.zip"
PAPER_PUBLIC = RELEASE_DIR / "02_OpenAI-Ten-Mathematical-Advances-Fail-the-Reality-Test_v1.1.0.md"
BLOG_PUBLIC = RELEASE_DIR / "03_The-Value-in-the-Human-Desire-to-Know_Companion-Essay_v1.1.0.md"
EVIDENCE_PUBLIC = RELEASE_DIR / "04_OpenAI-Ten-Mathematical-Advances-Fail-the-Reality-Test_Evidence-Map_v1.1.0.json"
SUMS_PATH = RELEASE_DIR / "99_SHA256SUMS.txt"
MANIFEST_PATH = RELEASE_DIR / "release_manifest.json"

PUBLIC_FILES = {
    PDF_PUBLIC.name: PDF_PUBLIC,
    ZIP_PATH.name: ZIP_PATH,
    PAPER_PUBLIC.name: PAPER_PUBLIC,
    BLOG_PUBLIC.name: BLOG_PUBLIC,
    EVIDENCE_PUBLIC.name: EVIDENCE_PUBLIC,
}

STATIC_EVIDENCE = [
    "CONSTITUTION.md",
    "LICENSE",
    "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.json",
    "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.md",
    "audits/OPENAI_2026_REALITY_COUNTERPAPER_2026-08-03_V1_1.json",
    "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.json",
    "audits/OPENAI_2026_SFT_COMPATIBILITY_CORRECTED_2026-08-02_V2.md",
    "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.json",
    "audits/OPENAI_2026_SFT_SOURCE_VALIDITY_COMPLETENESS_2026-08-02_V2.md",
    "census/openai_ten_advances_2026_sft_obligation_registry_v1.json",
    "census/openai_ten_advances_2026_sft_source_validity_registry_v2.json",
    "experiments/external_sources/mathematics/openai_ten_advances_mathematics_2026-08-01_v1/source_custody_manifest.json",
    "generated/lean4_validation/lakefile.toml",
    "generated/lean4_validation/lean-toolchain",
    "generated/lean4_validation/SFTValidation/OpenAI2026/Correspondence.lean",
    "generated/lean4_validation/SFTValidation/OpenAI2026/Obligations.lean",
    "generated/lean4_validation/SFTValidation/OpenAI2026/SourceValidity.lean",
    "generated/lean4_validation/reports/openai_2026_obligations_lean4.json",
    "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json",
    "generated/lean4_validation/reports/whole_model_validation.json",
    "generated/openai_2026_source_validity_validator_v2.py",
    "publications/counterpapers/openai_2026/CITATION.cff",
    "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1.md",
    "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1_EVIDENCE_MAP.json",
    "publications/counterpapers/openai_2026/OPENAI_TEN_MATHEMATICAL_ADVANCES_FAIL_THE_REALITY_TEST_V1_1_ZENODO_METADATA.json",
    "publications/counterpapers/openai_2026/README.md",
    "publications/essays/THE_VALUE_IN_THE_HUMAN_DESIRE_TO_KNOW_AND_THE_RESULTING_DISCOVERY.md",
    "sft/openai_2026/__init__.py",
    "sft/openai_2026/derivation_v1.py",
    "sft/openai_2026/execution_v1.py",
    "sft/openai_2026/obligations_v1.py",
    "sft/openai_2026/source_validity_execution_v2.py",
    "sft/openai_2026/source_validity_v2.py",
    "tools/admit_openai_2026_source_validity_disproofs_v2.py",
    "tools/admit_openai_ten_advances_sft_obligations_v1.py",
    "tools/audit_openai_2026_blog_counterposition_v1.py",
    "tools/audit_openai_2026_reality_counterpaper_v1_1.py",
    "tools/audit_openai_2026_source_validity_completeness_v2.py",
    "tools/bind_openai_2026_certificate_source_manifests_v1.py",
    "tools/build_openai_2026_corrected_compatibility_v2.py",
    "tools/build_openai_2026_reality_counterpaper_v1_1.py",
    "tools/build_openai_2026_reality_zenodo_release_v1_1.py",
    "tools/build_openai_2026_lean4_report_v1.py",
    "tools/build_openai_2026_source_validity_lean4_report_v2.py",
    "tools/materialize_openai_2026_source_validity_derivations_v2.py",
    "tools/materialize_openai_ten_advances_sft_derivations_v1.py",
    "tools/normalize_openai_2026_boundary_views_v1.py",
    "tools/register_openai_2026_source_validity_obligations_v2.py",
    "tools/register_openai_ten_advances_sft_obligations_v1.py",
    "tools/render_openai_2026_reality_counterpaper_v1_1.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def evidence_paths() -> list[Path]:
    evidence = json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))
    paths = {ROOT / item for item in STATIC_EVIDENCE}
    bound_rows = list(evidence["governing_artifacts"])
    for claim in evidence["claims"]:
        bound_rows.extend(claim["artifacts"])
    for row in bound_rows:
        path = ROOT / row["path"]
        require(path.is_file(), f"missing release evidence: {path}")
        require("sha256:" + sha256(path) == row["sha256"], f"evidence identity changed: {row['path']}")
        paths.add(path)
    missing = sorted(path for path in paths if not path.is_file())
    require(not missing, "missing static release evidence: " + ", ".join(str(path) for path in missing))
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def build_zip(paths: list[Path]) -> dict[str, object]:
    entries = [
        {
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for path in paths
    ]
    embedded_manifest = {
        "schema": "sft-openai-2026-reality-zenodo-evidence-manifest/1",
        "title": "OpenAI's Ten Mathematical Advances Fail the Reality Test",
        "version": VERSION,
        "doi": DOI,
        "concept_doi": CONCEPT_DOI,
        "supersedes_doi": PRIOR_DOI,
        "publication_date": "2026-08-03",
        "file_count": len(entries),
        "files": entries,
    }
    manifest_bytes = (json.dumps(embedded_manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 8, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        info = zipfile.ZipInfo("ZENODO_EVIDENCE_MANIFEST.json", date_time=(2026, 8, 3, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, manifest_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return embedded_manifest


def main() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    for required in (PDF, PAPER, BLOG, EVIDENCE_MAP, METADATA):
        require(required.is_file(), f"missing release input: {required}")
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    require(metadata["doi"] == DOI, "metadata DOI mismatch")
    require(metadata["metadata"]["version"] == VERSION, "metadata version mismatch")
    require(metadata["publication_authorized"] is True, "publication authorization missing")
    require(metadata["ready_to_publish"] is True, "publication readiness missing")

    PDF_PUBLIC.write_bytes(PDF.read_bytes())
    PAPER_PUBLIC.write_bytes(PAPER.read_bytes())
    BLOG_PUBLIC.write_bytes(BLOG.read_bytes())
    EVIDENCE_PUBLIC.write_bytes(EVIDENCE_MAP.read_bytes())
    embedded_manifest = build_zip(evidence_paths())
    sums = "".join(f"{sha256(path)}  {name}\n" for name, path in PUBLIC_FILES.items())
    SUMS_PATH.write_text(sums, encoding="utf-8")
    public_rows = [
        {
            "filename": name,
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
        }
        for name, path in PUBLIC_FILES.items()
    ]
    public_rows.append(
        {
            "filename": SUMS_PATH.name,
            "path": SUMS_PATH.relative_to(ROOT).as_posix(),
            "bytes": SUMS_PATH.stat().st_size,
            "sha256": sha256(SUMS_PATH),
        }
    )
    release_manifest = {
        "schema": "sft-openai-2026-reality-zenodo-release/1",
        "status": "READY",
        "title": "OpenAI's Ten Mathematical Advances Fail the Reality Test",
        "subtitle": "Twelve closed SFT disproofs, twelve first-principles replacements, and the cumulative cross-domain evidence that decides between them",
        "version": VERSION,
        "doi": DOI,
        "concept_doi": CONCEPT_DOI,
        "supersedes_doi": PRIOR_DOI,
        "zenodo_draft_id": 21768714,
        "publication_date": "2026-08-03",
        "closed_result": {
            "advertised_claims_rejected": 10,
            "source_validity_disproved": 12,
            "sft_replacements_proved_distinct": 12,
            "native_to_source_transfers": 0,
            "open": 0,
        },
        "evidence_archive_file_count": embedded_manifest["file_count"],
        "files": public_rows,
    }
    MANIFEST_PATH.write_text(json.dumps(release_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "READY",
        "doi": DOI,
        "evidence_files": embedded_manifest["file_count"],
        "public_files": len(public_rows),
        "release_manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
