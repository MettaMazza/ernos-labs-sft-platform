"""Official frozen-engine binding for vacuum density scale transport."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.vacuum_density_scale_terminal_law_v1 import CLAIM_ID, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/vacuum_density_scale_terminal_law_v1.py",
        root / "sft/physics/vacuum_density_scale_terminal_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/vacuum_density_scale_terminal_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-vacuum-density-scale-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_execution",)
