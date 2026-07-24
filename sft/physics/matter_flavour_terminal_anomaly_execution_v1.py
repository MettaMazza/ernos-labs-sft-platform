"""Official engine bindings for terminal turn and magnetic anomalies."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.matter_flavour_terminal_anomaly_laws_v1 import SPEC_BY_ID
from sft.physics.matter_flavour_terminal_anomaly_validation_v1 import (
    EMPIRICAL_SPEC_BY_ID,
    TerminalAnomalyValidator,
)
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_terminal_anomaly_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_anomaly_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_anomaly_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/matter_flavour_terminal_anomaly_execution_v1.py",
        execution_file,
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/matter_flavour_terminal_anomaly_validator_v1.py"
    empirical_spec = EMPIRICAL_SPEC_BY_ID.get(claim_id)
    empirical_validator = (
        None
        if empirical_spec is None
        else TerminalAnomalyValidator(
            root,
            "electron" if "ELECTRON" in claim_id else "muon",
            empirical_spec,
        )
    )
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID[claim_id], source_hash),
        independent_validator=ExternalCommandValidator(
            f"sft-physics-terminal-anomaly-{claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator), claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=empirical_validator,
    )


__all__ = ("build_terminal_anomaly_execution",)
