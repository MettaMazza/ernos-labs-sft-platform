"""Official frozen-engine binding for the Parker proton-energy claim."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.parker_proton_energy_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.parker_proton_energy_terminal_validation_v1 import ParkerProtonEnergyValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/parker_proton_energy_terminal_law_v1.py",
        root / "sft/physics/parker_proton_energy_terminal_validation_v1.py",
        root / "sft/physics/parker_proton_energy_terminal_execution_v1.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/lineage_particle_laws.py",
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
    validator = root / "generated/physics/parker_proton_energy_terminal_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-parker-proton-energy-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ParkerProtonEnergyValidator(root),
    )


__all__ = ("build_execution",)
