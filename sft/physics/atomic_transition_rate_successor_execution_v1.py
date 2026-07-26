"""Official engine binding for terminal atomic transition-rate completion."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_transition_rate_successor_laws_v1 import ATOMIC_TRANSITION_RATE_SPEC
from sft.physics.atomic_transition_rate_successor_validation_v1 import AtomicTransitionRateValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_atomic_transition_rate_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_spectra_completion_laws_v1.py",
        root / "sft/physics/atomic_transition_rate_successor_laws_v1.py",
        root / "sft/physics/atomic_transition_rate_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/atomic_transition_rate_successor_execution_v1.py",
        execution_file,
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/atomic_transition_rate_successor_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(ATOMIC_TRANSITION_RATE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-atomic-transition-rate-independent-python/1",
            (sys.executable, str(validator), ATOMIC_TRANSITION_RATE_SPEC.claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=AtomicTransitionRateValidator(root),
    )


__all__ = ("build_atomic_transition_rate_execution",)
