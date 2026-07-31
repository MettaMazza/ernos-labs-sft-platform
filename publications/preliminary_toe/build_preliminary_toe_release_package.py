#!/usr/bin/env python3
"""Package the verified SFT V3 preliminary ToE publication.

The builder is remote-inert: it records Maria Smith's existing authorisation
and creates the exact package for the already-reserved Zenodo draft.
"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PUBLICATION = HERE / "publication"
RELEASE = ROOT / "output/release/preliminary-toe-v3-0.1.0"

MASTER = HERE / "SMITHIAN_FOLD_THEORY_V3_PRELIMINARY_THEORY_OF_EVERYTHING.md"
MONOGRAPH_PDF = ROOT / "output/pdf/smithian-fold-theory-v3-preliminary-theory-of-everything-v0.1.0.pdf"
CLAIM_PDF = ROOT / "output/pdf/sft-v3-preliminary-toe-complete-claim-inventory-v0.1.0.pdf"
AUDIT_PDF = ROOT / "output/pdf/sft-v3-preliminary-toe-scientific-audit-layer-v0.1.0.pdf"
VERIFICATION = PUBLICATION / "PUBLICATION_VERIFICATION.json"


def digest(path: Path) -> str:
    block = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            block.update(chunk)
    return block.hexdigest()


def git_value(*arguments: str) -> str | None:
    result = subprocess.run(
        ["git", *arguments], cwd=ROOT, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def write_archive(destination: Path) -> None:
    sources = [
        ROOT / "publication guidance.md",
        MASTER,
        HERE / "appendices/COMPLETE_CLAIM_INVENTORY.md",
        HERE / "appendices/COMPLETE_CLAIM_INVENTORY.json",
        HERE / "AUTHORITATIVE_CORPUS_INVENTORY.json",
        HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.json",
        HERE / "EXHAUSTIVE_TOE_CONTENT_MATRIX.md",
        HERE / "SCIENTIFIC_AUDIT_LAYER.md",
        HERE / "build_authoritative_inventory.py",
        HERE / "build_exhaustive_toe_content_matrix.py",
        HERE / "build_exhaustive_toe_monograph.py",
        HERE / "build_full_preliminary_toe_release_candidate.py",
        HERE / "audit_full_preliminary_toe_publication_guidance.py",
        HERE / "render_scientific_audit.py",
        HERE / "build_preliminary_toe_release_package.py",
        HERE / "tests/test_full_preliminary_toe_release_candidate.py",
        ROOT / "tools/render_full_preliminary_toe.py",
        ROOT / "tools/verify_full_preliminary_toe_release.py",
        PUBLICATION / "CORPUS_FREEZE.json",
        PUBLICATION / "PUBLICATION_GUIDANCE_COMPLIANCE.json",
        PUBLICATION / "PUBLICATION_GUIDANCE_COMPLIANCE.md",
        PUBLICATION / "PDF_VISUAL_QA.json",
        PUBLICATION / "PUBLICATION_VERIFICATION.json",
        PUBLICATION / "PUBLICATION_APPROVAL_DOSSIER.md",
        ROOT / "audits/CURRENT_PROGRAMME_STATUS_2026-07-29.md",
        ROOT / "publication/FINAL_COMPLETE_FIELD_PUBLICATIONS_2026-07-29.md",
        ROOT / "publication/V3_ZENODO_CATALOGUE_AND_PRE_V3_STATUS_2026-07-28.md",
        ROOT / "publications/FINAL_TOE_PAPER_PROTOCOL.md",
        ROOT / "applications/frontier/v3_computational_proofs/protein_folding/paper/SMITHIAN_FOLD_THEORY_V3_PROTEIN_FOLD_COMPUTATIONAL_PROOF.md",
        ROOT / "applications/frontier/v3_computational_proofs/protein_folding/audits/current_scientific_gate_v20.json",
        ROOT / "applications/frontier/v3_computational_proofs/protein_folding/audits/full_test_suite_v21.json",
        ROOT / "applications/frontier/v3_computational_proofs/protein_folding/paper/COMPLETE_CLAIM_AUDIT_MANIFEST.json",
        ROOT / "applications/frontier/v3_computational_proofs/protein_folding/publication/protein_fold_preliminary_zenodo_publication_receipt_v0_9_4.json",
    ]
    sources.extend(sorted((HERE / "manuscript_parts").glob("*.md")))
    sources.extend(sorted((HERE / "volumes").glob("*.md")))
    missing = [str(path.relative_to(ROOT)) for path in sources if not path.is_file()]
    if missing:
        raise RuntimeError(f"archive inputs are missing: {missing}")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in sorted(set(sources)):
            archive.write(source, arcname=str(source.relative_to(ROOT)))


def main() -> int:
    required = (MASTER, MONOGRAPH_PDF, CLAIM_PDF, AUDIT_PDF, VERIFICATION)
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError(f"release inputs are missing: {missing}")
    verification = json.loads(VERIFICATION.read_text(encoding="utf-8"))
    if verification.get("status") != "PASS" or verification.get("failure_count"):
        raise RuntimeError("local publication verification has not passed")
    if not verification.get("remote_publication_authorised"):
        raise RuntimeError("verification does not record Maria Smith's publication authority")
    if verification.get("publication_operation") != "create_new_standalone_v3_record":
        raise RuntimeError("verification does not require a new standalone V3 record")
    if verification.get("concept_doi") is not None:
        raise RuntimeError("verification assigns a concept DOI before Zenodo publication")
    if verification.get("concept_record_id") != 21717583:
        raise RuntimeError("verification does not bind concept record 21717583")
    if verification.get("zenodo_draft_id") != 21717584:
        raise RuntimeError("verification does not bind Zenodo draft 21717584")
    if verification.get("version_doi") != "10.5281/zenodo.21717584":
        raise RuntimeError("verification does not bind reserved version DOI")

    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.mkdir(parents=True, exist_ok=True)
    destinations = {
        "01_Smithian-Fold-Theory-V3-Preliminary-Theory-of-Everything-v0.1.0.pdf": MONOGRAPH_PDF,
        "02_Smithian-Fold-Theory-V3-Preliminary-Theory-of-Everything-v0.1.0.md": MASTER,
        "03_SFT-V3-Preliminary-ToE-Complete-Claim-Inventory-v0.1.0.pdf": CLAIM_PDF,
        "04_SFT-V3-Preliminary-ToE-Scientific-Audit-Layer-v0.1.0.pdf": AUDIT_PDF,
        "05_COMPLETE_CLAIM_INVENTORY.json": HERE / "appendices/COMPLETE_CLAIM_INVENTORY.json",
        "06_PUBLICATION_APPROVAL_DOSSIER.md": PUBLICATION / "PUBLICATION_APPROVAL_DOSSIER.md",
        "07_PUBLICATION_VERIFICATION.json": VERIFICATION,
        "08_PUBLICATION_GUIDANCE_COMPLIANCE.json": PUBLICATION / "PUBLICATION_GUIDANCE_COMPLIANCE.json",
        "09_CORPUS_FREEZE.json": PUBLICATION / "CORPUS_FREEZE.json",
    }
    for filename, source in destinations.items():
        shutil.copyfile(source, RELEASE / filename)

    archive = RELEASE / "10_SFT-V3-Preliminary-ToE-Audit-and-Machine-Source-v0.1.0.zip"
    write_archive(archive)

    metadata = {
        "metadata": {
            "title": "The Smithian Fold Theory of Everything: An Exhaustive V3 Preliminary Monograph from There Is No Nothing to the Current Computational-Proof Frontier",
            "upload_type": "publication",
            "publication_type": "book",
            "creators": [
                {
                    "name": "Smith, Maria",
                    "affiliation": "Ernos Labs",
                }
            ],
            "description": (
                "Full-scale preliminary version 0.1.0 of the rebuilt Smithian Fold Theory of Everything V3, "
                "published as the first publication in a new standalone V3 Zenodo lineage. This release "
                "does not update the deprecated pre-V3 ToE concept. It presents the complete current "
                "dependency argument from the operational root through Foundation, Mathematics, "
                "Information Science, Classical and Quantum Computation, Physics, Chemistry, Materials, "
                "Biology, Medicine, Consciousness, Earth, Astronomy, Social Systems, Engineering and "
                "Cross-Branch Synthesis; reconciles the pre-V3 publication and computational history; "
                "reports 2,751 model-admitted claims, 892,246 candidates, 2,751 survivors and 11,004 "
                "passed controls; preserves adverse, corrected and unresolved evidence; and reports the "
                "current Protein, Chess, Go and Unison Fold computational-proof frontiers. The conceptual "
                "monograph is accompanied by the complete claim inventory, scientific audit layer, "
                "machine-source archive, corpus freeze and publication-guidance verification. Preliminary "
                "denotes the complete frozen present state while the remaining full-field and computational "
                "programmes remain open."
            ),
            "version": "0.1.0",
            "publication_date": "2026-07-31",
            "access_right": "open",
            "license": "cc-by-4.0",
            "keywords": [
                "Smithian Fold Theory",
                "theory of everything",
                "premise-free foundation",
                "parameter-free derivation",
                "machine-verifiable science",
                "physical constants",
                "computational proof",
                "protein folding",
                "AlphaFold",
                "open science",
            ],
            "related_identifiers": [
                {
                    "identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform",
                    "relation": "isSupplementedBy",
                    "resource_type": "software",
                    "scheme": "url",
                }
            ],
        },
        "publication_authorised": True,
        "publication_operation": "CREATE_NEW_STANDALONE_V3_RECORD",
        "existing_concept_doi": None,
        "create_new_concept": True,
        "new_concept_doi": None,
        "concept_record_id": 21717583,
        "zenodo_draft_id": 21717584,
        "historical_pre_v3_concept_doi": "10.5281/zenodo.21182468",
        "remote_publication_authorised": True,
        "version_doi": "10.5281/zenodo.21717584",
    }
    metadata_path = RELEASE / "11_ZENODO_METADATA_V0_1_0.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    readme = RELEASE / "README.txt"
    readme.write_text(
        "Smithian Fold Theory V3 preliminary ToE 0.1.0\n\n"
        "Author and publication authority: Maria Smith\n"
        "Organisation: Ernos Labs\n"
        "Publication operation: CREATE NEW STANDALONE V3 ZENODO RECORD\n"
        "Zenodo draft: 21717584\n"
        "Concept record: 21717583; concept DOI assigned when public\n"
        "Version DOI: 10.5281/zenodo.21717584\n"
        "Deprecated V2 concept DOI 10.5281/zenodo.21182468: historical only\n"
        "Remote publication status: AUTHORISED BY MARIA SMITH\n\n"
        "This is the verified publication package for Zenodo draft 21717584. It is\n"
        "published through Zenodo's new-record action, never as a version of the\n"
        "deprecated V2 ToE.\n",
        encoding="utf-8",
    )

    files_before_manifest = sorted(
        path for path in RELEASE.iterdir() if path.is_file() and path.name not in {"RELEASE_MANIFEST.json", "SHA256SUMS.txt"}
    )
    manifest = {
        "schema": "sft-v3-preliminary-toe-local-release-package/v1",
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "version": "0.1.0",
        "intended_public_version": "0.1.0",
        "existing_concept_doi": None,
        "new_concept_doi": None,
        "concept_record_id": 21717583,
        "zenodo_draft_id": 21717584,
        "historical_pre_v3_concept_doi": "10.5281/zenodo.21182468",
        "version_doi": "10.5281/zenodo.21717584",
        "publication_operation": "create_new_standalone_v3_record",
        "git_branch": git_value("branch", "--show-current"),
        "git_head": git_value("rev-parse", "HEAD"),
        "remote_publication_authorised": True,
        "protected_authority_edited": False,
        "local_verification_sha256": digest(VERIFICATION),
        "files": [
            {
                "name": path.name,
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
            for path in files_before_manifest
        ],
    }
    manifest_path = RELEASE / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    sums_sources = sorted(path for path in RELEASE.iterdir() if path.is_file() and path.name != "SHA256SUMS.txt")
    (RELEASE / "SHA256SUMS.txt").write_text(
        "".join(f"{digest(path)}  {path.name}\n" for path in sums_sources),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS_READY_FOR_AUTHORISED_PUBLICATION",
                "directory": str(RELEASE.relative_to(ROOT)),
                "files": len(list(RELEASE.iterdir())),
                "remote_publication_authorised": True,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
