"""In-memory authority ledger populated only by model-admitted receipts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from sft.engine.canonical import sha256_identity
from sft.engine.model import EngineReceipt


ENGINE_IDENTITY = "sft-v3-single-admission-engine/1"


@dataclass
class AuthorityLedger:
    admitted_receipts: dict[str, EngineReceipt] = field(default_factory=dict)

    def contains(self, claim_id: str) -> bool:
        receipt = self.admitted_receipts.get(claim_id)
        return bool(receipt and receipt.model_admitted)

    def admit(self, receipt: EngineReceipt) -> None:
        if not receipt.accepted_evidence or not receipt.model_admitted:
            raise ValueError("only model-admitted engine receipts can become dependencies")
        if receipt.engine_id != ENGINE_IDENTITY:
            raise ValueError("receipt was not emitted by the registered engine")
        if receipt.halted_stage is not None or receipt.violations:
            raise ValueError("halted or violated receipt cannot become a dependency")
        if any(not gate.passed for gate in receipt.gate_results):
            raise ValueError("receipt contains a failed admission gate")
        payload = asdict(receipt)
        claimed_hash = payload.pop("receipt_hash")
        if claimed_hash != sha256_identity(payload):
            raise ValueError("receipt identity does not match its contents")
        existing = self.admitted_receipts.get(receipt.claim_id)
        if existing is not None and existing.receipt_hash != receipt.receipt_hash:
            raise ValueError("claim identity already names a different admitted receipt")
        self.admitted_receipts[receipt.claim_id] = receipt
