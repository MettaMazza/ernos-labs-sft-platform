"""Official empirical binding for the thermal-history comparison."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.thermal_history_empirical_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, SPEC
from sft.physics.thermal_history_validation_v1 import ThermalHistoryValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/thermal_history_recombination_terminal_law_v1.py",
        root / "sft/physics/thermal_history_empirical_v1.py",
        root / "sft/physics/thermal_history_validation_v1.py",
        root / "sft/physics/thermal_history_empirical_execution_v1.py",
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
    validator = root / "generated/physics/thermal_history_empirical_validator_v1.py"
    return ClaimExecution(
        program=ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-thermal-history-empirical-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ThermalHistoryValidator(root),
    )


__all__ = ("build_execution",)
