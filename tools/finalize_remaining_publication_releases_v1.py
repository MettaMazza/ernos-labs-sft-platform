#!/usr/bin/env python3
"""Finalise the four versioned release surfaces not covered by branch builders.

This is a local, publication-unauthorised packaging operation.  It never creates
or updates a remote record and it keeps all Zenodo authority flags false.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
ENGINE_SEAL = "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a"
AUTHORITY_SEAL = "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def package_release(output: Path, files: list[tuple[str, Path]], schema: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, source in files:
        require(source.is_file(), f"missing release source: {source}")
        destination = output / name
        shutil.copyfile(source, destination)
        rows.append({"filename": name, "bytes": destination.stat().st_size, "sha256": sha(destination)})
    write(
        output / "99_SHA256SUMS.json",
        {"schema": schema, "publication_authorized": False, "files": rows},
    )


def information_science() -> dict:
    base = ROOT / "publications/successors/information_science"
    paper = base / "FROM_DISTINCTION_TO_INFORMATION_PAPER_001_V1_4.md"
    pdf = ROOT / "output/pdf/from-distinction-to-information-branch-paper-001-v1.4.pdf"
    frozen_path = ROOT / "census/information_science_discipline_obligations.json"
    recon_path = ROOT / "census/information_science_discipline_current_reconciliation_v20.json"
    frozen = read(frozen_path)
    recon = read(recon_path)
    rows = [row for family in frozen["family_order"] for row in recon["completed_families"][family]]
    require(len(rows) == 262 and recon["current_open_count"] == 0, "Information Science reconciliation is not closed")
    claims = []
    candidates = controls = empirical = 0
    for row in rows:
        package = ROOT / "claims" / row["claim_id"]
        census = read(package / "candidate_census.json")
        control_rows = read(package / "controls.json")["controls"]
        decisions = [path for path in package.glob("*receipt.json") if "decisions" in read(path)]
        require(len(decisions) == 1, f"Information Science decision receipt count changed: {row['claim_id']}")
        survivor_count = sum(item["survives"] for item in read(decisions[0])["decisions"])
        empirical_path = package / "empirical_validation.json"
        candidate_count = len(census["candidates"])
        control_count = len(control_rows)
        require(survivor_count == 1 and all(item["passed"] for item in control_rows), f"Information Science evidence halt: {row['claim_id']}")
        candidates += candidate_count
        controls += control_count
        empirical += empirical_path.is_file()
        claims.append(
            {
                "obligation_id": row["obligation_id"],
                "claim_id": row["claim_id"],
                "family": next(family for family in frozen["family_order"] if row in recon["completed_families"][family]),
                "closure_status": row["closure_status"],
                "external_status": row["external_status"],
                "engine_receipt_hash": row["receipt_hash"],
                "receipt_path": row["receipt_path"],
                "candidate_count": candidate_count,
                "unique_survivor_count": survivor_count,
                "control_count": control_count,
                "controls_passed": True,
                "empirical_package_present": empirical_path.is_file(),
            }
        )
    require((candidates, controls, empirical) == (75776, 1048, 250), "Information Science evidence totals changed")
    pages = len(PdfReader(str(pdf)).pages)
    evidence_path = base / "evidence_map_v1_4.json"
    evidence = {
        "schema": "sft-v3-information-science-complete-field-paper-evidence-map/1",
        "branch_id": "information_science",
        "version": "1.4.0",
        "publication_authorized": False,
        "ready_to_publish": False,
        "required_claim_count": 262,
        "candidate_count": candidates,
        "unique_survivor_count": 262,
        "control_count": controls,
        "independent_reconstruction_count": 262,
        "empirical_package_count": empirical,
        "current_open_obligation_count": 0,
        "frozen_census_identity": frozen["census_identity"],
        "reconciliation_identity": recon["reconciliation_identity"],
        "canonical_engine_seal": ENGINE_SEAL,
        "verification_authority_seal": AUTHORITY_SEAL,
        "paper": {"path": paper.relative_to(ROOT).as_posix(), "sha256": sha(paper)},
        "pdf": {"path": pdf.relative_to(ROOT).as_posix(), "sha256": sha(pdf), "pages": pages},
        "claims": claims,
        "complete_claim_coverage": True,
        "controls_passed": True,
        "ready_for_review": True,
    }
    write(evidence_path, evidence)

    metadata_path = base / "zenodo_metadata_v1_4.json"
    metadata = read(base / "zenodo_metadata.json")
    metadata["metadata"]["version"] = "1.4.0"
    metadata["metadata"]["publication_date"] = "2026-07-29"
    metadata["metadata"]["description"] = (
        "<p><strong>Information Science Branch Paper 001, version 1.4.0.</strong> "
        "This same-paper successor completes 262 of 262 current registered obligations: "
        "75,776 generated candidates, 262 unique survivors, 1,048 passed controls, "
        "262 independent reconstructions and 250 post-registry empirical packages.</p>"
        "<p>The branch is complete to its dated current census and remains open to lawful "
        "extension. The release preserves adverse, unresolved, transport and chronology "
        "records and does not treat compatibility, implementation success or correspondence "
        "as empirical confirmation.</p>"
    )
    relations = [item for item in metadata["metadata"].get("related_identifiers", []) if item.get("relation") != "isNewVersionOf"]
    relations.append({"identifier": "10.5281/zenodo.21627717", "relation": "isNewVersionOf", "scheme": "doi"})
    metadata["metadata"]["related_identifiers"] = relations
    metadata["metadata"]["notes"] = "Local candidate only. Publication requires Maria Smith's explicit final approval. Paper and documentation: CC BY 4.0; repository code: Apache-2.0."
    metadata["publication_authorized"] = False
    metadata["ready_to_publish"] = False
    write(metadata_path, metadata)

    manifest_path = base / "manifest_v1_4.json"
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": "information_science",
        "version": "1.4.0",
        "source_path": paper.relative_to(ROOT).as_posix(),
        "source_hash": sha(paper),
        "rendered_paper_path": pdf.relative_to(ROOT).as_posix(),
        "rendered_paper_hash": sha(pdf),
        "pdf_pages": pages,
        "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(),
        "evidence_map_hash": sha(evidence_path),
        "zenodo_metadata_path": metadata_path.relative_to(ROOT).as_posix(),
        "zenodo_metadata_hash": sha(metadata_path),
        "required_claim_count": 262,
        "generated_candidate_count": candidates,
        "control_count": controls,
        "comprehensive_derivation_coverage": True,
        "controls_passed": True,
        "publication_authorized": False,
        "ready_for_review": True,
        "ready_to_publish": False,
    }
    write(manifest_path, manifest)
    package_release(
        ROOT / "output/release/information-science-1.4.0",
        [
            ("00_From-Distinction-to-Information_Information-Science-Branch-Paper-001-v1.4.pdf", pdf),
            ("01_From-Distinction-to-Information_Information-Science-Branch-Paper-001-v1.4.md", paper),
            ("02_Information-Science-Paper-001-v1.4-Evidence-Map.json", evidence_path),
            ("03_Information-Science-Paper-001-v1.4-Manifest.json", manifest_path),
            ("04_Information-Science-Paper-001-v1.4-Zenodo-Metadata-Draft.json", metadata_path),
            ("05_Information-Science-Frozen-Complete-Field-Census.json", frozen_path),
            ("06_Information-Science-Final-Reconciliation-v20.json", recon_path),
        ],
        "sft-information-science-1.4-review-checksums/1",
    )
    return {"branch": "information_science", "claims": 262, "candidates": candidates, "controls": controls, "pages": pages}


def existing_complete_field(branch: str, version: str, stem: str, paper_name: str, pdf_name: str, previous_doi: str, census_name: str, recon_name: str) -> dict:
    base = ROOT / "publications/successors" / branch
    paper = base / paper_name
    pdf = ROOT / "output/pdf" / pdf_name
    evidence_path = base / f"evidence_map_v{stem}.json"
    metadata_path = base / f"zenodo_metadata_v{stem}.json"
    manifest_path = base / f"manifest_v{stem}.json"
    evidence = read(evidence_path)
    metadata = read(metadata_path)
    evidence["publication_authorized"] = False
    evidence["ready_to_publish"] = False
    write(evidence_path, evidence)
    require(metadata["publication_authorized"] is False and metadata["ready_to_publish"] is False, f"{branch} authorization boundary changed")
    require(any(item.get("identifier") == previous_doi and item.get("relation") == "isNewVersionOf" for item in metadata["metadata"]["related_identifiers"]), f"{branch} previous-version relation missing")
    pages = len(PdfReader(str(pdf)).pages)
    manifest = read(manifest_path)
    manifest.update(
        {
            "version": version,
            "source_path": paper.relative_to(ROOT).as_posix(),
            "source_hash": sha(paper),
            "rendered_paper_path": pdf.relative_to(ROOT).as_posix(),
            "rendered_paper_hash": sha(pdf),
            "pdf_pages": pages,
            "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(),
            "evidence_map_hash": sha(evidence_path),
            "zenodo_metadata_path": metadata_path.relative_to(ROOT).as_posix(),
            "zenodo_metadata_hash": sha(metadata_path),
            "publication_authorized": False,
            "ready_for_review": True,
            "ready_to_publish": False,
        }
    )
    write(manifest_path, manifest)
    label = "Classical-Computation" if branch == "computation" else "Quantum-Computation"
    title = "After-Turing-The-Fold-Machine" if branch == "computation" else "The-Quantum-Fold-Machine"
    output = ROOT / "output/release" / (("classical-computation" if branch == "computation" else "quantum-computation") + f"-{version}")
    census = ROOT / "census" / census_name
    recon = ROOT / "census" / recon_name
    recon_release_name = f"06_{label}-Final-Reconciliation.json"
    extras = []
    if branch == "quantum_computation":
        recon_release_name = "06_Quantum-Computation-Final-Reconciliation-v13.json"
        extras.append(
            (
                "07_Quantum-Computation-Active-Completion-Checkpoint.md",
                ROOT / "audits/ACTIVE_QUANTUM_COMPUTATION_CONTINUATION_CHECKPOINT_2026-07-29.md",
            )
        )
    package_release(
        output,
        [
            (f"00_{title}_{label}-Branch-Paper-001-v{stem.replace('_', '.')}.pdf", pdf),
            (f"01_{title}_{label}-Branch-Paper-001-v{stem.replace('_', '.')}.md", paper),
            (f"02_{label}-Paper-001-v{stem.replace('_', '.')}-Evidence-Map.json", evidence_path),
            (f"03_{label}-Paper-001-v{stem.replace('_', '.')}-Manifest.json", manifest_path),
            (f"04_{label}-Paper-001-v{stem.replace('_', '.')}-Zenodo-Metadata-Draft.json", metadata_path),
            (f"05_{label}-Frozen-Complete-Field-Census.json", census),
            (recon_release_name, recon),
            *extras,
        ],
        f"sft-{branch.replace('_', '-')}-{version}-review-checksums/1",
    )
    return {"branch": branch, "claims": evidence["claim_count"], "candidates": evidence["candidate_count"], "controls": evidence["control_count"], "pages": pages}


def chemistry() -> dict:
    base = ROOT / "publications/successors/chemistry"
    paper = base / "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md"
    pdf = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.3.pdf"
    evidence_path = base / "evidence_map_v1.3.json"
    manifest_path = base / "manifest_v1.3.json"
    metadata_path = base / "zenodo_metadata_v1.3_draft.json"
    inventory_path = ROOT / "publications/inventories/successors/chemistry_v1.3.json"
    pages = len(PdfReader(str(pdf)).pages)
    evidence = read(evidence_path)
    evidence.update(
        {
            "paper_path": paper.relative_to(ROOT).as_posix(),
            "paper_sha256": sha(paper),
            "rendered_paper_path": pdf.relative_to(ROOT).as_posix(),
            "rendered_paper_sha256": sha(pdf),
            "rendered_page_count": pages,
            "publication_authorized": False,
            "ready_to_publish": False,
        }
    )
    write(evidence_path, evidence)
    metadata = read(metadata_path)
    metadata["ready_to_publish"] = False
    write(metadata_path, metadata)
    require(
        metadata["publication_authorized"] is False
        and metadata["remote_action_permitted"] is False
        and metadata["ready_to_publish"] is False,
        "Chemistry authorization boundary changed",
    )
    manifest = read(manifest_path)
    manifest.update(
        {
            "paper_path": paper.relative_to(ROOT).as_posix(),
            "paper_sha256": sha(paper),
            "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(),
            "evidence_map_sha256": sha(evidence_path),
            "metadata_path": metadata_path.relative_to(ROOT).as_posix(),
            "metadata_sha256": sha(metadata_path),
            "rendered_paper_path": pdf.relative_to(ROOT).as_posix(),
            "rendered_paper_sha256": sha(pdf),
            "rendered_page_count": pages,
            "publication_authorized": False,
            "remote_action_permitted": False,
            "ready_to_publish": False,
        }
    )
    write(manifest_path, manifest)
    package_release(
        ROOT / "output/release/chemistry-1.3.0",
        [
            ("00_From-Fold-to-Chemistry_Chemistry-Branch-Paper-001-v1.3.pdf", pdf),
            ("01_From-Fold-to-Chemistry_Chemistry-Branch-Paper-001-v1.3.md", paper),
            ("02_Chemistry-Paper-001-v1.3-Evidence-Map.json", evidence_path),
            ("03_Chemistry-Paper-001-v1.3-Manifest.json", manifest_path),
            ("04_Chemistry-Paper-001-v1.3-Zenodo-Metadata-Draft.json", metadata_path),
            ("05_Chemistry-Successor-Inventory.json", inventory_path),
        ],
        "sft-chemistry-1.3-review-checksums/1",
    )
    return {"branch": "chemistry", "claims": evidence["live_claim_count"], "candidates": evidence["candidate_count"], "controls": evidence["control_count"], "pages": pages}


def main() -> None:
    reports = [
        information_science(),
        existing_complete_field("computation", "1.4.0", "1_4", "AFTER_TURING_THE_FOLD_MACHINE_PAPER_001_V1_4.md", "after-turing-the-fold-machine-classical-computation-branch-paper-001-v1.4.pdf", "10.5281/zenodo.21627721", "computation_discipline_obligations.json", "computation_discipline_current_reconciliation_v12.json"),
        existing_complete_field("quantum_computation", "1.4.0", "1_4", "THE_QUANTUM_FOLD_MACHINE_PAPER_001_V1_4.md", "the-quantum-fold-machine-branch-paper-001-v1.4.pdf", "10.5281/zenodo.21627748", "quantum_computation_discipline_obligations.json", "quantum_computation_discipline_current_reconciliation_v13.json"),
        chemistry(),
    ]
    print(json.dumps({"publication_authorized": False, "releases": reports}, indent=2))


if __name__ == "__main__":
    main()
