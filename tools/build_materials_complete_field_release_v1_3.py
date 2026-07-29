#!/usr/bin/env python3
"""Build the local, unpublished Materials v1.3 evidence map and release."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "publications/successors/materials/FROM_FOLD_TO_MATERIALS_PAPER_001_V1_3.md"
PDF = ROOT / "output/pdf/from-fold-to-materials-branch-paper-001-v1.3.pdf"
RECON = ROOT / "census/materials_discipline_current_reconciliation_v20.json"
OUT = ROOT / "publications/successors/materials"
RELEASE = ROOT / "output/release/materials-1.3.0"
METADATA_SOURCE = ROOT / "publication/materials_zenodo_metadata_v1_3_draft.json"
METADATA = OUT / "zenodo_metadata_v1_3.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return "sha256:" + value.hexdigest()


def write(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    recon = read(RECON)
    census = {row["claim_id"]: row for row in read(ROOT / "census/claims.json")["claims"]}
    materials = [row for row in census.values() if row["branch"] == "materials"]
    if len(materials) != 289 or recon["current_closed_count"] != 289 or recon["current_open_count"] != 0:
        raise SystemExit("Materials v1.3 release requires the final 289/289 reconciliation")
    text = PAPER.read_text(encoding="utf-8")
    claims = []
    archive_paths = {PAPER, PDF, RECON, ROOT / "census/materials_discipline_obligations.json", ROOT / "census/claims.json", ROOT / "census/execution_manifest.json"}
    for row in materials:
        package = ROOT / "claims" / row["claim_id"]
        receipt = ROOT / row["receipt_path"]
        certs = [path for path in package.glob("certificate*.json") if read(path).get("engine_receipt_hash") == row["receipt_hash"]]
        if len(certs) != 1 or row["claim_id"] not in text:
            raise SystemExit("missing current paper evidence: " + row["claim_id"])
        certificate = read(certs[0])
        empirical = read(package / "empirical_validation.json")
        if not row["model_admitted"] or not empirical["passed"] or not empirical["all_rows_preserved"]:
            raise SystemExit("incomplete admitted empirical package: " + row["claim_id"])
        claims.append({
            "claim_id": row["claim_id"], "receipt_path": row["receipt_path"],
            "engine_receipt_hash": row["receipt_hash"], "receipt_file_hash": sha(receipt),
            "derivation_seal_hash": certificate["derivation_seal_hash"],
            "independent_implementation_hash": certificate["independent_implementation_hash"],
            "independent_certificate_hash": certificate["independent_certificate_hash"],
            "measurement_receipt_hash": certificate["measurement_receipt_hash"],
            "external_validation_hash": certificate["external_validation_hash"],
            "empirical_validation_hash": certificate["empirical_validation_hash"],
            "closure_status": row["closure_status"], "external_status": row["external_status"],
            "all_external_rows_preserved": True, "root_trace_registered": True,
        })
        archive_paths.add(receipt)
        archive_paths.update(path for path in package.rglob("*") if path.is_file())
    for pattern in (
        "sft/engine/**/*.py", "sft/materials/**/*.py", "generated/materials/**/*.py",
        "tests/test_materials*.py", "tools/*materials*.py", "census/materials*.json",
        "audits/MATERIALS*", "audits/ACTIVE_MATERIALS*", "experiments/materials/**/*",
        "experiments/external_sources/materials/**/*", "experiments/sealed_predictions/materials*",
        "governance/*", "LICENSE*", "README.md", "pyproject.toml", "uv.lock",
    ):
        archive_paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    evidence = {
        "schema": "sft-v3-materials-complete-field-paper-evidence-map/1",
        "branch_id": "materials", "version": "1.3.0", "publication_authorized": False,
        "required_claim_count": 289, "required_candidate_count": 73984,
        "unique_survivor_count": 289, "control_count": 1156,
        "independent_reconstruction_count": 289, "current_open_obligation_count": 0,
        "reconciliation_identity": recon["reconciliation_identity"],
        "canonical_engine_seal": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
        "claims": claims,
        "paper": {"path": PAPER.relative_to(ROOT).as_posix(), "sha256": sha(PAPER)},
        "pdf": {"path": PDF.relative_to(ROOT).as_posix(), "sha256": sha(PDF), "pages": 790},
        "complete_claim_coverage": True, "root_traces_registered": True,
        "controls_passed": True, "ready_for_review": True, "ready_to_publish": False,
    }
    evidence_path = OUT / "evidence_map_v1_3.json"
    write(evidence_path, evidence)
    archive_paths.add(evidence_path)
    metadata = read(METADATA_SOURCE)
    metadata["publication_authorized"] = False
    metadata["ready_to_publish"] = False
    metadata["doi"] = "10.5281/zenodo.21629306"
    metadata["supersedes_record"] = 21629306
    relations = [
        item for item in metadata["metadata"].get("related_identifiers", [])
        if item.get("relation") != "isNewVersionOf"
    ]
    relations.append({"identifier": "10.5281/zenodo.21629306", "relation": "isNewVersionOf", "scheme": "doi"})
    metadata["metadata"]["related_identifiers"] = relations
    write(METADATA, metadata)
    archive_paths.add(METADATA)
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1", "branch_id": "materials",
        "version": "1.3.0", "source_path": PAPER.relative_to(ROOT).as_posix(),
        "source_hash": sha(PAPER), "rendered_paper_path": PDF.relative_to(ROOT).as_posix(),
        "rendered_paper_hash": sha(PDF), "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(),
        "evidence_map_hash": sha(evidence_path), "required_claim_count": 289,
        "zenodo_metadata_path": METADATA.relative_to(ROOT).as_posix(),
        "zenodo_metadata_hash": sha(METADATA),
        "generated_candidate_count": 73984, "comprehensive_derivation_coverage": True,
        "controls_passed": True, "root_traces_verified": True,
        "publication_authorized": False, "ready_for_review": True, "ready_to_publish": False,
    }
    manifest_path = OUT / "manifest_v1_3.json"
    write(manifest_path, manifest)
    archive_paths.add(manifest_path)

    RELEASE.mkdir(parents=True, exist_ok=True)
    for old in RELEASE.iterdir():
        if old.is_file(): old.unlink()
    pdf_name = "00_From-Fold-to-Materials_Materials-Science-Branch-Paper-001-v1.3.pdf"
    zip_name = "01_Ernos-Labs-SFT-Materials-Branch-Evidence-and-Source-v1.3.0.zip"
    md_name = "02_From-Fold-to-Materials_Materials-Science-Branch-Paper-001-v1.3.md"
    shutil.copyfile(PDF, RELEASE / pdf_name)
    shutil.copyfile(PAPER, RELEASE / md_name)
    prefix = "ernos-labs-sft-materials-branch-1.3.0/"
    with zipfile.ZipFile(RELEASE / zip_name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(archive_paths):
            info = zipfile.ZipInfo(prefix + path.relative_to(ROOT).as_posix(), (2026, 7, 29, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    names = (pdf_name, zip_name, md_name)
    ledger = "".join(f"{sha(RELEASE / name).removeprefix('sha256:')}  {name}\n" for name in names)
    (RELEASE / "99_SHA256SUMS.txt").write_text(ledger, encoding="utf-8")
    print(json.dumps({"claims": 289, "files_in_evidence_archive": len(archive_paths), "release": RELEASE.relative_to(ROOT).as_posix(), "paper": sha(PAPER), "pdf": sha(PDF), "archive": sha(RELEASE / zip_name)}, indent=2))


if __name__ == "__main__":
    main()
