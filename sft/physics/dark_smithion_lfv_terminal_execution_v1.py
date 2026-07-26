from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.dark_smithion_lfv_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    files = (
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/sector_inventory_law_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/particle_mode_generation_terminal_law_v1.py",
        root / "sft/physics/dark_smithion_lfv_terminal_law_v1.py",
        root / "sft/physics/dark_smithion_lfv_terminal_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/dark_smithion_lfv_terminal_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator("sft-physics-dark-smithion-lfv-independent-python/1", (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,)),
        files,
    )


__all__ = ("build_execution",)
