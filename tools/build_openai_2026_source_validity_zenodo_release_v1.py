#!/usr/bin/env python3
"""Build the deterministic Zenodo evidence release for the OpenAI 2026 counterpaper."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.0.0"
DOI = "10.5281/zenodo.21760208"
RELEASE_DIR = ROOT / "output/release/formal-verification-is-not-foundational-derivation-1.0.0"
PDF = ROOT / "output/pdf/formal-verification-is-not-foundational-derivation-sft-counterpaper-v1.0.pdf"
PAPER = ROOT / "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0.md"
BLOG = ROOT / "publications/essays/THE_VALUE_IN_THE_HUMAN_DESIRE_TO_KNOW_AND_THE_RESULTING_DISCOVERY.md"
EVIDENCE_MAP = ROOT / "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0_EVIDENCE_MAP.json"
ZIP_PATH = RELEASE_DIR / "01_Formal-Verification-Is-Not-Foundational-Derivation_Evidence-and-Source-v1.0.0.zip"
SUMS_PATH = RELEASE_DIR / "99_SHA256SUMS.txt"
MANIFEST_PATH = RELEASE_DIR / "release_manifest.json"

PDF_PUBLIC = RELEASE_DIR / "00_Formal-Verification-Is-Not-Foundational-Derivation_v1.0.0.pdf"
PAPER_PUBLIC = RELEASE_DIR / "02_Formal-Verification-Is-Not-Foundational-Derivation_v1.0.0.md"
BLOG_PUBLIC = RELEASE_DIR / "03_The-Value-in-the-Human-Desire-to-Know_Companion-Essay_v1.0.0.md"

PUBLIC_FILES = {
    PDF_PUBLIC.name: PDF_PUBLIC,
    ZIP_PATH.name: ZIP_PATH,
    PAPER_PUBLIC.name: PAPER_PUBLIC,
    BLOG_PUBLIC.name: BLOG_PUBLIC,
}

STATIC_EVIDENCE = [
    "CONSTITUTION.md",
    "LICENSE",
    "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.json",
    "audits/OPENAI_2026_BLOG_COUNTERPOSITION_COMPLETENESS_2026-08-02_V1.md",
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
    "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0_EVIDENCE_MAP.json",
    "publications/counterpapers/openai_2026/FORMAL_VERIFICATION_IS_NOT_FOUNDATIONAL_DERIVATION_V1_0_ZENODO_METADATA.json",
    "publications/counterpapers/openai_2026/README.md",
    "sft/openai_2026/__init__.py",
    "sft/openai_2026/derivation_v1.py",
    "sft/openai_2026/execution_v1.py",
    "sft/openai_2026/obligations_v1.py",
    "sft/openai_2026/source_validity_execution_v2.py",
    "sft/openai_2026/source_validity_v2.py",
    "tools/admit_openai_2026_source_validity_disproofs_v2.py",
    "tools/admit_openai_ten_advances_sft_obligations_v1.py",
    "tools/audit_openai_2026_blog_counterposition_v1.py",
    "tools/audit_openai_2026_source_validity_completeness_v2.py",
    "tools/bind_openai_2026_certificate_source_manifests_v1.py",
    "tools/build_openai_2026_corrected_compatibility_v2.py",
    "tools/build_openai_2026_lean4_report_v1.py",
    "tools/build_openai_2026_source_validity_counterpaper_v1.py",
    "tools/build_openai_2026_source_validity_lean4_report_v2.py",
    "tools/materialize_openai_2026_source_validity_derivations_v2.py",
    "tools/materialize_openai_ten_advances_sft_derivations_v1.py",
    "tools/normalize_openai_2026_boundary_views_v1.py",
    "tools/register_openai_2026_source_validity_obligations_v2.py",
    "tools/register_openai_ten_advances_sft_obligations_v1.py",
    "tools/render_openai_2026_source_validity_counterpaper_v1.py",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def evidence_paths() -> list[Path]:
    evidence = json.loads(EVIDENCE_MAP.read_text(encoding="utf-8"))
    paths = {ROOT / item for item in STATIC_EVIDENCE}
    paths.update(ROOT / item["path"] for item in evidence["governing_artifacts"])
    for claim in evidence["claims"]:
        paths.update(ROOT / item["path"] for item in claim["artifacts"])
        for claim_id in (claim["claim_id"], claim["native_reconstruction_claim_id"]):
            package = ROOT / "claims" / claim_id
            paths.update(path for path in package.rglob("*") if path.is_file())
    missing = sorted(path for path in paths if not path.is_file())
    if missing:
        raise RuntimeError("missing release evidence: " + ", ".join(str(path) for path in missing))
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
        "schema": "sft-openai-2026-zenodo-evidence-manifest/1",
        "title": "Formal Verification Is Not Foundational Derivation",
        "version": VERSION,
        "doi": DOI,
        "publication_date": "2026-08-02",
        "file_count": len(entries),
        "files": entries,
    }
    manifest_bytes = (json.dumps(embedded_manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in paths:
            info = zipfile.ZipInfo(path.relative_to(ROOT).as_posix(), date_time=(2026, 8, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
        info = zipfile.ZipInfo("ZENODO_EVIDENCE_MANIFEST.json", date_time=(2026, 8, 2, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, manifest_bytes, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return embedded_manifest


def main() -> None:
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)
    for required in (PDF, PAPER, BLOG, EVIDENCE_MAP):
        if not required.is_file():
            raise RuntimeError(f"missing release input: {required}")
    PDF_PUBLIC.write_bytes(PDF.read_bytes())
    PAPER_PUBLIC.write_bytes(PAPER.read_bytes())
    BLOG_PUBLIC.write_bytes(BLOG.read_bytes())
    embedded_manifest = build_zip(evidence_paths())
    sums = "".join(f"{sha256(path)}  {name}\n" for name, path in PUBLIC_FILES.items())
    SUMS_PATH.write_text(sums, encoding="utf-8")
    public_rows = [
        {"filename": name, "path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
        for name, path in PUBLIC_FILES.items()
    ]
    public_rows.append(
        {"filename": SUMS_PATH.name, "path": SUMS_PATH.relative_to(ROOT).as_posix(), "bytes": SUMS_PATH.stat().st_size, "sha256": sha256(SUMS_PATH)}
    )
    release_manifest = {
        "schema": "sft-openai-2026-zenodo-release/1",
        "status": "READY",
        "title": "Formal Verification Is Not Foundational Derivation",
        "subtitle": "Twelve Closed SFT Source-Validity Disproofs of OpenAI's 2026 Mathematical Artifacts",
        "version": VERSION,
        "doi": DOI,
        "zenodo_record_id": 21760208,
        "publication_date": "2026-08-02",
        "closed_result": {"source_validity_disproved": 12, "native_reconstructions_proved_distinct": 12, "native_to_source_transfers": 0, "open": 0},
        "evidence_archive_file_count": embedded_manifest["file_count"],
        "files": public_rows,
    }
    MANIFEST_PATH.write_text(json.dumps(release_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "READY", "doi": DOI, "evidence_files": embedded_manifest["file_count"], "public_files": len(public_rows), "release_manifest": str(MANIFEST_PATH.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
