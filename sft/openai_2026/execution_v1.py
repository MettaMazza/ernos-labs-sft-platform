"""Official execution bindings for the twelve OpenAI 2026 SFT obligations."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.openai_2026.derivation_v1 import OpenAI2026Program, validate_derivation_spec
from sft.verification import ClaimExecution


REGISTRY = Path("census/openai_ten_advances_2026_sft_obligation_registry_v1.json")
OWNER_LEDGER = Path("audits/OPENAI_TEN_ADVANCES_ONE_OWNER_LEDGER_2026-08-02.json")


def current_certificate(root: Path, claim_id: str) -> Path:
    census = json.loads((root / "census/claims.json").read_text(encoding="utf-8"))
    row = next(row for row in census["claims"] if row["claim_id"] == claim_id)
    matches = [
        path
        for path in sorted((root / "claims" / claim_id).glob("certificate*.json"))
        if json.loads(path.read_text(encoding="utf-8")).get("engine_receipt_hash") == row["receipt_hash"]
    ]
    if len(matches) != 1:
        raise ValueError(f"{claim_id} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    package = root / "claims" / claim_id
    spec = json.loads((package / "derivation_spec_v1.json").read_text(encoding="utf-8"))
    validate_derivation_spec(spec)
    validator = root / "generated/openai_2026_sft_obligation_validator_v1.py"
    files = [
        root / "sft/openai_2026/obligations_v1.py",
        root / "sft/openai_2026/derivation_v1.py",
        root / "sft/openai_2026/execution_v1.py",
        validator,
        root / REGISTRY,
        root / OWNER_LEDGER,
        package / "source_statement.json",
        package / "translation.json",
        package / "correspondence_obligation.json",
        package / "derivation_spec_v1.json",
        root / "generated/lean4_validation/SFTValidation/OpenAI2026/Correspondence.lean",
        root / "generated/lean4_validation/SFTValidation/OpenAI2026/Obligations.lean",
        root / "generated/lean4_validation/reports/openai_2026_obligations_lean4.json",
        execution_file,
    ]
    for dependency in spec["dependencies"]:
        files.extend((
            root / "claims" / dependency / "registration.json",
            current_certificate(root, dependency),
        ))
    source_files = tuple(dict.fromkeys(files))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    independent = ExternalCommandValidator(
        "sft-openai-2026-obligations-independent-python/1",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
        timeout_seconds=180,
    )
    return ClaimExecution(OpenAI2026Program(spec, source_hash), independent, source_files)
