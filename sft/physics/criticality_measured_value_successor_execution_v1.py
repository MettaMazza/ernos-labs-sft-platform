from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.criticality_measured_value_successor_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, SPEC
from sft.physics.criticality_measured_value_successor_validation_v1 import CriticalityMeasuredValueSuccessorValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    files = (
        root / "sft/physics/criticality_universality_turbulence_terminal_law_v1.py",
        root / "sft/physics/criticality_measured_value_successor_v1.py",
        root / "sft/physics/criticality_measured_value_successor_validation_v1.py",
        root / "sft/physics/criticality_measured_value_successor_execution_v1.py",
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
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/criticality_measured_value_successor_validator_v1.py"
    return ClaimExecution(
        ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator("sft-physics-criticality-measured-value-successor-independent-python/1", (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,)),
        files,
        CriticalityMeasuredValueSuccessorValidator(root),
    )


__all__ = ("build_execution",)
