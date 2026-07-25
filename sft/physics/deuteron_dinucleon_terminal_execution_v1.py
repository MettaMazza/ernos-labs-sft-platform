"""Official frozen-engine binding for the terminal deuteron law."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.deuteron_dinucleon_terminal_law_v1 import (
    CLAIM_ID,
    DeuteronDinucleonProgram,
)
from sft.physics.deuteron_dinucleon_terminal_validation_v1 import (
    DeuteronDinucleonValidator,
)
from sft.verification import ClaimExecution


def build_deuteron_dinucleon_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/foundation/half_one.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/quantum_physics_laws.py",
        root / "sft/physics/nucleon_binding_successor_laws_v1.py",
        root / "sft/physics/nuclear_residual_force_successor_laws_v1.py",
        root / "sft/physics/deuteron_dinucleon_terminal_law_v1.py",
        root / "sft/physics/deuteron_dinucleon_terminal_validation_v1.py",
        root / "sft/physics/deuteron_dinucleon_terminal_execution_v1.py",
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
    validator = root / "generated/physics/deuteron_dinucleon_terminal_validator_v1.py"
    return ClaimExecution(
        program=DeuteronDinucleonProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-deuteron-dinucleon-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=DeuteronDinucleonValidator(root),
    )


__all__ = ("build_deuteron_dinucleon_execution",)
