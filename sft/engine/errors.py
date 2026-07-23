"""Fail-closed engine exception."""

from __future__ import annotations

from sft.engine.model import EngineReceipt


class EngineHalt(RuntimeError):
    def __init__(self, receipt: EngineReceipt):
        self.receipt = receipt
        detail = "; ".join(receipt.violations) or "unspecified engine violation"
        super().__init__(f"SFT engine halted at {receipt.halted_stage}: {detail}")
