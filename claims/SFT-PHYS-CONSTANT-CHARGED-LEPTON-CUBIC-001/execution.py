"""Official execution binding for the charged-lepton cubic invariants."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.prior_value_laws import CHARGED_LEPTON_CUBIC_SPEC
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "claims/SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-CONSTANT-CHARGED-LEPTON-CUBIC-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(CHARGED_LEPTON_CUBIC_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-constant-charged-lepton-cubic-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
