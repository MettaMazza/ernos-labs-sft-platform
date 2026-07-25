"""Official frozen-engine binding for terminal fusion/fission forcing."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.fusion_fission_terminal_law_v1 import (
    CLAIM_ID,
    FusionFissionTerminalProgram,
)
from sft.physics.fusion_fission_terminal_validation_v1 import (
    FusionFissionTerminalValidator,
)
from sft.verification import ClaimExecution


def build_fusion_fission_terminal_execution(
    root: Path, execution_file: Path
) -> ClaimExecution:
    source_files = (
        root / "sft/foundation/half_one.py",
        root / "sft/foundation/exact_operations.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/nuclear_residual_force_successor_laws_v1.py",
        root / "sft/physics/nuclear_binding_curve_successor_laws_v1.py",
        root / "sft/physics/fusion_fission_terminal_law_v1.py",
        root / "sft/physics/fusion_fission_terminal_validation_v1.py",
        root / "sft/physics/fusion_fission_terminal_execution_v1.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        root / "sft/engine/empirical.py",
        root / "sft/engine/isolation.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/fusion_fission_terminal_validator_v1.py"
    return ClaimExecution(
        program=FusionFissionTerminalProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-fusion-fission-terminal-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=FusionFissionTerminalValidator(root),
    )


__all__ = ("build_fusion_fission_terminal_execution",)
