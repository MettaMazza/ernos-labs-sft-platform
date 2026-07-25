"""Official frozen-engine binding for terminal decay-width laws."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.decay_width_branching_lifetime_terminal_law_v1 import (
    CLAIM_ID,
    DecayWidthBranchingLifetimeProgram,
)
from sft.physics.decay_width_branching_lifetime_terminal_validation_v1 import (
    DecayWidthBranchingLifetimeValidator,
)
from sft.verification import ClaimExecution


def build_decay_width_branching_lifetime_execution(
    root: Path,
    execution_file: Path,
) -> ClaimExecution:
    source_files = (
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/decay_width_branching_lifetime_terminal_law_v1.py",
        root / "sft/physics/decay_width_branching_lifetime_terminal_validation_v1.py",
        root / "sft/physics/decay_width_branching_lifetime_terminal_execution_v1.py",
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
    validator = root / "generated/physics/decay_width_branching_lifetime_terminal_validator_v1.py"
    return ClaimExecution(
        program=DecayWidthBranchingLifetimeProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-decay-width-branching-lifetime-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=DecayWidthBranchingLifetimeValidator(root),
    )


__all__ = ("build_decay_width_branching_lifetime_execution",)
