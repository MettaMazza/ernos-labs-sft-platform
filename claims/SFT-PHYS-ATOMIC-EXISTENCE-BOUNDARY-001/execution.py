"""Official execution binding for SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_constants import SPEC_BY_ID
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "claims/SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID['SFT-PHYS-ATOMIC-EXISTENCE-BOUNDARY-001'], source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-phys-atomic-existence-boundary-001-independent-python/1',
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
