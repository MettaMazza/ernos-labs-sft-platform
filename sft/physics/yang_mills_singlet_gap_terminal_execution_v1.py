"""Official frozen-engine binding for the finite colour-singlet gap law."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.yang_mills_singlet_gap_terminal_law_v1 import CLAIM_ID, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/yang_mills_singlet_gap_terminal_law_v1.py",
        root / "sft/physics/yang_mills_singlet_gap_terminal_execution_v1.py",
        root / "sft/physics/interaction_unification_terminal_law_v1.py",
        root / "sft/physics/sector_inventory_law_v1.py",
        root / "sft/physics/strong_carrier_massless_confined_terminal_law_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/engine/canonical.py",
        root / "sft/engine/exact.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/yang_mills_singlet_gap_terminal_validator_v1.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-yang-mills-singlet-gap-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_execution",)
