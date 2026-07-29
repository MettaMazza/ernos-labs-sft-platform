"""Execution builder for empirical new-sector Claim 095."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.new_sector_complete_family_empirical_v1 import CLAIM_ID, ObservationalEmpiricalPhysicsProgram, PREREGISTRATION_PATH, SOURCE_FILES, SOURCE_PATH, SPEC
from sft.physics.new_sector_complete_family_empirical_validation_v1 import NewSectorCompleteFamilyMeasurementValidator
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    fixed = (
        root / "sft/physics/new_sector_complete_family_empirical_v1.py",
        root / "sft/physics/new_sector_complete_family_empirical_validation_v1.py",
        root / "sft/physics/new_sector_complete_family_empirical_execution_v1.py",
        root / "sft/physics/new_sector_complete_family_law_v1.py",
        root / "sft/physics/sector_inventory_validation_v1.py",
        root / "sft/physics/dark_smithion_lfv_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / SOURCE_PATH,
        root / PREREGISTRATION_PATH,
        root / "experiments/physics/SFT-EXP-PHYS-NEW-SECTOR-COMPLETE-FAMILY-095/registration.json",
        *(root / path for path, _ in SOURCE_FILES),
        execution_file,
    )
    evidence = []
    for dependency in SPEC.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/new_sector_complete_family_empirical_validator_v1.py"
    return ClaimExecution(
        ObservationalEmpiricalPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator("sft-physics-new-sector-complete-family-empirical-independent-python/1", (sys.executable, str(validator), CLAIM_ID), validator.parent, (validator,)),
        files,
        NewSectorCompleteFamilyMeasurementValidator(root),
    )


__all__ = ("build_execution",)
