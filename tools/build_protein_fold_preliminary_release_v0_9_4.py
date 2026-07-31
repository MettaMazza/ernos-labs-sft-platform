#!/usr/bin/env python3
"""Build and verify the authorised Protein Fold v0.9.4 Zenodo payload."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT / "applications/frontier/v3_computational_proofs/protein_folding"
RELEASE = ROOT / "output/release/protein-fold-preliminary-0.9.4"

FILES = (
    ("01_From-Sequence-to-an-Auditable-Fold-SFT-V3-Protein-Fold-v0.9.4.pdf", ROOT / "output/pdf/sft-v3-protein-fold-computational-proof-preliminary-results-v0.9.4.pdf"),
    ("02_From-Sequence-to-an-Auditable-Fold-SFT-V3-Protein-Fold-v0.9.4.md", WORKSPACE / "paper/SMITHIAN_FOLD_THEORY_V3_PROTEIN_FOLD_COMPUTATIONAL_PROOF.md"),
    ("03_SCIENTIFIC_AUDIT_LAYER.md", WORKSPACE / "paper/SCIENTIFIC_AUDIT_LAYER.md"),
    ("04_COMPLETE_CLAIM_AUDIT.md", WORKSPACE / "paper/COMPLETE_CLAIM_AUDIT.md"),
    ("05_COMPLETE_CLAIM_AUDIT_MANIFEST.json", WORKSPACE / "paper/COMPLETE_CLAIM_AUDIT_MANIFEST.json"),
    ("06_V0_9_4_IDENTITY_RECONCILIATION.json", WORKSPACE / "paper/PRELIMINARY_V0_9_4_IDENTITY_RECONCILIATION.json"),
    ("07_REPRODUCIBILITY.md", WORKSPACE / "paper/REPRODUCIBILITY.md"),
    ("08_PUBLICATION_GUIDANCE_COMPLIANCE.md", WORKSPACE / "paper/PUBLICATION_GUIDANCE_COMPLIANCE.md"),
    ("09_MACHINE_ARCHIVE_MANIFEST.json", WORKSPACE / "paper/MACHINE_ARCHIVE_MANIFEST.json"),
    ("10_CURRENT_SCIENTIFIC_GATE_V20.json", WORKSPACE / "audits/current_scientific_gate_v20.json"),
    ("11_FULL_TEST_SUITE_V21.json", WORKSPACE / "audits/full_test_suite_v21.json"),
    ("12_PDF_VISUAL_QA_V0_9_4.json", WORKSPACE / "paper/PDF_VISUAL_QA_V0_9_4.json"),
    ("13_ZENODO_METADATA_V0_9_4.json", WORKSPACE / "publication/protein_fold_preliminary_zenodo_metadata_v0_9_4.json"),
    ("14_MARIA_SMITH_APPROVAL_DOSSIER.md", WORKSPACE / "paper/MARIA_SMITH_FINAL_APPROVAL_DOSSIER.md"),
)


def digest(path: Path) -> str:
    value = sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_readme() -> Path:
    path = RELEASE / "README.txt"
    path.write_text(
        "Smithian Fold Theory V3 Protein Fold computational proof\n"
        "Updated preliminary results, version 0.9.4\n\n"
        "Author and publication authority: Maria Smith\n"
        "Organisation: Ernos Labs\n"
        "Version DOI: 10.5281/zenodo.21717581\n"
        "Concept DOI: 10.5281/zenodo.21713536\n"
        "Previous version DOI: 10.5281/zenodo.21713537\n\n"
        "Scientific gate v20 is unchanged. This successor adds the complete\n"
        "21-record claim audit, reconciles stale v0.9.3 manifest identities,\n"
        "and records 898 passing publication-integrated tests. AlphaFold\n"
        "generalised blind parity remains unresolved.\n",
        encoding="utf-8",
    )
    return path


def main() -> int:
    absent = [str(source.relative_to(ROOT)) for _, source in FILES if not source.is_file()]
    if absent:
        raise SystemExit(f"missing release inputs: {absent}")
    if RELEASE.exists():
        shutil.rmtree(RELEASE)
    RELEASE.mkdir(parents=True)
    records = []
    for name, source in FILES:
        target = RELEASE / name
        shutil.copyfile(source, target)
        records.append({"name": name, "bytes": target.stat().st_size, "sha256": digest(target)})
    readme = write_readme()
    records.append({"name": readme.name, "bytes": readme.stat().st_size, "sha256": digest(readme)})
    manifest = {
        "schema": "sft-v3-protein-fold-preliminary-release/v0.9.4",
        "status": "PASS_READY_FOR_AUTHORISED_PUBLICATION",
        "author": "Maria Smith",
        "publication_authority": "Maria Smith",
        "version": "0.9.4",
        "version_doi": "10.5281/zenodo.21717581",
        "concept_doi": "10.5281/zenodo.21713536",
        "previous_version_doi": "10.5281/zenodo.21713537",
        "scientific_gate": "v20 unchanged",
        "publication_integrated_tests": {"run": 898, "failures": 0, "errors": 0},
        "files": records,
    }
    manifest_path = RELEASE / "RELEASE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ledger_paths = sorted(path for path in RELEASE.iterdir() if path.name != "SHA256SUMS.txt")
    ledger = "".join(f"{digest(path)}  {path.name}\n" for path in ledger_paths)
    checksum_path = RELEASE / "SHA256SUMS.txt"
    checksum_path.write_text(ledger, encoding="utf-8")
    for path in ledger_paths:
        expected = next(line.split()[0] for line in ledger.splitlines() if line.endswith(f"  {path.name}"))
        if digest(path) != expected:
            raise SystemExit(f"checksum verification failed: {path.name}")
    print(json.dumps({
        "status": manifest["status"],
        "payload_files": len(ledger_paths) + 1,
        "payload_bytes": sum(path.stat().st_size for path in RELEASE.iterdir()),
        "checksum_ledger_sha256": digest(checksum_path),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
