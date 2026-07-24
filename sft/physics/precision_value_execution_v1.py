"""Frozen official-execution binding for Physics precision successors."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.precision_value_laws_v1 import SPEC_BY_ID
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_precision_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/lineage_particle_laws.py",
        root / "sft/physics/precision_value_laws_v1.py",
        root / "sft/physics/precision_value_execution_v1.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/precision_value_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID[claim_id], source_hash),
        independent_validator=ExternalCommandValidator(
            f"sft-physics-precision-{claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator), claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_precision_execution",)
