"""Official engine binding for the terminal nuclear binding curve."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.nuclear_binding_curve_successor_laws_v1 import NUCLEAR_BINDING_CURVE_SPEC
from sft.physics.nuclear_binding_curve_successor_validation_v1 import NuclearBindingCurveValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_nuclear_binding_curve_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/nuclear_residual_force_successor_laws_v1.py",
        root / "sft/physics/nuclear_binding_curve_successor_laws_v1.py",
        root / "sft/physics/nuclear_binding_curve_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/nuclear_binding_curve_successor_execution_v1.py",
        execution_file,
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/nuclear_binding_curve_successor_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(NUCLEAR_BINDING_CURVE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-nuclear-binding-curve-independent-python/1",
            (sys.executable, str(validator), NUCLEAR_BINDING_CURVE_SPEC.claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=NuclearBindingCurveValidator(root),
    )


__all__ = ("build_nuclear_binding_curve_execution",)
