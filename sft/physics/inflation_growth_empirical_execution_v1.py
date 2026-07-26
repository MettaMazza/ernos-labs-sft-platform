"""Official empirical binding for the inflation-growth comparison."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.inflation_growth_empirical_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, SPEC
from sft.physics.inflation_growth_validation_v1 import InflationGrowthValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/inflation_growth_terminal_law_v1.py",
        root / "sft/physics/inflation_growth_empirical_v1.py",
        root / "sft/physics/inflation_growth_validation_v1.py",
        root / "sft/physics/inflation_growth_empirical_execution_v1.py",
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
    validator = root / "generated/physics/inflation_growth_empirical_validator_v1.py"
    return ClaimExecution(
        program=ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-inflation-growth-empirical-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=InflationGrowthValidator(root),
    )


__all__ = ("build_execution",)
