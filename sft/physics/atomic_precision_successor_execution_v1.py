"""Official engine bindings for terminal atomic-precision successors."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_precision_successor_laws_v1 import SPEC_BY_ID
from sft.physics.atomic_precision_successor_validation_v1 import (
    AtomicPrecisionValidator,
    EMPIRICAL_SPEC_BY_ID,
)
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_atomic_precision_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/matter_flavour_laws_v1.py",
        root / "sft/physics/matter_flavour_completion_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_proton_laws_v1.py",
        root / "sft/physics/matter_flavour_terminal_anomaly_laws_v1.py",
        root / "sft/physics/atomic_precision_successor_laws_v1.py",
        root / "sft/physics/atomic_precision_successor_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/atomic_precision_successor_execution_v1.py",
        execution_file,
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/physics/atomic_precision_successor_validator_v1.py"
    empirical_spec = EMPIRICAL_SPEC_BY_ID[claim_id]
    kind = (
        "lamb" if "LAMB" in claim_id else
        "hyperfine" if "HYPERFINE" in claim_id else
        "fine"
    )
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPEC_BY_ID[claim_id], source_hash),
        independent_validator=ExternalCommandValidator(
            f"sft-physics-atomic-precision-{claim_id.lower()}-independent-python/1",
            (sys.executable, str(validator), claim_id),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=AtomicPrecisionValidator(root, kind, empirical_spec),
    )


__all__ = ("build_atomic_precision_execution",)
