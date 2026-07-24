"""Official execution binding for the inverse-square structural law."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import INVERSE_SQUARE_SPEC, StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "claims/SFT-PHYS-FIELD-INVERSE-SQUARE-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-FIELD-INVERSE-SQUARE-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(INVERSE_SQUARE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-field-inverse-square-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
