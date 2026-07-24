"""Official execution binding for the rank-two boundary law."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import BOUNDARY_RANK_SPEC, StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "claims/SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-SPACE-BOUNDARY-RANK-TWO-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(BOUNDARY_RANK_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-space-boundary-rank-two-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
