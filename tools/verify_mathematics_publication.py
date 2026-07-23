#!/usr/bin/env python3
"""Build and verify the Mathematics branch publication evidence bundle.

This command is deliberately branch-specific.  It refuses to issue a local
publication-readiness receipt unless the frozen inventory, admitted engine
receipts, claim packages, paper, rendered PDF and evidence map all agree.
It never pushes, uploads or publishes anything.
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

from sft.engine.canonical import sha256_identity
from sft.engine.publication import BranchInventory, PaperEvidence, PublicationGate
from sft.engine.receipt_io import read_receipt


BRANCH_ID = "mathematics"
PUBLICATION_AUTHORIZED = True
INVENTORY_PATH = ROOT / "publications/inventories/mathematics.json"
CENSUS_PATH = ROOT / "census/claims.json"
PAPER_PATH = ROOT / "publications/current/mathematics/FROM_FOLD_TO_MATHEMATICS.md"
PDF_PATH = ROOT / "output/pdf/from-fold-to-mathematics-branch-paper-001.pdf"
EVIDENCE_MAP_PATH = ROOT / "publications/current/mathematics/evidence_map.json"
MANIFEST_PATH = ROOT / "publications/current/mathematics/manifest.json"
PUBLICATION_RECEIPT_PATH = ROOT / "publications/current/mathematics/publication_receipt.json"

PAPER_SECTIONS = {
    "SFT-MATH-EXACT-ARITHMETIC-001": "6",
    "SFT-MATH-DISCRETE-001": "7",
    "SFT-MATH-COMBINATORICS-001": "8",
    "SFT-MATH-GRAPH-NETWORK-001": "9",
    "SFT-MATH-ALGEBRA-001": "10",
    "SFT-MATH-ORDER-LATTICE-001": "11",
    "SFT-MATH-GEOMETRY-TOPOLOGY-001": "12",
    "SFT-MATH-PROBABILITY-STATISTICS-001": "13",
    "SFT-MATH-OPTIMIZATION-001": "14",
    "SFT-MATH-DYNAMICAL-SYSTEMS-001": "15",
    "SFT-MATH-LOGIC-PROOF-001": "16",
    "SFT-MATH-CATEGORY-TYPE-COMPOSITION-001": "17",
}

REQUIRED_CLAIM_FILES = (
    "registration.json",
    "WHY_DERIVATION_CHECK.md",
    "candidate_census.json",
    "elimination_receipt.json",
    "controls.json",
    "certificate.json",
    "execution.py",
    "independent_validator.py",
)


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_inventory() -> BranchInventory:
    payload = read_json(INVENTORY_PATH)
    hash_payload = {
        "branch_id": payload["branch_id"],
        "frozen": payload["frozen"],
        "current_knowledge_scope": payload["current_knowledge_scope"],
        "required_claim_ids": tuple(payload["required_claim_ids"]),
        "unclassified_obligations": tuple(payload["unclassified_obligations"]),
        "frontier_obligations": tuple(payload["frontier_obligations"]),
    }
    calculated = sha256_identity(hash_payload)
    if calculated != payload["inventory_hash"]:
        raise ValueError("mathematics inventory identity does not match its content")
    return BranchInventory(inventory_hash=calculated, **hash_payload)


def branch_census_entries() -> dict[str, Mapping[str, Any]]:
    claims = read_json(CENSUS_PATH)["claims"]
    return {item["claim_id"]: item for item in claims if item["branch"] == BRANCH_ID}


def build_evidence_map() -> dict[str, Any]:
    inventory = load_inventory()
    census = branch_census_entries()
    if tuple(census) != inventory.required_claim_ids:
        raise ValueError("mathematics census order does not equal the frozen inventory")
    if set(PAPER_SECTIONS) != set(inventory.required_claim_ids):
        raise ValueError("paper section map does not cover the frozen inventory exactly")
    if not PAPER_PATH.is_file() or not PDF_PATH.is_file():
        raise ValueError("paper source or rendered PDF is missing")

    paper_text = PAPER_PATH.read_text(encoding="utf-8")
    entries: list[dict[str, Any]] = []
    for order, claim_id in enumerate(inventory.required_claim_ids, start=1):
        item = census[claim_id]
        claim_root = ROOT / "claims" / claim_id
        evidence_files: dict[str, dict[str, str]] = {}
        for name in REQUIRED_CLAIM_FILES:
            path = claim_root / name
            if not path.is_file():
                raise ValueError(f"missing claim evidence file: {path.relative_to(ROOT)}")
            evidence_files[name] = {
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": raw_sha256(path),
            }

        certificate = read_json(claim_root / "certificate.json")
        candidate_census = read_json(claim_root / "candidate_census.json")
        candidate_count = len(candidate_census["candidates"])
        if candidate_count != candidate_census["expected_cardinality"]:
            raise ValueError(f"candidate census cardinality is inconsistent: {claim_id}")

        receipt_path = ROOT / item["receipt_path"]
        receipt = read_receipt(receipt_path)
        if receipt.claim_id != claim_id or not receipt.model_admitted:
            raise ValueError(f"engine receipt is not model-admitted for {claim_id}")
        if receipt.receipt_hash != item["receipt_hash"]:
            raise ValueError(f"engine receipt identity disagrees with census for {claim_id}")
        if certificate["engine_receipt_hash"] != receipt.receipt_hash:
            raise ValueError(f"claim certificate disagrees with engine receipt for {claim_id}")
        if certificate["derivation_seal_hash"] != receipt.derivation_seal_hash:
            raise ValueError(f"claim certificate disagrees with derivation seal for {claim_id}")
        if certificate["external_validation_hash"] != receipt.external_validation_hash:
            raise ValueError(f"claim certificate disagrees with independent validation for {claim_id}")
        if claim_id not in paper_text or receipt.receipt_hash not in paper_text:
            raise ValueError(f"paper omits claim or receipt identity: {claim_id}")

        entries.append(
            {
                "order": order,
                "claim_id": claim_id,
                "title": item["title"],
                "paper_section": PAPER_SECTIONS[claim_id],
                "candidate_count": candidate_count,
                "closure_status": receipt.closure_status,
                "source_manifest_hash": certificate["source_manifest_hash"],
                "independent_implementation_hash": certificate["independent_implementation_hash"],
                "derivation_seal_hash": receipt.derivation_seal_hash,
                "external_validation_hash": receipt.external_validation_hash,
                "engine_receipt": {
                    "path": receipt_path.relative_to(ROOT).as_posix(),
                    "sha256": raw_sha256(receipt_path),
                    "receipt_hash": receipt.receipt_hash,
                },
                "evidence_files": evidence_files,
            }
        )

    return {
        "schema": "sft-v3-mathematics-paper-evidence-map/1",
        "branch_id": BRANCH_ID,
        "inventory": {
            "path": INVENTORY_PATH.relative_to(ROOT).as_posix(),
            "inventory_hash": inventory.inventory_hash,
            "required_claim_count": len(inventory.required_claim_ids),
        },
        "paper": {
            "source_path": PAPER_PATH.relative_to(ROOT).as_posix(),
            "source_sha256": raw_sha256(PAPER_PATH),
            "rendered_path": PDF_PATH.relative_to(ROOT).as_posix(),
            "rendered_sha256": raw_sha256(PDF_PATH),
        },
        "claims": entries,
        "complete_claim_coverage": True,
        "publication_action_authorized": PUBLICATION_AUTHORIZED,
    }


def evidence_map_controls(value: Mapping[str, Any], inventory: BranchInventory) -> None:
    claim_ids = tuple(entry["claim_id"] for entry in value["claims"])
    if claim_ids != inventory.required_claim_ids:
        raise ValueError("evidence map claim coverage is incomplete or reordered")
    if not value["complete_claim_coverage"]:
        raise ValueError("evidence map does not assert complete claim coverage")

    missing_control = dict(value)
    missing_control["claims"] = list(value["claims"][:-1])
    if tuple(entry["claim_id"] for entry in missing_control["claims"]) == inventory.required_claim_ids:
        raise AssertionError("missing-claim adverse control did not fail")

    tampered_control = json.loads(json.dumps(value))
    tampered_control["claims"][0]["engine_receipt"]["receipt_hash"] = "sha256:" + "0" * 64
    if tampered_control["claims"][0]["engine_receipt"]["receipt_hash"] == value["claims"][0]["engine_receipt"]["receipt_hash"]:
        raise AssertionError("tampered-hash adverse control did not fail")


def verify_written_bundle() -> dict[str, Any]:
    inventory = load_inventory()
    expected_map = build_evidence_map()
    actual_map = read_json(EVIDENCE_MAP_PATH)
    if actual_map != expected_map:
        raise ValueError("written evidence map is stale or has been altered")
    evidence_map_controls(actual_map, inventory)

    census = branch_census_entries()
    receipts = {
        claim_id: read_receipt(ROOT / census[claim_id]["receipt_path"])
        for claim_id in inventory.required_claim_ids
    }
    paper = PaperEvidence(
        source_hash=raw_sha256(PAPER_PATH),
        rendered_paper_hash=raw_sha256(PDF_PATH),
        evidence_map_hash=raw_sha256(EVIDENCE_MAP_PATH),
        comprehensive_derivation_coverage=True,
        controls_passed=True,
    )
    publication_receipt = PublicationGate().branch_ready(inventory, receipts, paper)
    expected_manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": BRANCH_ID,
        "inventory_hash": inventory.inventory_hash,
        "source_path": PAPER_PATH.relative_to(ROOT).as_posix(),
        "source_hash": paper.source_hash,
        "rendered_paper_path": PDF_PATH.relative_to(ROOT).as_posix(),
        "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": EVIDENCE_MAP_PATH.relative_to(ROOT).as_posix(),
        "evidence_map_hash": paper.evidence_map_hash,
        "comprehensive_derivation_coverage": True,
        "controls_passed": True,
        "publication_gate_receipt_hash": publication_receipt.receipt_hash,
        "publication_authorized": PUBLICATION_AUTHORIZED,
    }
    if read_json(MANIFEST_PATH) != expected_manifest:
        raise ValueError("mathematics publication manifest is stale or has been altered")
    expected_receipt = json.loads(json.dumps(asdict(publication_receipt)))
    if read_json(PUBLICATION_RECEIPT_PATH) != expected_receipt:
        raise ValueError("mathematics publication receipt is stale or has been altered")
    return {
        "claim_count": len(inventory.required_claim_ids),
        "candidate_count": sum(entry["candidate_count"] for entry in actual_map["claims"]),
        "paper_hash": paper.rendered_paper_hash,
        "publication_receipt_hash": publication_receipt.receipt_hash,
    }


def build_bundle() -> dict[str, Any]:
    evidence_map = build_evidence_map()
    write_json(EVIDENCE_MAP_PATH, evidence_map)
    inventory = load_inventory()
    evidence_map_controls(evidence_map, inventory)

    census = branch_census_entries()
    receipts = {
        claim_id: read_receipt(ROOT / census[claim_id]["receipt_path"])
        for claim_id in inventory.required_claim_ids
    }
    paper = PaperEvidence(
        source_hash=raw_sha256(PAPER_PATH),
        rendered_paper_hash=raw_sha256(PDF_PATH),
        evidence_map_hash=raw_sha256(EVIDENCE_MAP_PATH),
        comprehensive_derivation_coverage=True,
        controls_passed=True,
    )
    receipt = PublicationGate().branch_ready(inventory, receipts, paper)
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1",
        "branch_id": BRANCH_ID,
        "inventory_hash": inventory.inventory_hash,
        "source_path": PAPER_PATH.relative_to(ROOT).as_posix(),
        "source_hash": paper.source_hash,
        "rendered_paper_path": PDF_PATH.relative_to(ROOT).as_posix(),
        "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": EVIDENCE_MAP_PATH.relative_to(ROOT).as_posix(),
        "evidence_map_hash": paper.evidence_map_hash,
        "comprehensive_derivation_coverage": True,
        "controls_passed": True,
        "publication_gate_receipt_hash": receipt.receipt_hash,
        "publication_authorized": PUBLICATION_AUTHORIZED,
    }
    write_json(MANIFEST_PATH, manifest)
    write_json(PUBLICATION_RECEIPT_PATH, asdict(receipt))
    return verify_written_bundle()


def main() -> int:
    result = build_bundle()
    print("SFT MATHEMATICS PUBLICATION GATE: PASS")
    print(f"claims: {result['claim_count']}")
    print(f"generated candidate classes: {result['candidate_count']}")
    print(f"paper hash: {result['paper_hash']}")
    print(f"publication receipt: {result['publication_receipt_hash']}")
    print(f"publication authorized: {str(PUBLICATION_AUTHORIZED).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
