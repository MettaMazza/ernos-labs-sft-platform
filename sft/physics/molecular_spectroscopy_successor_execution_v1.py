"""Official engine binding for terminal molecular spectroscopy."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.molecular_spectroscopy_successor_laws_v1 import (
    MOLECULAR_SPECTROSCOPY_SPEC,
    MOLECULAR_SPECTROSCOPY_TERMINAL_ID,
)
from sft.physics.molecular_spectroscopy_successor_validation_v1 import (
    MolecularSpectroscopyValidator,
)
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_molecular_spectroscopy_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/molecular_spectroscopy_successor_laws_v1.py",
        root / "sft/physics/molecular_spectroscopy_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/molecular_spectroscopy_successor_execution_v1.py",
        execution_file,
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/molecular_spectroscopy_successor_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(MOLECULAR_SPECTROSCOPY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-molecular-spectroscopy-terminal-independent-python/1",
            (sys.executable, str(validator), MOLECULAR_SPECTROSCOPY_TERMINAL_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=MolecularSpectroscopyValidator(root),
    )


__all__ = ("build_molecular_spectroscopy_execution",)
