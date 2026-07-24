"""Official engine binding for terminal proton/electron precision."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.matter_flavour_terminal_proton_laws_v1 import TERMINAL_PROTON_SPEC
from sft.physics.matter_flavour_terminal_proton_validation_v1 import TerminalProtonValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_terminal_proton_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_proton_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_proton_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/matter_flavour_terminal_proton_execution_v1.py",
        execution_file,
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/matter_flavour_terminal_proton_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(TERMINAL_PROTON_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-terminal-proton-electron-004-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=TerminalProtonValidator(root),
    )


__all__ = ("build_terminal_proton_execution",)
