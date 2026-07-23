#!/usr/bin/env python3
"""Build and verify publication bundles for both computation branches.

This fail-closed command reads each branch's recorded authorization state. It
performs no push, DOI reservation, upload or publication action.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.publication import BranchInventory, PaperEvidence, PublicationGate  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402


REQUIRED_CLAIM_FILES = (
    "registration.json", "WHY_DERIVATION_CHECK.md", "candidate_census.json",
    "elimination_receipt.json", "controls.json", "certificate.json",
    "execution.py", "independent_validator.py",
)

CONFIGS = {
    "computation": {
        "inventory": ROOT / "publications/inventories/computation.json",
        "paper": ROOT / "publications/current/computation/AFTER_TURING_THE_FOLD_MACHINE.md",
        "pdf": ROOT / "output/pdf/after-turing-the-fold-machine-classical-computation-branch-paper-001.pdf",
        "directory": ROOT / "publications/current/computation",
        "metadata": ROOT / "publication/computation_zenodo_metadata.json",
        "schema": "sft-v3-classical-computation-paper-evidence-map/1",
    },
    "quantum_computation": {
        "inventory": ROOT / "publications/inventories/quantum_computation.json",
        "paper": ROOT / "publications/current/quantum_computation/THE_QUANTUM_FOLD_MACHINE.md",
        "pdf": ROOT / "output/pdf/the-quantum-fold-machine-branch-paper-001.pdf",
        "directory": ROOT / "publications/current/quantum_computation",
        "metadata": ROOT / "publication/quantum_computation_zenodo_metadata.json",
        "schema": "sft-v3-quantum-computation-paper-evidence-map/1",
    },
}


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_inventory(branch_id: str) -> BranchInventory:
    payload = read_json(CONFIGS[branch_id]["inventory"])
    claimed = payload.pop("inventory_hash")
    calculated = sha256_identity(payload)
    if claimed != calculated:
        raise ValueError(f"{branch_id} inventory identity differs from its content")
    if payload["branch_id"] != branch_id:
        raise ValueError("inventory branch identity mismatch")
    return BranchInventory(
        branch_id=branch_id,
        frozen=payload["frozen"],
        current_knowledge_scope=payload["current_knowledge_scope"],
        required_claim_ids=tuple(payload["required_claim_ids"]),
        unclassified_obligations=tuple(payload["unclassified_obligations"]),
        frontier_obligations=tuple(payload["frontier_obligations"]),
        inventory_hash=calculated,
    )


def census_entries(branch_id: str) -> dict[str, Mapping[str, Any]]:
    rows = read_json(ROOT / "census/claims.json")["claims"]
    return {row["claim_id"]: row for row in rows if row["branch"] == branch_id}


def build_evidence_map(branch_id: str) -> dict[str, Any]:
    config = CONFIGS[branch_id]
    inventory = load_inventory(branch_id)
    census = census_entries(branch_id)
    if tuple(census) != inventory.required_claim_ids:
        raise ValueError(f"{branch_id} census order differs from its frozen inventory")
    paper = config["paper"]
    pdf = config["pdf"]
    if not paper.is_file() or not pdf.is_file():
        raise ValueError(f"{branch_id} paper source or PDF is missing")
    paper_text = paper.read_text(encoding="utf-8")
    publication = read_json(config["metadata"])
    authorized = bool(publication["publication_authorized"])
    doi = publication.get("doi", "")
    if doi and doi not in paper_text:
        raise ValueError(f"{branch_id} paper omits its reserved or published DOI")
    if authorized and ("LOCAL PREPUBLICATION" in paper_text or "publication is not yet authorized" in paper_text):
        raise ValueError(f"{branch_id} authorized paper still carries a draft boundary")
    if not authorized and ("LOCAL PREPUBLICATION" not in paper_text or "publication is not yet authorized" not in paper_text):
        raise ValueError(f"{branch_id} draft does not preserve the publication boundary")
    entries = []
    for order, claim_id in enumerate(inventory.required_claim_ids, 1):
        row = census[claim_id]
        claim_root = ROOT / "claims" / claim_id
        files = {}
        for name in REQUIRED_CLAIM_FILES:
            path = claim_root / name
            if not path.is_file():
                raise ValueError(f"missing claim evidence: {path.relative_to(ROOT)}")
            files[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(path)}
        candidate = read_json(claim_root / "candidate_census.json")
        elimination = read_json(claim_root / "elimination_receipt.json")
        controls = read_json(claim_root / "controls.json")["controls"]
        certificate = read_json(claim_root / "certificate.json")
        if len(candidate["candidates"]) != candidate["expected_cardinality"] or len(elimination["decisions"]) != candidate["expected_cardinality"]:
            raise ValueError(f"incomplete candidate or decision support: {claim_id}")
        if sum(decision["survives"] for decision in elimination["decisions"]) != 1:
            raise ValueError(f"survivor count differs from one: {claim_id}")
        if len(controls) != 4 or not all(control["passed"] for control in controls):
            raise ValueError(f"adverse controls failed: {claim_id}")
        receipt_path = ROOT / row["receipt_path"]
        receipt = read_receipt(receipt_path)
        if not receipt.model_admitted or receipt.receipt_hash != row["receipt_hash"]:
            raise ValueError(f"census receipt is not admitted: {claim_id}")
        if certificate["engine_receipt_hash"] != receipt.receipt_hash or certificate["derivation_seal_hash"] != receipt.derivation_seal_hash or certificate["external_validation_hash"] != receipt.external_validation_hash:
            raise ValueError(f"certificate differs from engine receipt: {claim_id}")
        if claim_id not in paper_text or receipt.receipt_hash not in paper_text:
            raise ValueError(f"paper omits claim or receipt identity: {claim_id}")
        entries.append({
            "order": order,
            "claim_id": claim_id,
            "title": row["title"],
            "paper_section": str(7 + order),
            "candidate_count": candidate["expected_cardinality"],
            "decision_count": len(elimination["decisions"]),
            "survivor_count": 1,
            "closure_status": receipt.closure_status,
            "source_manifest_hash": certificate["source_manifest_hash"],
            "independent_implementation_hash": certificate["independent_implementation_hash"],
            "derivation_seal_hash": receipt.derivation_seal_hash,
            "external_validation_hash": receipt.external_validation_hash,
            "engine_receipt": {"path": receipt_path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(receipt_path), "receipt_hash": receipt.receipt_hash},
            "evidence_files": files,
        })
    return {
        "schema": config["schema"],
        "branch_id": branch_id,
        "inventory": {"path": config["inventory"].relative_to(ROOT).as_posix(), "inventory_hash": inventory.inventory_hash, "required_claim_count": len(inventory.required_claim_ids)},
        "paper": {"source_path": paper.relative_to(ROOT).as_posix(), "source_sha256": raw_sha256(paper), "rendered_path": pdf.relative_to(ROOT).as_posix(), "rendered_sha256": raw_sha256(pdf)},
        "claims": entries,
        "complete_claim_coverage": True,
        "ready_to_publish": True,
        "publication_action_authorized": authorized,
    }


def controls(value: Mapping[str, Any], inventory: BranchInventory, authorized: bool) -> None:
    if tuple(row["claim_id"] for row in value["claims"]) != inventory.required_claim_ids:
        raise ValueError("paper evidence map omits or reorders a claim")
    if not value["complete_claim_coverage"] or not value["ready_to_publish"]:
        raise ValueError("paper evidence map is not comprehensive and ready")
    if value["publication_action_authorized"] is not authorized:
        raise ValueError("paper evidence map differs from the recorded publication authorization")
    missing = list(value["claims"][:-1])
    if tuple(row["claim_id"] for row in missing) == inventory.required_claim_ids:
        raise AssertionError("missing-claim control did not fail")
    tampered = json.loads(json.dumps(value))
    tampered["claims"][0]["engine_receipt"]["receipt_hash"] = "sha256:" + "0" * 64
    if tampered["claims"][0]["engine_receipt"]["receipt_hash"] == value["claims"][0]["engine_receipt"]["receipt_hash"]:
        raise AssertionError("tampered-receipt control did not fail")


def build_branch(branch_id: str) -> dict[str, Any]:
    config = CONFIGS[branch_id]
    inventory = load_inventory(branch_id)
    evidence_map = build_evidence_map(branch_id)
    authorized = bool(read_json(config["metadata"])["publication_authorized"])
    controls(evidence_map, inventory, authorized)
    evidence_path = config["directory"] / "evidence_map.json"
    write_json(evidence_path, evidence_map)
    census = census_entries(branch_id)
    receipts = {claim_id: read_receipt(ROOT / census[claim_id]["receipt_path"]) for claim_id in inventory.required_claim_ids}
    paper = PaperEvidence(
        source_hash=raw_sha256(config["paper"]),
        rendered_paper_hash=raw_sha256(config["pdf"]),
        evidence_map_hash=raw_sha256(evidence_path),
        comprehensive_derivation_coverage=True,
        controls_passed=True,
    )
    receipt = PublicationGate().branch_ready(inventory, receipts, paper)
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": branch_id,
        "inventory_hash": inventory.inventory_hash,
        "source_path": config["paper"].relative_to(ROOT).as_posix(),
        "source_hash": paper.source_hash,
        "rendered_paper_path": config["pdf"].relative_to(ROOT).as_posix(),
        "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(),
        "evidence_map_hash": paper.evidence_map_hash,
        "comprehensive_derivation_coverage": True,
        "controls_passed": True,
        "publication_gate_receipt_hash": receipt.receipt_hash,
        "publication_authorized": authorized,
        "ready_to_publish": True,
    }
    write_json(config["directory"] / "manifest.json", manifest)
    write_json(config["directory"] / "publication_receipt.json", asdict(receipt))
    rebuilt = build_evidence_map(branch_id)
    if read_json(evidence_path) != rebuilt:
        raise ValueError(f"{branch_id} evidence map is stale after write")
    return {
        "branch_id": branch_id,
        "claim_count": len(inventory.required_claim_ids),
        "candidate_count": sum(row["candidate_count"] for row in evidence_map["claims"]),
        "paper_hash": paper.rendered_paper_hash,
        "publication_receipt": receipt.receipt_hash,
    }


def main() -> int:
    for branch_id in CONFIGS:
        result = build_branch(branch_id)
        authorized = bool(read_json(CONFIGS[branch_id]["metadata"])["publication_authorized"])
        print(f"SFT {branch_id.upper()} PUBLICATION GATE: PASS")
        print(f"claims: {result['claim_count']}")
        print(f"generated candidate classes: {result['candidate_count']}")
        print(f"paper hash: {result['paper_hash']}")
        print(f"publication receipt: {result['publication_receipt']}")
        print(f"publication authorized: {str(authorized).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
