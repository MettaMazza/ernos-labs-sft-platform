"""Execution bindings for the twelve OpenAI source-validity disproofs."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.openai_2026.source_validity_v2 import SourceValidityProgramV2, validate_spec
from sft.verification import ClaimExecution


REGISTRY = Path("census/openai_ten_advances_2026_sft_source_validity_registry_v2.json")


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
    spec = json.loads((package / "derivation_spec_v2.json").read_text(encoding="utf-8"))
    source_binding = json.loads((package / "source_binding_v2.json").read_text(encoding="utf-8"))
    validate_spec(spec)
    validator = root / "generated/openai_2026_source_validity_validator_v2.py"
    files = [
        root / "sft/openai_2026/source_validity_v2.py",
        root / "sft/openai_2026/source_validity_execution_v2.py",
        validator,
        root / REGISTRY,
        package / "registration.json",
        package / "source_binding_v2.json",
        package / "source_validity_target_v2.json",
        package / "derivation_spec_v2.json",
        root / source_binding["source_statement_path"],
        root / source_binding["source_file_path"],
        root / "generated/lean4_validation/SFTValidation/OpenAI2026/SourceValidity.lean",
        root / "generated/lean4_validation/reports/openai_2026_source_validity_lean4.json",
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
        "sft-openai-2026-source-validity-independent-python/2",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
        timeout_seconds=180,
    )
    return ClaimExecution(SourceValidityProgramV2(spec, source_hash), independent, source_files)
