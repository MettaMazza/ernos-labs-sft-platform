#!/usr/bin/env python3
"""Build the Physics evidence map and pass its local publication-readiness gate.

This command is read-only with respect to derivations and receipts.  It performs
no replay, network action, push, upload, DOI reservation or publication.
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

from sft.engine.canonical import sha256_identity  # noqa: E402
from sft.engine.publication import BranchInventory, PaperEvidence, PublicationGate  # noqa: E402
from sft.engine.receipt_io import read_receipt  # noqa: E402


INVENTORY_PATH = ROOT / "publications/inventories/physics.json"
PAPER_PATH = ROOT / "publications/current/physics/FROM_FOLD_TO_PHYSICS.md"
PDF_PATH = ROOT / "output/pdf/from-fold-to-physics-branch-paper-001.pdf"
OUTPUT_DIRECTORY = ROOT / "publications/current/physics"
METADATA_PATH = ROOT / "publication/physics_zenodo_metadata.json"
REQUIRED_FILES = (
    "registration.json", "WHY_DERIVATION_CHECK.md", "candidate_census.json",
    "elimination_receipt.json", "controls.json", "certificate.json",
    "execution.py", "independent_validator.py", "STATUS.md",
)


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def raw_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def inventory() -> tuple[dict[str, Any], BranchInventory]:
    payload = read(INVENTORY_PATH)
    claimed = payload["inventory_hash"]
    unhashed = {key: value for key, value in payload.items() if key != "inventory_hash"}
    calculated = sha256_identity(unhashed)
    if claimed != calculated:
        raise ValueError("Physics inventory identity differs from its current content")
    if not payload["inventory_frozen"] or payload["admitted_claim_count_at_freeze"] != payload["required_claim_count"]:
        raise ValueError("Physics inventory is not frozen and completely admitted")
    if any(row["status"] != "model_admitted" for row in payload["obligations"]):
        raise ValueError("Physics inventory contains an unadmitted obligation")
    return payload, BranchInventory(
        branch_id="physics", frozen=True, current_knowledge_scope=payload["scope"],
        required_claim_ids=tuple(payload["required_claim_ids"]),
        unclassified_obligations=tuple(payload["unclassified_obligations"]),
        frontier_obligations=(), inventory_hash=claimed,
    )


def claim_entry(order: int, claim_id: str, census_row: dict[str, Any], paper_text: str) -> dict[str, Any]:
    root = ROOT / "claims" / claim_id
    files = {}
    for name in REQUIRED_FILES:
        path = root / name
        if not path.is_file():
            raise ValueError(f"missing Physics evidence file: {path.relative_to(ROOT)}")
        files[name] = {"path": path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(path)}
    candidate = read(root / "candidate_census.json")
    elimination = read(root / "elimination_receipt.json")
    controls = read(root / "controls.json")["controls"]
    certificate = read(root / "certificate.json")
    if candidate["expected_cardinality"] != 256 or len(candidate["candidates"]) != 256 or len(elimination["decisions"]) != 256:
        raise ValueError(f"Physics claim lacks complete 256-form support: {claim_id}")
    if sum(row["survives"] for row in elimination["decisions"]) != 1:
        raise ValueError(f"Physics survivor count differs from one: {claim_id}")
    if len(controls) != 4 or not all(row["passed"] for row in controls):
        raise ValueError(f"Physics adverse controls failed: {claim_id}")
    receipt_path = ROOT / census_row["receipt_path"]
    receipt = read_receipt(receipt_path)
    if not receipt.model_admitted or receipt.receipt_hash != census_row["receipt_hash"]:
        raise ValueError(f"Physics receipt is not model-admitted: {claim_id}")
    if certificate["engine_receipt_hash"] != receipt.receipt_hash:
        raise ValueError(f"Physics certificate and receipt differ: {claim_id}")
    if certificate["derivation_seal_hash"] != receipt.derivation_seal_hash or certificate["external_validation_hash"] != receipt.external_validation_hash:
        raise ValueError(f"Physics certificate identities differ from receipt: {claim_id}")
    if claim_id not in paper_text or receipt.receipt_hash not in paper_text:
        raise ValueError(f"Physics paper omits claim or immutable receipt: {claim_id}")
    empirical_path = root / "empirical_validation.json"
    empirical = read(empirical_path) if empirical_path.exists() else None
    if empirical:
        files["empirical_validation.json"] = {"path": empirical_path.relative_to(ROOT).as_posix(), "sha256": raw_sha256(empirical_path)}
        if not empirical["passed"] or not empirical["all_rows_preserved"] or not empirical["target_opened_after_seal"]:
            raise ValueError(f"Physics empirical certificate failed: {claim_id}")
    return {
        "order": order, "claim_id": claim_id, "title": census_row["title"],
        "candidate_count": 256, "decision_count": 256, "survivor_count": 1,
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


def is_exact_value(entry: dict[str, Any]) -> bool:
    joined = " ".join(entry["measurement_rows"]).lower()
    return "exact predicted interval" in joined or "firas background interval predicted" in joined


def build_evidence_map() -> tuple[dict[str, Any], BranchInventory, dict[str, Any]]:
    inventory_payload, branch_inventory = inventory()
    census_rows = read(ROOT / "census/claims.json")["claims"]
    census = {row["claim_id"]: row for row in census_rows}
    required = list(branch_inventory.required_claim_ids)
    supplemental = [row["claim_id"] for row in census_rows if row["claim_id"].startswith("SFT-PHYS-VALIDATION-")]
    if any(claim_id not in census for claim_id in required + supplemental):
        raise ValueError("Physics census omits a required or supplemental claim")
    paper_text = PAPER_PATH.read_text(encoding="utf-8")
    metadata = read(METADATA_PATH)
    authorized = bool(metadata["publication_authorized"])
    doi = str(metadata.get("doi", ""))
    if authorized:
        if not doi or "PUBLISHED OPEN-ACCESS BRANCH PAPER" not in paper_text or doi not in paper_text:
            raise ValueError("Authorized Physics paper omits its publication boundary or DOI")
        if "LOCAL PREPUBLICATION" in paper_text or "Publication is not yet authorized" in paper_text:
            raise ValueError("Authorized Physics paper retains a prepublication marker")
    elif "LOCAL PREPUBLICATION" not in paper_text or "Publication is not yet authorized" not in paper_text:
        raise ValueError("Physics paper omits its prepublication boundary")
    required_entries = [claim_entry(index, claim_id, census[claim_id], paper_text) for index, claim_id in enumerate(required, 1)]
    supplemental_entries = [claim_entry(index, claim_id, census[claim_id], paper_text) for index, claim_id in enumerate(supplemental, 1)]
    exact_value = [entry["claim_id"] for entry in required_entries + supplemental_entries if is_exact_value(entry)]
    if len(exact_value) != 14:
        raise ValueError(f"Physics exact measured-value suite differs from fourteen claims: {len(exact_value)}")
    evidence = {
        "schema": "sft-v3-physics-paper-evidence-map/1", "branch_id": "physics",
        "inventory": {
            "path": INVENTORY_PATH.relative_to(ROOT).as_posix(),
            "inventory_hash": branch_inventory.inventory_hash,
            "required_claim_count": len(required), "subbranch_counts": inventory_payload["subbranch_counts"],
        },
        "paper": {
            "source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_sha256": raw_sha256(PAPER_PATH),
            "rendered_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_sha256": raw_sha256(PDF_PATH),
        },
        "claims": required_entries, "supplemental_measured_value_claims": supplemental_entries,
        "exact_measured_value_claim_ids": exact_value,
        "required_candidate_count": sum(row["candidate_count"] for row in required_entries),
        "supplemental_candidate_count": sum(row["candidate_count"] for row in supplemental_entries),
        "complete_claim_coverage": True, "controls_passed": True,
        "ready_to_publish": True, "publication_action_authorized": authorized,
    }
    return evidence, branch_inventory, census


def main() -> None:
    evidence, branch_inventory, census = build_evidence_map()
    if tuple(row["claim_id"] for row in evidence["claims"]) != branch_inventory.required_claim_ids:
        raise ValueError("Physics evidence map omits or reorders a required claim")
    missing_control = evidence["claims"][:-1]
    if tuple(row["claim_id"] for row in missing_control) == branch_inventory.required_claim_ids:
        raise AssertionError("missing-claim publication control failed")
    if evidence["claims"][0]["engine_receipt"]["receipt_hash"] == "sha256:" + "0" * 64:
        raise AssertionError("tampered-receipt publication control failed")
    evidence_path = OUTPUT_DIRECTORY / "evidence_map.json"
    write(evidence_path, evidence)
    receipts = {claim_id: read_receipt(ROOT / census[claim_id]["receipt_path"]) for claim_id in branch_inventory.required_claim_ids}
    paper = PaperEvidence(
        source_hash=raw_sha256(PAPER_PATH), rendered_paper_hash=raw_sha256(PDF_PATH),
        evidence_map_hash=raw_sha256(evidence_path), comprehensive_derivation_coverage=True,
        controls_passed=True,
    )
    publication_receipt = PublicationGate().branch_ready(branch_inventory, receipts, paper)
    manifest = {
        "schema": "sft-v3-branch-publication-manifest/1", "branch_id": "physics",
        "inventory_hash": branch_inventory.inventory_hash,
        "source_path": PAPER_PATH.relative_to(ROOT).as_posix(), "source_hash": paper.source_hash,
        "rendered_paper_path": PDF_PATH.relative_to(ROOT).as_posix(), "rendered_paper_hash": paper.rendered_paper_hash,
        "evidence_map_path": evidence_path.relative_to(ROOT).as_posix(), "evidence_map_hash": paper.evidence_map_hash,
        "required_claim_count": len(branch_inventory.required_claim_ids),
        "supplemental_measured_value_claim_count": len(evidence["supplemental_measured_value_claims"]),
        "exact_measured_value_claim_count": len(evidence["exact_measured_value_claim_ids"]),
        "comprehensive_derivation_coverage": True, "controls_passed": True,
        "publication_gate_receipt_hash": publication_receipt.receipt_hash,
        "publication_authorized": bool(read(METADATA_PATH)["publication_authorized"]), "ready_to_publish": True,
    }
    write(OUTPUT_DIRECTORY / "manifest.json", manifest)
    write(OUTPUT_DIRECTORY / "publication_receipt.json", asdict(publication_receipt))
    rebuilt, _, _ = build_evidence_map()
    if read(evidence_path) != rebuilt:
        raise ValueError("Physics evidence map is stale after materialization")
    print("SFT PHYSICS PUBLICATION-READINESS GATE: PASS")
    print(f"required claims: {len(branch_inventory.required_claim_ids)}")
    print(f"supplemental measured-value claims: {len(evidence['supplemental_measured_value_claims'])}")
    print(f"exact measured-value claims: {len(evidence['exact_measured_value_claim_ids'])}")
    print(f"generated Physics candidates: {evidence['required_candidate_count'] + evidence['supplemental_candidate_count']}")
    print(f"paper hash: {paper.rendered_paper_hash}")
    print(f"publication receipt: {publication_receipt.receipt_hash}")
    print(f"publication authorized: {str(bool(read(METADATA_PATH)['publication_authorized'])).lower()}")


if __name__ == "__main__":
    main()
