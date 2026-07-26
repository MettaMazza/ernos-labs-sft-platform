"""Official empirical engine binding for Landauer comparison."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import (
    BlindExternalMeasurementValidator,
    GeneratedEmpiricalPhysicsProgram,
)
from sft.physics.landauer_demon_empirical_v1 import CLAIM_ID, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/landauer_demon_ledger_terminal_law_v1.py",
        root / "sft/physics/landauer_demon_empirical_v1.py",
        root / "sft/physics/landauer_demon_empirical_execution_v1.py",
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
    validator = root / "generated/physics/landauer_demon_empirical_validator_v1.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-landauer-empirical-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=BlindExternalMeasurementValidator(root, SPEC),
    )


__all__ = ("build_execution",)
