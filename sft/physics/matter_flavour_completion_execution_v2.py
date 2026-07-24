"""Official engine binding for dependency-corrected completion claims."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.matter_flavour_completion_laws_v2 import SPEC_BY_ID
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_completion_execution_v2(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v2.py",
        root / "sft/physics/matter_flavour_completion_execution_v2.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/matter_flavour_completion_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID[claim_id], source_hash),
        independent_validator=ExternalCommandValidator(
            f"sft-physics-matter-completion-v2-{claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator), claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_completion_execution_v2",)
