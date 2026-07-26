"""Official engine binding for the terminal strong-CP/baryon law."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.strong_cp_baryon_stability_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    files = (
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/lineage_particle_laws.py",
        root / "sft/physics/sector_inventory_law_v1.py",
        root / "sft/physics/strong_cp_baryon_stability_terminal_law_v1.py",
        root / "sft/physics/strong_cp_baryon_stability_terminal_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/strong_cp_baryon_stability_terminal_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-strong-cp-baryon-stability-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
