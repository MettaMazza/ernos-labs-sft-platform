"""Official frozen-engine binding for the terminal proton-radius claim."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.proton_radius_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.proton_radius_terminal_validation_v1 import ProtonRadiusTerminalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/proton_radius_terminal_law_v1.py",
        root / "sft/physics/proton_radius_terminal_validation_v1.py",
        root / "sft/physics/proton_radius_terminal_execution_v1.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/structural_constants.py",
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
    validator = root / "generated/physics/proton_radius_terminal_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-proton-radius-terminal-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ProtonRadiusTerminalValidator(root),
    )


__all__ = ("build_execution",)
