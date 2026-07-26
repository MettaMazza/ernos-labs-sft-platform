"""Official joint execution for the Hubble calibration reconstruction."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.hubble_calibration_law import HUBBLE_CALIBRATION_SPEC
from sft.physics.hubble_calibration_validation import HubbleCalibrationExternalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/hubble_calibration_law.py",
        root / "sft/physics/hubble_calibration_validation.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "claims/SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-COSMO-HUBBLE-CALIBRATION-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(HUBBLE_CALIBRATION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-cosmo-hubble-calibration-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=HubbleCalibrationExternalValidator(root),
    )
