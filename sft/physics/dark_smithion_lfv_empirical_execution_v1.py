from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.dark_smithion_lfv_empirical_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, SPEC
from sft.physics.dark_smithion_lfv_validation_v1 import DarkSmithionLfvValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path):
    files = (
        root / "sft/physics/dark_smithion_lfv_terminal_law_v1.py",
        root / "sft/physics/dark_smithion_lfv_empirical_v1.py",
        root / "sft/physics/dark_smithion_lfv_validation_v1.py",
        root / "sft/physics/dark_smithion_lfv_empirical_execution_v1.py",
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
    validator = root / "generated/physics/dark_smithion_lfv_empirical_validator_v1.py"
    return ClaimExecution(
        ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator("sft-physics-dark-smithion-lfv-empirical-independent-python/1", (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,)),
        files,
        DarkSmithionLfvValidator(root),
    )


__all__ = ("build_execution",)
