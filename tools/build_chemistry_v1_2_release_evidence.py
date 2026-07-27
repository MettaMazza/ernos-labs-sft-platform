#!/usr/bin/env python3
"""Build the local Chemistry v1.2 publication evidence from admitted receipts.

This is a read-only projection of scientific authority. It does not call or
modify the admission engine, protected verifiers, claims, receipts or census.
It writes only versioned publication evidence and a local successor manifest.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md"
PDF = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001-v1.2.pdf"
METADATA = ROOT / "publication/chemistry_zenodo_metadata.json"
EVIDENCE = ROOT / "publications/current/chemistry/evidence_map_v1.2.json"
MANIFEST = ROOT / "publications/current/chemistry/manifest_v1.2.json"


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    metadata = read(METADATA)
    if metadata["metadata"]["version"] != "1.2.0" or metadata["publication_authorized"]:
        raise SystemExit("Chemistry v1.2 must remain a local unauthorized successor")
    paper_text = PAPER.read_text(encoding="utf-8")
    census = read(ROOT / "census/claims.json")["claims"]
    rows = [row for row in census if row.get("branch") == "chemistry" and row.get("model_admitted") is True]
    if len(rows) != 176:
        raise SystemExit(f"expected 176 admitted Chemistry claims, found {len(rows)}")

    entries = []
    candidate_total = control_total = empirical_total = depth_total = finite_total = 0
    vector_rows = []
    for order, row in enumerate(rows, 1):
        claim_id = row["claim_id"]
        root = ROOT / "claims" / claim_id
        candidate_path = root / "candidate_census.json"
        controls_path = root / "controls.json"
        certificate_path = root / "certificate.json"
        registration_path = root / "registration.json"
        independent_path = root / "independent_validator.py"
        execution_path = root / "execution.py"
        required = (
            registration_path, candidate_path, controls_path, certificate_path,
            independent_path, execution_path, ROOT / row["receipt_path"],
        )
        missing = [path.relative_to(ROOT).as_posix() for path in required if not path.is_file()]
        if missing:
            raise SystemExit(f"{claim_id} missing {missing}")

        candidate = read(candidate_path)
        decision_paths = [
            path for path in root.glob("*receipt.json")
            if path.name != "empirical_validation.json" and "decisions" in read(path)
        ]
        if len(decision_paths) != 1:
            raise SystemExit(f"{claim_id} has {len(decision_paths)} decision receipts")
        decisions = read(decision_paths[0])["decisions"]
        controls = read(controls_path)["controls"]
        certificate = read(certificate_path)
        expected = candidate["expected_cardinality"]
        if expected != len(candidate["candidates"]) or expected != len(decisions):
            raise SystemExit(f"{claim_id} candidate/decision census is incomplete")
        if sum(bool(item["survives"]) for item in decisions) != 1:
            raise SystemExit(f"{claim_id} does not have exactly one survivor")
        if len(controls) != 4 or not all(item["passed"] for item in controls):
            raise SystemExit(f"{claim_id} controls do not pass")
        if certificate["engine_receipt_hash"] != row["receipt_hash"]:
            raise SystemExit(f"{claim_id} certificate/engine receipt mismatch")
        if claim_id not in paper_text or row["receipt_hash"] not in paper_text:
            raise SystemExit(f"{claim_id} or its receipt is absent from the manuscript")

        empirical_path = root / "empirical_validation.json"
        empirical = read(empirical_path) if empirical_path.exists() else None
        if empirical:
            if not empirical.get("passed") or not empirical.get("all_rows_preserved"):
                raise SystemExit(f"{claim_id} empirical package is not passing and complete")
            empirical_total += 1
        closure = row["closure_status"]
        depth_total += closure == "depth_independent"
        finite_total += closure == "finite_complete"
        candidate_total += expected
        control_total += len(controls)
        vector_rows.append(f"{claim_id}\t{row['receipt_hash']}")
        files = {
            path.name: {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha(path),
            }
            for path in required[:-1]
        }
        files[decision_paths[0].name] = {
            "path": decision_paths[0].relative_to(ROOT).as_posix(),
            "sha256": sha(decision_paths[0]),
        }
        if empirical_path.exists():
            files[empirical_path.name] = {
                "path": empirical_path.relative_to(ROOT).as_posix(),
                "sha256": sha(empirical_path),
            }
        entries.append({
            "order": order,
            "claim_id": claim_id,
            "title": row["title"],
            "closure_status": closure,
            "external_status": row["external_status"],
            "candidate_count": expected,
            "decision_count": len(decisions),
            "survivor_count": 1,
            "control_count": len(controls),
            "independent_implementation_hash": certificate["independent_implementation_hash"],
            "independent_certificate_hash": certificate["independent_certificate_hash"],
            "empirical_package_present": empirical is not None,
            "engine_receipt": {
                "path": row["receipt_path"],
                "receipt_hash": row["receipt_hash"],
                "file_sha256": sha(ROOT / row["receipt_path"]),
            },
            "evidence_files": files,
        })

    if (candidate_total, control_total, empirical_total, depth_total, finite_total) != (45056, 704, 175, 171, 5):
        raise SystemExit("Chemistry v1.2 aggregate evidence differs from the declared live surface")
    receipt_vector = "sha256:" + hashlib.sha256(
        ("\n".join(sorted(vector_rows)) + "\n").encode("utf-8")
    ).hexdigest()
    evidence = {
        "schema": "sft-v3-chemistry-successor-publication-evidence/1",
        "branch_id": "chemistry",
        "version": "1.2.0",
        "publication_authorized": False,
        "foundation_status": "current_evidence_complete__extension_open",
        "full_discipline_status": "active__97_declared_operations_remaining_after_org_011",
        "claim_count": len(entries),
        "candidate_count": candidate_total,
        "survivor_count": len(entries),
        "control_count": control_total,
        "independent_reconstruction_count": len(entries),
        "empirical_package_count": empirical_total,
        "depth_independent_count": depth_total,
        "finite_complete_count": finite_total,
        "claim_receipt_vector": receipt_vector,
        "paper": {"path": PAPER.relative_to(ROOT).as_posix(), "sha256": sha(PAPER)},
        "rendered_paper": {"path": PDF.relative_to(ROOT).as_posix(), "sha256": sha(PDF)},
        "claims": entries,
    }
    write(EVIDENCE, evidence)
    manifest = {
        "schema": "sft-v3-local-successor-publication-manifest/1",
        "branch_id": "chemistry",
        "version": "1.2.0",
        "publication_authorized": False,
        "remote_action_permitted": False,
        "ready_for_editorial_review": True,
        "full_heavy_repository_verification_rerun": False,
        "paper_path": PAPER.relative_to(ROOT).as_posix(),
        "paper_sha256": sha(PAPER),
        "rendered_paper_path": PDF.relative_to(ROOT).as_posix(),
        "rendered_paper_sha256": sha(PDF),
        "rendered_page_count": 1440,
        "evidence_map_path": EVIDENCE.relative_to(ROOT).as_posix(),
        "evidence_map_sha256": sha(EVIDENCE),
        "claim_receipt_vector": receipt_vector,
        "claim_count": len(entries),
        "candidate_count": candidate_total,
        "survivor_count": len(entries),
        "control_count": control_total,
        "empirical_package_count": empirical_total,
        "next_scientific_operation": "SFT-CHEM-OBL-ORG-012",
    }
    write(MANIFEST, manifest)
    print(f"built {EVIDENCE.relative_to(ROOT)} and {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

