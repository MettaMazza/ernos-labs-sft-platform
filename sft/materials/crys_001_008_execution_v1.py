"""Execution assembly for the complete Materials CRYS-001--008 family."""

from __future__ import annotations

import json
from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.materials.crys_001_008_external_v1 import CrystallographyExternalValidator, MANIFEST, REGISTRY, VECTOR
from sft.materials.crys_001_008_laws_v1 import CrystallographyProgram, SPECS
from sft.verification import ClaimExecution


def current_certificate(root: Path, claim_id: str) -> Path:
    row = next(item for item in json.loads((root / "census/claims.json").read_text())["claims"] if item["claim_id"] == claim_id)
    matches = [
        path for path in sorted((root / "claims" / claim_id).glob("certificate*.json"))
        if json.loads(path.read_text()).get("engine_receipt_hash") == row["receipt_hash"]
    ]
    if len(matches) != 1:
        raise ValueError(f"{claim_id} current certificate count {len(matches)}")
    return matches[0]


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    manifest = json.loads((root / MANIFEST).read_text())
    vector = json.loads((root / VECTOR).read_text())
    fixed = (
        root / "sft/materials/crys_001_008_laws_v1.py",
        root / "sft/materials/crys_001_008_external_v1.py",
        root / "sft/materials/crys_001_008_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        root / REGISTRY,
        root / MANIFEST,
        root / VECTOR,
        execution_file,
    )
    sources = tuple(root / row["snapshot_path"] for row in manifest["documents"])
    reconstructions = tuple(root / row["text_path"] for row in vector["pdf_text_reconstructions"])
    dependencies = tuple(path for dependency in spec.dependencies for path in (root / "claims" / dependency / "registration.json", current_certificate(root, dependency)))
    source_files = tuple(dict.fromkeys(fixed + sources + reconstructions + dependencies))
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/materials/crys_001_008_validator_v1.py"
    independent = ExternalCommandValidator(
        "sft-materials-crys-001-008-independent-python/1",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
    )
    return ClaimExecution(
        CrystallographyProgram(spec, source_hash),
        independent,
        source_files,
        CrystallographyExternalValidator(root, spec),
    )


__all__ = ("build_execution",)
