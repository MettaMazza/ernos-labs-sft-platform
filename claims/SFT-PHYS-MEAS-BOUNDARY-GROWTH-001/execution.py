"""Official execution binding for SFT-PHYS-MEAS-BOUNDARY-GROWTH-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.formal_law import FormalPrerequisiteProgram
from sft.physics.source_boundary_growth import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/formal_law.py",
        root / "sft/physics/source_boundary_growth.py",
        root / "claims/SFT-PHYS-MEAS-BOUNDARY-GROWTH-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-MEAS-BOUNDARY-GROWTH-001/independent_validator.py"
    return ClaimExecution(
        program=FormalPrerequisiteProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-meas-boundary-growth-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
