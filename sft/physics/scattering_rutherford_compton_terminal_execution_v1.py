"""Official frozen-engine binding for terminal scattering laws."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.scattering_rutherford_compton_terminal_law_v1 import (
    CLAIM_ID,
    ScatteringRutherfordComptonProgram,
)
from sft.physics.scattering_rutherford_compton_terminal_validation_v1 import (
    ScatteringRutherfordComptonValidator,
)
from sft.verification import ClaimExecution


def build_scattering_rutherford_compton_execution(
    root: Path,
    execution_file: Path,
) -> ClaimExecution:
    source_files = (
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/scattering_rutherford_compton_terminal_law_v1.py",
        root / "sft/physics/scattering_rutherford_compton_terminal_validation_v1.py",
        root / "sft/physics/scattering_rutherford_compton_terminal_execution_v1.py",
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
    validator = root / "generated/physics/scattering_rutherford_compton_terminal_validator_v1.py"
    return ClaimExecution(
        program=ScatteringRutherfordComptonProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-physics-scattering-rutherford-compton-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=ScatteringRutherfordComptonValidator(root),
    )


__all__ = ("build_scattering_rutherford_compton_execution",)
