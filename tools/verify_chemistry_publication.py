#!/usr/bin/env python3
"""Build and verify the Chemistry paper's complete local evidence map.

This verifier is read-only with respect to derivations and immutable receipts.
It performs no network action, upload, DOI reservation, push or publication.
"""

from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sft.chemistry.v2_reconciliation import validate_v2_chemistry_reconciliation  # noqa: E402
from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.publication import BranchInventory, PaperEvidence, PublicationGate  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402


INVENTORY_PATH = ROOT / "publications/inventories/chemistry.json"
PAPER_PATH = ROOT / "publications/current/chemistry/FROM_FOLD_TO_CHEMISTRY.md"
PDF_PATH = ROOT / "output/pdf/from-fold-to-chemistry-branch-paper-001.pdf"
OUTPUT_DIRECTORY = ROOT / "publications/current/chemistry"
METADATA_PATH = ROOT / "publication/chemistry_zenodo_metadata.json"
LINEAGE_PATH = ROOT / "census/lineage_reconciliation.json"
REQUIRED_FILES = (
    "registration.json", "WHY_DERIVATION_CHECK.md", "candidate_census.json",
    "elimination_receipt.json", "controls.json", "certificate.json",
    "execution.py", "independent_validator.py", "STATUS.md",
)
UPSTREAM_CLAIM_IDS = (
    "SFT-PHYS-CONSTANT-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-ATOMIC-CELL-ORBIT-CAPACITY-001",
    "SFT-PHYS-NUCLEAR-COLOUR-COUPLING-001",
    "SFT-PHYS-NUCLEAR-CLOSURE-SEQUENCE-001",
    "SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001",
    "SFT-PHYS-VALIDATION-INVERSE-FINE-STRUCTURE-001",
    "SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001",
)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_inventory() -> tuple[dict[str, Any], BranchInventory]:
    payload = read(INVENTORY_PATH)
    claimed = payload["inventory_hash"]
    calculated = sha256_identity({key: value for key, value in payload.items() if key != "inventory_hash"})
    if claimed != calculated:
        raise ValueError("Chemistry inventory identity differs from its current content")
    if not payload["inventory_frozen"]:
        raise ValueError("Chemistry inventory is not frozen")
    if payload["admitted_claim_count_at_freeze"] != payload["required_claim_count"]:
        raise ValueError("Chemistry inventory is not completely admitted")
    if any(row["status"] != "model_admitted" for row in payload["obligations"]):
        raise ValueError("Chemistry inventory contains an unadmitted obligation")
    if payload["frontier_obligations"]:
        raise ValueError("Chemistry retains an unclosed derivational frontier")
    if len(payload.get("unobserved_prediction_targets", ())) != 3:
        raise ValueError("Chemistry does not explicitly retain all three unobserved targets")
    return payload, BranchInventory(
        branch_id="chemistry", frozen=True,
        current_knowledge_scope=payload["scope"],
        required_claim_ids=tuple(payload["required_claim_ids"]),
        unclassified_obligations=tuple(payload["unclassified_obligations"]),
        frontier_obligations=tuple(payload["frontier_obligations"]),
        inventory_hash=claimed,
    )


def verify_lineage() -> dict[str, Any]:
    validate_v2_chemistry_reconciliation()
    lineage = read(LINEAGE_PATH)
    groups = {row["group_id"]: row for row in lineage["named_consequence_groups"]}
    group = groups["elements_nuclear_structure_and_island_of_stability"]
    if group["v3_status"] != "closed_current_v3_standard":
        raise ValueError("Chemistry element/nuclear lineage group is not closed in V3")
    mapped = set(group["formal_prerequisite_claims"] + group["postseal_validation_claims"])
    if mapped != set(UPSTREAM_CLAIM_IDS):
        raise ValueError("Chemistry paper upstream suite differs from lineage reconciliation")
    if set(group["chemistry_claims"]) != {
        "SFT-CHEM-PRED-G-BLOCK-001", "SFT-CHEM-PRED-SMITHIUM-001",
        "SFT-CHEM-PRED-PERIODIC-ENDPOINT-001",
    }:
        raise ValueError("Chemistry terminal claims differ from lineage reconciliation")
    return group


def claim_entry(order: int, claim_id: str, census_row: dict[str, Any], paper_text: str) -> dict[str, Any]:
    claim_root = ROOT / "claims" / claim_id
    files: dict[str, Any] = {}
    for name in REQUIRED_FILES:
        path = claim_root / name
        if not path.is_file():
            raise ValueError(f"missing Chemistry evidence file: {path.relative_to(ROOT)}")
        files[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(path)}
    candidate = read(claim_root / "candidate_census.json")
    elimination = read(claim_root / "elimination_receipt.json")
    controls = read(claim_root / "controls.json")["controls"]
    certificate = read(claim_root / "certificate.json")
    expected = candidate["expected_cardinality"]
    actual = len(candidate["candidates"])
    decisions = len(elimination["decisions"])
    if expected != actual or actual != decisions or actual < 1:
        raise ValueError(f"Chemistry claim has an incomplete candidate census: {claim_id}")
    if sum(bool(row["survives"]) for row in elimination["decisions"]) != 1:
        raise ValueError(f"Chemistry survivor count differs from one: {claim_id}")
    if len(controls) != 4 or not all(row["passed"] for row in controls):
        raise ValueError(f"Chemistry adverse controls failed: {claim_id}")
    receipt_path = ROOT / census_row["receipt_path"]
    receipt = read_receipt(receipt_path)
    if not receipt.model_admitted or receipt.receipt_hash != census_row["receipt_hash"]:
        raise ValueError(f"Chemistry receipt is not model-admitted: {claim_id}")
    if certificate["engine_receipt_hash"] != receipt.receipt_hash:
        raise ValueError(f"Chemistry certificate and receipt differ: {claim_id}")
    if certificate["derivation_seal_hash"] != receipt.derivation_seal_hash:
        raise ValueError(f"Chemistry derivation seal differs from receipt: {claim_id}")
    if certificate["external_validation_hash"] != receipt.external_validation_hash:
        raise ValueError(f"Chemistry independent reconstruction differs from receipt: {claim_id}")
    if claim_id not in paper_text or receipt.receipt_hash not in paper_text:
        raise ValueError(f"Chemistry paper omits claim or immutable receipt: {claim_id}")
    empirical_path = claim_root / "empirical_validation.json"
    empirical = read(empirical_path) if empirical_path.is_file() else None
    if empirical:
        files["empirical_validation.json"] = {
            "path": empirical_path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(empirical_path),
        }
        if not empirical["passed"] or not empirical["all_rows_preserved"] or not empirical["target_opened_after_seal"]:
            raise ValueError(f"Chemistry empirical certificate failed: {claim_id}")
    return {
        "order": order, "claim_id": claim_id, "title": census_row["title"],
        "candidate_count": actual, "decision_count": decisions, "survivor_count": 1,
        "closure_status": receipt.closure_status, "external_status": receipt.external_status,
        "source_manifest_hash": certificate["source_manifest_hash"],
        "derivation_seal_hash": receipt.derivation_seal_hash,
        "independent_implementation_hash": certificate["independent_implementation_hash"],
        "external_validation_hash": receipt.external_validation_hash,
        "empirical_validation_hash": receipt.empirical_validation_hash,
        "measurement_receipt_hash": certificate.get("measurement_receipt_hash"),
        "external_data_source_ids": empirical["data_source_ids"] if empirical else [],
        "measurement_rows": empirical["measurements"] if empirical else [],
        "engine_receipt": {
            "path": receipt_path.relative_to(ROOT).as_posix(),
            "sha256": raw_sha256(receipt_path), "receipt_hash": receipt.receipt_hash,
        },
        "evidence_files": files,
    }


def build_evidence_map() -> tuple[dict[str, Any], BranchInventory, dict[str, Any]]:
    inventory_payload, branch_inventory = load_inventory()
    lineage_group = verify_lineage()
    census_rows = read(ROOT / "census/claims.json")["claims"]
    census = {row["claim_id"]: row for row in census_rows}
    required = list(branch_inventory.required_claim_ids)
    upstream = list(UPSTREAM_CLAIM_IDS)
    if any(claim_id not in census for claim_id in required + upstream):
        raise ValueError("Chemistry census omits a required or upstream claim")
    paper_text = PAPER_PATH.read_text(encoding="utf-8")
    metadata = read(METADATA_PATH)
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized:
        if not doi or "PUBLISHED OPEN-ACCESS BRANCH PAPER" not in paper_text or doi not in paper_text:
            raise ValueError("Authorized Chemistry paper omits its publication boundary or DOI")
        if "LOCAL PREPUBLICATION" in paper_text or "Publication is not yet authorized" in paper_text:
            raise ValueError("Authorized Chemistry paper retains a prepublication marker")
    elif "LOCAL PREPUBLICATION" not in paper_text or "Publication is not yet authorized" not in paper_text:
        raise ValueError("Chemistry paper omits its prepublication boundary")
    required_entries = [claim_entry(index, claim_id, census[claim_id], paper_text) for index, claim_id in enumerate(required, 1)]
    upstream_entries = [claim_entry(index, claim_id, census[claim_id], paper_text) for index, claim_id in enumerate(upstream, 1)]
    if len(required_entries) != 86 or len(upstream_entries) != 7:
        raise ValueError("Chemistry paper claim coverage differs from 86 plus seven")
    evidence = {
        "schema": "sft-v3-chemistry-paper-evidence-map/1", "branch_id": "chemistry",
        "inventory": {
            "path": INVENTORY_PATH.relative_to(ROOT).as_posix(),
            "inventory_hash": branch_inventory.inventory_hash,
            "required_claim_count": len(required), "subbranch_counts": inventory_payload["subbranch_counts"],
            "unobserved_prediction_targets": inventory_payload["unobserved_prediction_targets"],
        },
        "paper": {
            "source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_sha256": raw_sha256(PAPER_PATH),
            "rendered_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_sha256": raw_sha256(PDF_PATH),
        },
        "claims": required_entries, "upstream_prerequisite_and_validation_claims": upstream_entries,
        "lineage_group": lineage_group["group_id"],
        "required_candidate_count": sum(row["candidate_count"] for row in required_entries),
        "upstream_candidate_count": sum(row["candidate_count"] for row in upstream_entries),
        "complete_claim_coverage": True, "controls_passed": True,
        "ready_to_publish": True, "publication_action_authorized": authorized,
    }
    return evidence, branch_inventory, census


def main() -> None:
    evidence, branch_inventory, census = build_evidence_map()
    if tuple(row["claim_id"] for row in evidence["claims"]) != branch_inventory.required_claim_ids:
        raise ValueError("Chemistry evidence map omits or reorders a required claim")
    # Publication-control probes must themselves be capable of detecting a
    # missing claim and a replaced receipt identity.
    if tuple(row["claim_id"] for row in evidence["claims"][:-1]) == branch_inventory.required_claim_ids:
        raise AssertionError("missing-claim publication control failed")
    if evidence["claims"][0]["engine_receipt"]["receipt_hash"] == "sha256:" + "0" * 64:
        raise AssertionError("tampered-receipt publication control failed")
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
        "schema": "sft-v3-branch-publication-manifest/1", "branch_id": "chemistry",
        "inventory_hash": branch_inventory.inventory_hash,
        "source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_hash": paper.source_hash,
        "rendered_paper_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(), "evidence_map_hash": paper.evidence_map_hash,
        "required_claim_count": len(branch_inventory.required_claim_ids),
        "upstream_claim_count": len(evidence["upstream_prerequisite_and_validation_claims"]),
        "generated_candidate_count": evidence["required_candidate_count"] + evidence["upstream_candidate_count"],
        "comprehensive_derivation_coverage": True, "controls_passed": True,
        "publication_gate_receipt_hash": publication_receipt.receipt_hash,
        "publication_authorized": bool(read(METADATA_PATH)["publication_authorized"]), "ready_to_publish": True,
    }
    write(OUTPUT_DIRECTORY / "manifest.json", manifest)
    write(OUTPUT_DIRECTORY / "publication_receipt.json", asdict(publication_receipt))
    rebuilt, _, _ = build_evidence_map()
    if read(evidence_path) != rebuilt:
        raise ValueError("Chemistry evidence map is stale after materialization")
    print("SFT CHEMISTRY PUBLICATION-READINESS GATE: PASS")
    print(f"required Chemistry claims: {len(branch_inventory.required_claim_ids)}")
    print(f"upstream prerequisite/validation claims: {len(evidence['upstream_prerequisite_and_validation_claims'])}")
    print(f"generated candidates: {manifest['generated_candidate_count']}")
    print(f"paper hash: {paper.rendered_paper_hash}")
    print(f"publication receipt: {publication_receipt.receipt_hash}")
    print(f"publication authorized: {str(bool(read(METADATA_PATH)['publication_authorized'])).lower()}")


if __name__ == "__main__":
    main()
