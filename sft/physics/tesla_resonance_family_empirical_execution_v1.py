"""Execution builder for complete empirical Tesla-family Claim 082."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.tesla_resonance_family_empirical_v1 import (
    CLAIM_ID,
    ObservationalEmpiricalPhysicsProgram,
    PREREGISTRATION_PATH,
    SOURCE_FILES,
    SOURCE_PATH,
    SPEC,
)
from sft.physics.tesla_resonance_family_empirical_validation_v1 import TeslaResonanceFamilyMeasurementValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    fixed = (
        root / "sft/physics/tesla_resonance_family_empirical_v1.py",
        root / "sft/physics/tesla_resonance_family_empirical_validation_v1.py",
        root / "sft/physics/tesla_resonance_family_empirical_execution_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / SOURCE_PATH,
        root / PREREGISTRATION_PATH,
        root / "experiments/physics/SFT-EXP-PHYS-TESLA-RESONANCE-FAMILY-082/registration.json",
        *(root / path for path, _ in SOURCE_FILES),
        execution_file,
    )
    evidence = []
    for dependency in SPEC.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/tesla_resonance_family_empirical_validator_v1.py"
    return ClaimExecution(
        ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-tesla-resonance-family-empirical-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID),
            validator.parent,
            (validator,),
        ),
        files,
        TeslaResonanceFamilyMeasurementValidator(root),
    )


__all__ = ("build_execution",)
