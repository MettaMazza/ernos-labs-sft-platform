"""Deterministic persistence and verification of accepted or rejected receipts."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Mapping

from sft.engine.canonical import canonical_json, sha256_identity
from sft.engine.engine import receipt_dict
from sft.engine.model import EngineReceipt, GateResult


def write_receipt(path: Path, receipt: EngineReceipt) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = receipt_dict(receipt)
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=str(path.parent),
        prefix=path.name + ".",
        suffix=".pending",
        delete=False,
    ) as handle:
        handle.write(rendered)
        pending = Path(handle.name)
    pending.replace(path)


def verify_receipt_mapping(payload: Mapping[str, object]) -> bool:
    if "receipt_hash" not in payload:
        return False
    claimed_hash = payload["receipt_hash"]
    unhashed = {key: value for key, value in payload.items() if key != "receipt_hash"}
    return claimed_hash == sha256_identity(unhashed)


def canonical_receipt_text(receipt: EngineReceipt) -> str:
    return canonical_json(receipt_dict(receipt))


def read_receipt(path: Path) -> EngineReceipt:
    """Load and verify an immutable engine receipt from JSON."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not verify_receipt_mapping(payload):
        raise ValueError(f"engine receipt identity is invalid: {path}")
    expected = {
        "engine_id",
        "claim_id",
        "accepted_evidence",
        "model_admitted",
        "closure_status",
        "external_status",
        "halted_stage",
        "violations",
        "gate_results",
        "derivation_seal_hash",
        "receipt_hash",
    }
    if set(payload) != expected:
        raise ValueError(f"engine receipt fields are invalid: {path}")
    gates = tuple(GateResult(**item) for item in payload["gate_results"])
    return EngineReceipt(
        engine_id=payload["engine_id"],
        claim_id=payload["claim_id"],
        accepted_evidence=payload["accepted_evidence"],
        model_admitted=payload["model_admitted"],
        closure_status=payload["closure_status"],
        external_status=payload["external_status"],
        halted_stage=payload["halted_stage"],
        violations=tuple(payload["violations"]),
        gate_results=gates,
        derivation_seal_hash=payload["derivation_seal_hash"],
        receipt_hash=payload["receipt_hash"],
    )
