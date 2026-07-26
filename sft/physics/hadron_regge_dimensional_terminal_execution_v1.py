from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.hadron_regge_dimensional_terminal_law_v1 import CLAIM_ID, SPEC
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    files = (
        root / "sft/physics/relativistic_field_laws_v1.py",
        root / "sft/physics/hadron_regge_successor_laws_v1.py",
        root / "sft/physics/hadron_regge_dimensional_terminal_law_v1.py",
        root / "sft/physics/hadron_regge_dimensional_terminal_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/hadron_regge_dimensional_terminal_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator("sft-physics-hadron-regge-dimensional-independent-python/1", (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,)),
        files,
    )


__all__ = ("build_execution",)
