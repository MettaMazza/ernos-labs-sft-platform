#!/usr/bin/env python3
"""Verify Materials manuscript coverage and build its immutable evidence map."""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.publication import BranchInventory, PaperEvidence, PublicationGate  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402
from sft.materials.generated_law import MATERIALS_SPECS, validate_pre_source_seal  # noqa: E402
from sft.materials.v2_reconciliation import validate_v2_materials_reconciliation  # noqa: E402


INVENTORY_PATH = ROOT / "publications/inventories/materials.json"
PAPER_PATH = ROOT / "publications/current/materials/FROM_FOLD_TO_MATERIALS.md"
PDF_PATH = ROOT / "output/pdf/from-fold-to-materials-branch-paper-001.pdf"
OUTPUT_DIRECTORY = ROOT / "publications/current/materials"
METADATA_PATH = ROOT / "publication/materials_zenodo_metadata.json"
REQUIRED_FILES = (
    "registration.json", "WHY_DERIVATION_CHECK.md", "candidate_census.json",
    "elimination_receipt.json", "controls.json", "empirical_validation.json",
    "certificate.json", "execution.py", "independent_validator.py", "STATUS.md",
)


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def root_reaches(claim_id: str, seen: frozenset[str] = frozenset()) -> bool:
    if claim_id == "SFT-ROOT-THERE-IS-NO-NOTHING":
        return True
    if claim_id in seen:
        return False
    path = ROOT / "claims" / claim_id / "registration.json"
    if not path.is_file():
        return False
    dependencies = read(path).get("dependencies", ())
    return any(root_reaches(row, seen | {claim_id}) for row in dependencies)


def load_inventory() -> tuple[dict, BranchInventory]:
    payload = read(INVENTORY_PATH)
    claimed = payload["inventory_hash"]
    calculated = sha256_identity({key: value for key, value in payload.items() if key != "inventory_hash"})
    if claimed != calculated or not payload["inventory_frozen"]:
        raise ValueError("Materials inventory identity or frozen state differs")
    if payload["required_claim_count"] != 84 or payload["admitted_claim_count_at_freeze"] != 84:
        raise ValueError("Materials inventory is not completely admitted")
    if payload["frontier_obligations"] or payload["unclassified_obligations"]:
        raise ValueError("Materials inventory retains an unclosed obligation")
    if any(row["status"] != "model_admitted" for row in payload["obligations"]):
        raise ValueError("Materials inventory contains an unadmitted row")
    return payload, BranchInventory(
        branch_id="materials", frozen=True, current_knowledge_scope=payload["scope"],
        required_claim_ids=tuple(payload["required_claim_ids"]),
        unclassified_obligations=(), frontier_obligations=(), inventory_hash=claimed,
    )


def claim_entry(order: int, claim_id: str, census_row: dict, paper_text: str) -> dict:
    root = ROOT / "claims" / claim_id
    files = {}
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing Materials evidence file: {path.relative_to(ROOT)}")
        files[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(path)}
    candidate = read(root / "candidate_census.json")
    elimination = read(root / "elimination_receipt.json")
    controls = read(root / "controls.json")["controls"]
    empirical = read(root / "empirical_validation.json")
    certificate = read(root / "certificate.json")
    if candidate["expected_cardinality"] != 256 or len(candidate["candidates"]) != 256 or len(elimination["decisions"]) != 256:
        raise ValueError(f"Materials candidate/decision parity failed: {claim_id}")
    if sum(bool(row["survives"]) for row in elimination["decisions"]) != 1:
        raise ValueError(f"Materials survivor count differs from one: {claim_id}")
    if len(controls) != 4 or not all(row["passed"] for row in controls):
        raise ValueError(f"Materials adverse controls failed: {claim_id}")
    if not empirical["passed"] or not empirical["all_rows_preserved"] or not empirical["target_opened_after_seal"]:
        raise ValueError(f"Materials empirical validation failed: {claim_id}")
    receipt_path = ROOT / census_row["receipt_path"]
    receipt = read_receipt(receipt_path)
    if not receipt.model_admitted or receipt.receipt_hash != census_row["receipt_hash"]:
        raise ValueError(f"Materials receipt is not model-admitted: {claim_id}")
    if certificate["engine_receipt_hash"] != receipt.receipt_hash or certificate["derivation_seal_hash"] != receipt.derivation_seal_hash:
        raise ValueError(f"Materials certificate differs from receipt: {claim_id}")
    if certificate["external_validation_hash"] != receipt.external_validation_hash or certificate["empirical_validation_hash"] != receipt.empirical_validation_hash:
        raise ValueError(f"Materials validation identities differ from receipt: {claim_id}")
    if claim_id not in paper_text or receipt.receipt_hash not in paper_text:
        raise ValueError(f"Materials paper omits claim or receipt: {claim_id}")
    if not root_reaches(claim_id):
        raise ValueError(f"Materials claim does not trace to the root theorem: {claim_id}")
    return {
        "order": order, "claim_id": claim_id, "title": census_row["title"],
        "candidate_count": 256, "decision_count": 256, "survivor_count": 1,
        "closure_status": receipt.closure_status, "external_status": receipt.external_status,
        "root_trace_verified": True, "source_manifest_hash": certificate["source_manifest_hash"],
        "derivation_seal_hash": receipt.derivation_seal_hash,
        "independent_implementation_hash": certificate["independent_implementation_hash"],
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": certificate["measurement_receipt_hash"],
        "external_data_source_ids": empirical["data_source_ids"],
        "engine_receipt": {"path": receipt_path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(receipt_path), "receipt_hash": receipt.receipt_hash},
        "evidence_files": files,
    }


def build_evidence_map() -> tuple[dict, BranchInventory, dict]:
    inventory, branch_inventory = load_inventory()
    validate_v2_materials_reconciliation()
    pre_source_hash = validate_pre_source_seal(ROOT)
    census_rows = read(ROOT / "census/claims.json")["claims"]
    census = {row["claim_id"]: row for row in census_rows}
    paper_text = PAPER_PATH.read_text(encoding="utf-8")
    metadata = read(METADATA_PATH)
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized:
        if not doi or "PUBLISHED OPEN-ACCESS BRANCH PAPER" not in paper_text or doi not in paper_text:
            raise ValueError("authorized Materials paper omits DOI or publication boundary")
        if "LOCAL PREPUBLICATION" in paper_text or "Publication is not yet authorized" in paper_text:
            raise ValueError("authorized Materials paper retains prepublication text")
    elif "LOCAL PREPUBLICATION" not in paper_text:
        raise ValueError("prepublication Materials paper lacks boundary marker")
    entries = [
        claim_entry(index, claim_id, census[claim_id], paper_text)
        for index, claim_id in enumerate(branch_inventory.required_claim_ids, 1)
    ]
    if len(entries) != 84 or sum(row["candidate_count"] for row in entries) != 21504:
        raise ValueError("Materials evidence coverage differs from frozen totals")
    evidence = {
        "schema": "sft-v3-materials-paper-evidence-map/1", "branch_id": "materials",
        "inventory": {"path": INVENTORY_PATH.relative_to(ROOT).as_posix(), "inventory_hash": branch_inventory.inventory_hash, "required_claim_count": 84, "subbranch_counts": inventory["subbranch_counts"]},
        "pre_source_complete_branch_seal_hash": pre_source_hash,
        "paper": {"source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_sha256": raw_sha256(PAPER_PATH), "rendered_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_sha256": raw_sha256(PDF_PATH)},
        "claims": entries, "required_candidate_count": 21504,
        "complete_claim_coverage": True, "root_traces_verified": True,
        "controls_passed": True, "ready_to_publish": True,
        "publication_action_authorized": authorized,
    }
    return evidence, branch_inventory, census


def main() -> None:
    evidence, branch_inventory, census = build_evidence_map()
    evidence_path = OUTPUT_DIRECTORY / "evidence_map.json"
    write(evidence_path, evidence)
    receipts = {
        claim_id: read_receipt(ROOT / census[claim_id]["receipt_path"])
        for claim_id in branch_inventory.required_claim_ids
    }
    paper = PaperEvidence(
        source_hash=raw_sha256(PAPER_PATH), rendered_paper_hash=raw_sha256(PDF_PATH),
        evidence_map_hash=raw_sha256(evidence_path), comprehensive_derivation_coverage=True,
        controls_passed=True,
    )
    publication_receipt = PublicationGate().branch_ready(branch_inventory, receipts, paper)
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1", "branch_id": "materials",
        "inventory_hash": branch_inventory.inventory_hash,
        "source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_hash": paper.source_hash,
        "rendered_paper_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(), "evidence_map_hash": paper.evidence_map_hash,
        "required_claim_count": 84, "generated_candidate_count": 21504,
        "comprehensive_derivation_coverage": True, "controls_passed": True,
        "root_traces_verified": True, "publication_gate_receipt_hash": publication_receipt.receipt_hash,
        "publication_authorized": bool(read(METADATA_PATH)["publication_authorized"]), "ready_to_publish": True,
    }
    write(OUTPUT_DIRECTORY / "manifest.json", manifest)
    write(OUTPUT_DIRECTORY / "publication_receipt.json", asdict(publication_receipt))
    rebuilt, _, _ = build_evidence_map()
    if read(evidence_path) != rebuilt:
        raise ValueError("Materials evidence map is stale")
    print("SFT MATERIALS PUBLICATION-READINESS GATE: PASS")
    print("required Materials claims: 84")
    print("generated candidates: 21504")
    print("root traces: 84")
    print(f"paper hash: {paper.rendered_paper_hash}")
    print(f"publication receipt: {publication_receipt.receipt_hash}")
    print(f"publication authorized: {str(bool(read(METADATA_PATH)['publication_authorized'])).lower()}")


if __name__ == "__main__":
    main()
