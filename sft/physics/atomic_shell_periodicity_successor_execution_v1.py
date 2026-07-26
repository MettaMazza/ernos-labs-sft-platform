"""Official engine binding for terminal atomic shell periodicity."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_shell_periodicity_successor_laws_v1 import ATOMIC_SHELL_PERIODICITY_SPEC
from sft.physics.atomic_shell_periodicity_successor_validation_v1 import AtomicShellPeriodicityValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_atomic_shell_periodicity_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/atomic_shell_periodicity_successor_laws_v1.py",
        root / "sft/physics/atomic_shell_periodicity_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/atomic_shell_periodicity_successor_execution_v1.py",
        execution_file,
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/atomic_shell_periodicity_successor_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(ATOMIC_SHELL_PERIODICITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-atomic-shell-periodicity-independent-python/1",
            (sys.executable, str(validator), ATOMIC_SHELL_PERIODICITY_SPEC.claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=AtomicShellPeriodicityValidator(root),
    )


__all__ = ("build_atomic_shell_periodicity_execution",)
