"""Official empirical engine binding for the Fizeau discriminator."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.velocity_composition_fizeau_empirical_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, SPEC
from sft.physics.velocity_composition_fizeau_validation_v1 import VelocityCompositionFizeauValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/velocity_composition_terminal_law_v1.py",
        root / "sft/physics/velocity_composition_fizeau_empirical_v1.py",
        root / "sft/physics/velocity_composition_fizeau_validation_v1.py",
        root / "sft/physics/velocity_composition_fizeau_execution_v1.py",
        root / "sft/physics/generated_empirical_law.py",
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
    validator = root / "generated/physics/velocity_composition_fizeau_validator_v1.py"
    return ClaimExecution(
        program=ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-velocity-composition-Fizeau-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=VelocityCompositionFizeauValidator(root),
    )


__all__ = ("build_execution",)
