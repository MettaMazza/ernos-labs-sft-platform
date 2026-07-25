from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.strong_field_nonlinear_fixed_point_terminal_law_v1 import (
    StrongFieldNonlinearFixedPointProgram,
)
from sft.physics.strong_field_nonlinear_fixed_point_terminal_validation_v1 import (
    StrongFieldNonlinearFixedPointValidator,
)
from sft.verification import ClaimExecution


def build_strong_field_nonlinear_fixed_point_execution(root: Path, execution_file: Path) -> ClaimExecution:
    files = (
        root / "sft/physics/strong_field_nonlinear_fixed_point_terminal_law_v1.py",
        root / "sft/physics/strong_field_nonlinear_fixed_point_terminal_validation_v1.py",
        root / "sft/physics/strong_field_nonlinear_fixed_point_terminal_execution_v1.py",
        root / "sft/physics/post_newtonian_fixed_point_terminal_law_v1.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        root / "sft/engine/empirical.py",
        root / "sft/engine/isolation.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/strong_field_nonlinear_fixed_point_terminal_validator_v1.py"
    return ClaimExecution(
        StrongFieldNonlinearFixedPointProgram(source_hash),
        ExternalCommandValidator(
            "sft-physics-strong-field-nonlinear-fixed-point-independent-python/1",
            (sys.executable, str(validator), "SFT-PHYS-STRONG-FIELD-NONLINEAR-FIXED-POINT-TERMINAL-014"),
            validator.parent,
            (validator,),
        ),
        files,
        StrongFieldNonlinearFixedPointValidator(root),
    )


__all__ = ("build_strong_field_nonlinear_fixed_point_execution",)
