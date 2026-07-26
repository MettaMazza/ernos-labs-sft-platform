"""Official frozen-engine binding for the common scale-axis claim."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.common_scale_axis_terminal_law_v1 import CLAIM_ID, CommonScaleAxisProgram, SPEC
from sft.physics.common_scale_axis_terminal_validation_v1 import CommonScaleAxisTerminalValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/common_scale_axis_terminal_law_v1.py",
        root / "sft/physics/common_scale_axis_terminal_validation_v1.py",
        root / "sft/physics/common_scale_axis_terminal_execution_v1.py",
        root / "sft/physics/coupling_running_convergence_terminal_law_v1.py",
        root / "sft/physics/precision_value_laws_v1.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/lineage_particle_laws.py",
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
    validator = root / "generated/physics/common_scale_axis_terminal_validator_v1.py"
    return ClaimExecution(
        program=CommonScaleAxisProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-common-scale-axis-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=CommonScaleAxisTerminalValidator(root),
    )


__all__ = ("build_execution",)
