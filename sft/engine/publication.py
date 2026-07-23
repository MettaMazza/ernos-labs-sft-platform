"""Fail-closed gates for comprehensive branch papers and the final TOE paper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from sft.engine.canonical import is_sha256_identity, sha256_identity
from sft.engine.model import EngineReceipt


class PublicationHalt(RuntimeError):
    def __init__(self, violations: tuple[str, ...]):
        self.violations = violations
        super().__init__("publication gate halted: " + "; ".join(violations))


@dataclass(frozen=True)
class BranchInventory:
    branch_id: str
    frozen: bool
    current_knowledge_scope: str
    required_claim_ids: tuple[str, ...]
    unclassified_obligations: tuple[str, ...]
    frontier_obligations: tuple[str, ...]
    inventory_hash: str


@dataclass(frozen=True)
class PaperEvidence:
    source_hash: str
    rendered_paper_hash: str
    evidence_map_hash: str
    comprehensive_derivation_coverage: bool
    controls_passed: bool


@dataclass(frozen=True)
class BranchPublicationReceipt:
    branch_id: str
    ready: bool
    inventory_hash: str
    paper_hash: str
    covered_claim_ids: tuple[str, ...]
    receipt_hash: str


@dataclass(frozen=True)
class FinalTOEInventory:
    required_branch_ids: tuple[str, ...]
    global_unclassified_obligations: tuple[str, ...]
    global_frontier_obligations: tuple[str, ...]
    inventory_hash: str


@dataclass(frozen=True)
class FinalTOEReceipt:
    ready: bool
    covered_branch_ids: tuple[str, ...]
    paper_hash: str
    receipt_hash: str


class PublicationGate:
    def branch_ready(
        self,
        inventory: BranchInventory,
        claim_receipts: Mapping[str, EngineReceipt],
        paper: PaperEvidence,
    ) -> BranchPublicationReceipt:
        violations: list[str] = []
        if not inventory.branch_id.strip():
            violations.append("branch identity is missing")
        if not inventory.frozen:
            violations.append("current-knowledge obligation inventory is not frozen")
        if not inventory.current_knowledge_scope.strip():
            violations.append("current-knowledge scope is missing")
        if not inventory.required_claim_ids:
            violations.append("branch has no registered current-knowledge obligations")
        if len(set(inventory.required_claim_ids)) != len(inventory.required_claim_ids):
            violations.append("branch obligation inventory contains duplicates")
        if inventory.unclassified_obligations:
            violations.append("branch contains unclassified obligations")
        if inventory.frontier_obligations:
            violations.append("branch contains unclosed frontier obligations")
        if not is_sha256_identity(inventory.inventory_hash):
            violations.append("branch inventory hash is invalid")
        for claim_id in inventory.required_claim_ids:
            receipt = claim_receipts.get(claim_id)
            if receipt is None:
                violations.append(f"missing engine receipt for {claim_id}")
            elif not receipt.model_admitted:
                violations.append(f"claim is not model-admitted: {claim_id}")
        violations.extend(self._paper_violations(paper))
        if violations:
            raise PublicationHalt(tuple(violations))
        payload = {
            "branch_id": inventory.branch_id,
            "ready": True,
            "inventory_hash": inventory.inventory_hash,
            "paper_hash": paper.rendered_paper_hash,
            "covered_claim_ids": inventory.required_claim_ids,
        }
        return BranchPublicationReceipt(receipt_hash=sha256_identity(payload), **payload)

    def final_toe_ready(
        self,
        inventory: FinalTOEInventory,
        branch_receipts: Mapping[str, BranchPublicationReceipt],
        paper: PaperEvidence,
    ) -> FinalTOEReceipt:
        violations: list[str] = []
        if not inventory.required_branch_ids:
            violations.append("final TOE inventory has no registered branches")
        if len(set(inventory.required_branch_ids)) != len(inventory.required_branch_ids):
            violations.append("final TOE branch inventory contains duplicates")
        if inventory.global_unclassified_obligations:
            violations.append("global census contains unclassified obligations")
        if inventory.global_frontier_obligations:
            violations.append("global census contains unclosed frontier obligations")
        if not is_sha256_identity(inventory.inventory_hash):
            violations.append("final TOE inventory hash is invalid")
        for branch_id in inventory.required_branch_ids:
            receipt = branch_receipts.get(branch_id)
            if receipt is None or not receipt.ready:
                violations.append(f"branch paper is not complete: {branch_id}")
        violations.extend(self._paper_violations(paper))
        if violations:
            raise PublicationHalt(tuple(violations))
        payload = {
            "ready": True,
            "covered_branch_ids": inventory.required_branch_ids,
            "paper_hash": paper.rendered_paper_hash,
        }
        return FinalTOEReceipt(receipt_hash=sha256_identity(payload), **payload)

    @staticmethod
    def _paper_violations(paper: PaperEvidence) -> tuple[str, ...]:
        violations: list[str] = []
        for label, value in (
            ("paper source", paper.source_hash),
            ("rendered paper", paper.rendered_paper_hash),
            ("evidence map", paper.evidence_map_hash),
        ):
            if not is_sha256_identity(value):
                violations.append(f"{label} hash is invalid")
        if not paper.comprehensive_derivation_coverage:
            violations.append("paper does not cover every registered derivation")
        if not paper.controls_passed:
            violations.append("paper evidence-map controls failed")
        return tuple(violations)
