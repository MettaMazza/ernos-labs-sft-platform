"""Official execution binding for the inverse-square empirical check."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.physics.inverse_square_validation import CLAIM_ID, InverseSquareExternalValidator, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/inverse_square_validation.py",
        root / f"claims/{CLAIM_ID}/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims" / CLAIM_ID / "independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-validation-inverse-square-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=InverseSquareExternalValidator(root),
    )
