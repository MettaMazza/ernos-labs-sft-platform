"""Official frozen-engine binding for terminal coupling-running laws."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.coupling_running_convergence_terminal_law_v1 import (
    CLAIM_ID,
    CouplingRunningConvergenceProgram,
)
from sft.physics.coupling_running_convergence_terminal_validation_v1 import (
    CouplingRunningConvergenceValidator,
)
from sft.verification import ClaimExecution


def build_coupling_running_convergence_execution(
    root: Path,
    execution_file: Path,
) -> ClaimExecution:
    source_files = (
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/lineage_particle_laws.py",
        root / "sft/physics/sector_inventory_law_v1.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/coupling_running_convergence_terminal_law_v1.py",
        root / "sft/physics/coupling_running_convergence_terminal_validation_v1.py",
        root / "sft/physics/coupling_running_convergence_terminal_execution_v1.py",
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
    validator = root / "generated/physics/coupling_running_convergence_terminal_validator_v1.py"
    return ClaimExecution(
        program=CouplingRunningConvergenceProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-coupling-running-convergence-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=CouplingRunningConvergenceValidator(root),
    )


__all__ = ("build_coupling_running_convergence_execution",)
