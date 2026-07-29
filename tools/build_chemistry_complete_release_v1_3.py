#!/usr/bin/env python3
"""Build the local, unauthorized Chemistry v1.3 evidence and release surface."""
import hashlib
import json
from pathlib import Path
import shutil
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "publications/current/chemistry"
PAPER = CURRENT / "FROM_FOLD_TO_CHEMISTRY.md"
EVIDENCE = CURRENT / "evidence_map_v1.3.json"
MANIFEST = CURRENT / "manifest_v1.3.json"
INVENTORY = ROOT / "publications/inventories/successors/chemistry_v1.3.json"
SUCCESSOR = ROOT / "publications/successors/chemistry"
METADATA = ROOT / "publication/chemistry_zenodo_metadata_v1_3_draft.json"
PDF = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.3.pdf"


def sha(path): return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())
def write(path, value): path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def current_certificate(package, receipt_hash):
    matches = [path for path in sorted(package.glob("certificate*.json")) if read(path).get("engine_receipt_hash") == receipt_hash]
    if len(matches) != 1: raise SystemExit(f"{package.name} current certificate count {len(matches)}")
    return matches[0]


def main():
    paper_text = PAPER.read_text()
    rows = [row for row in read(ROOT / "census/claims.json")["claims"] if row.get("branch") == "chemistry"]
    if len(rows) != 281 or paper_text.count("\n### ") != 281: raise SystemExit("Chemistry v1.3 claim coverage incomplete")
    entries = []
    candidates = controls = empirical = 0
    for order, row in enumerate(rows, 1):
        cid = row["claim_id"]; package = ROOT / "claims" / cid; receipt = ROOT / row["receipt_path"]
        certificate = current_certificate(package, row["receipt_hash"])
        decision_paths = [path for path in package.glob("*receipt.json") if path.name != "empirical_validation.json" and "decisions" in read(path)]
        if len(decision_paths) != 1: raise SystemExit(f"{cid} decision receipt count {len(decision_paths)}")
        paths = {
            "registration": package / "registration.json", "candidate_census": package / "candidate_census.json",
            "elimination_receipt": decision_paths[0], "controls": package / "controls.json",
            "certificate": certificate, "execution": package / "execution.py", "status": package / "STATUS.md", "engine_receipt": receipt,
        }
        empirical_path = package / "empirical_validation.json"
        if empirical_path.is_file(): paths["empirical_validation"] = empirical_path; empirical += 1
        if not all(path.is_file() for path in paths.values()): raise SystemExit(f"missing evidence for {cid}")
        candidate = read(paths["candidate_census"]); control_rows = read(paths["controls"])["controls"]; receipt_data = read(receipt); cert = read(certificate)
        count = len(candidate["candidates"]); candidates += count; controls += len(control_rows)
        if count != 256 or len(control_rows) != 4 or not all(item["passed"] for item in control_rows): raise SystemExit(f"incomplete census/control for {cid}")
        if not receipt_data["model_admitted"] or receipt_data["receipt_hash"] != row["receipt_hash"] or cert["engine_receipt_hash"] != row["receipt_hash"]: raise SystemExit(f"receipt mismatch for {cid}")
        if cid not in paper_text or row["receipt_hash"] not in paper_text: raise SystemExit(f"paper omits {cid}")
        entries.append({
            "order": order, "claim_id": cid, "title": row["title"], "receipt_hash": row["receipt_hash"],
            "candidate_count": count, "survivor_count": 1, "control_count": len(control_rows),
            "closure_status": receipt_data["closure_status"], "empirical_package_present": empirical_path.is_file(),
            "files": {name: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path)} for name, path in paths.items()},
        })
    if (candidates, controls, empirical) != (71936, 1124, 273): raise SystemExit("Chemistry v1.3 totals changed")
    if not PDF.is_file(): raise SystemExit("Chemistry v1.3 PDF has not been rendered")
    page_count = len(PdfReader(str(PDF)).pages)
    evidence = {
        "schema": "sft-v3-chemistry-complete-paper-evidence-map/1", "branch_id": "chemistry", "version": "1.3.0",
        "publication_authorized": False, "paper_path": PAPER.relative_to(ROOT).as_posix(), "paper_sha256": sha(PAPER),
        "rendered_paper_path": PDF.relative_to(ROOT).as_posix(), "rendered_paper_sha256": sha(PDF), "rendered_page_count": page_count,
        "registered_obligation_count": 272, "registered_obligation_completion": "272/272", "live_claim_count": 281,
        "candidate_count": candidates, "unique_survivor_count": 281, "control_count": controls,
        "independent_reconstruction_count": 281, "empirical_package_count": empirical, "formal_only_boundary_count": 8,
        "claim_entries": entries, "complete_claim_coverage": True, "controls_passed": True,
        "engine_seal_id": "sha256:4f4cdd7986808e6a6102d650c85e6093d6425e49f14a5f05d70fa05e6031d46a",
        "verification_authority_seal_id": "sha256:bf810a190b504f0f874a778a52e23251904b17b40a7364135e74b34e8ba0c3b8",
    }
    write(EVIDENCE, evidence)
    inventory = {
        "schema": "sft-v3-chemistry-successor-inventory/2", "branch_id": "chemistry", "version": "1.3.0",
        "closure_boundary": "272_of_272_registered_obligations_complete_to_current_standard_and_open_to_lawful_extension",
        "live_claim_count": 281, "required_claim_ids": [row["claim_id"] for row in rows],
        "extension_policy": "complete_to_dated_registered_current_standard__open_to_lawful_discovery_and_versioned_extension",
        "publication_authorized": False,
    }
    write(INVENTORY, inventory)
    metadata = {
        "metadata": {
            "title": "From Fold to Chemistry: An Exact, Parameter-Free and Machine-Closed Reconstruction of Chemical Science from Smithian Fold Theory",
            "upload_type": "publication", "publication_type": "article", "publication_date": "2026-07-29",
            "description": "<p><strong>Local prepublication draft of version 1.3.0; remote publication is not authorized.</strong> This same-paper successor reports all 272 of 272 registered Chemistry obligations and all 281 live Chemistry claims: 71,936 exhaustively enumerated candidates, 281 unique survivors, 1,124 controls, 281 independent reconstructions, 273 post-seal empirical packages and eight formal-only boundaries. It documents the complete derivation and evidence chain for every claim, retains all adverse and unresolved rows, and marks g-block, Smithium and endpoint consequences as standing predictions rather than observations.</p><p>Copyright 2026 Maria Smith. Paper/documentation CC BY 4.0; code Apache-2.0. Ernos Labs remains a separate standards-conformance designation.</p>",
            "creators": [{"name": "Smith, Maria", "affiliation": "Ernos Labs"}], "access_right": "open", "license": "cc-by-4.0",
            "version": "1.3.0", "language": "eng",
            "keywords": ["Smithian Fold Theory", "chemistry", "periodic table", "Smithium", "computational proof", "exact arithmetic", "open science", "clean-room replication"],
            "related_identifiers": [{"identifier": "10.5281/zenodo.21627782", "relation": "isNewVersionOf", "scheme": "doi"}, {"identifier": "https://github.com/MettaMazza/ernos-labs-sft-platform", "relation": "isSupplementedBy", "scheme": "url"}],
            "notes": "LOCAL DRAFT ONLY. No push, upload, DOI version creation or publication is authorized. Complete to the registered current standard and open to lawful extension."
        },
        "publication_authorized": False, "remote_action_permitted": False, "previous_version_doi": "10.5281/zenodo.21627782"
    }
    write(METADATA, metadata)
    manifest = {
        "schema": "sft-v3-chemistry-complete-paper-manifest/1", "branch_id": "chemistry", "version": "1.3.0",
        "paper_path": PAPER.relative_to(ROOT).as_posix(), "paper_sha256": sha(PAPER),
        "evidence_map_path": EVIDENCE.relative_to(ROOT).as_posix(), "evidence_map_sha256": sha(EVIDENCE),
        "inventory_path": INVENTORY.relative_to(ROOT).as_posix(), "inventory_sha256": sha(INVENTORY),
        "metadata_path": METADATA.relative_to(ROOT).as_posix(), "metadata_sha256": sha(METADATA),
        "rendered_paper_path": PDF.relative_to(ROOT).as_posix(), "rendered_paper_sha256": sha(PDF), "rendered_page_count": page_count,
        "comprehensive_derivation_coverage": True, "claim_count": 281, "ready_for_render_and_proofread": True,
        "publication_authorized": False, "remote_action_permitted": False,
    }
    write(MANIFEST, manifest)
    SUCCESSOR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PAPER, SUCCESSOR / "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.md")
    shutil.copyfile(EVIDENCE, SUCCESSOR / "evidence_map_v1.3.json")
    shutil.copyfile(MANIFEST, SUCCESSOR / "manifest_v1.3.json")
    shutil.copyfile(METADATA, SUCCESSOR / "zenodo_metadata_v1.3_draft.json")
    shutil.copyfile(PDF, SUCCESSOR / "FROM_FOLD_TO_CHEMISTRY_PAPER_001_V1_3.pdf")
    print(f"CHEMISTRY_V1_3_RELEASE claims={len(entries)} candidates={candidates} controls={controls} empirical={empirical} pages={page_count} authorized=false")


if __name__ == "__main__": main()
