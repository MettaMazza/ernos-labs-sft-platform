"""Official joint execution for the spatial-flatness reconstruction."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.spatial_flatness_law import SPATIAL_FLATNESS_SPEC
from sft.physics.spatial_flatness_validation import SpatialFlatnessExternalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/spatial_flatness_law.py",
        root / "sft/physics/spatial_flatness_validation.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "claims/SFT-PHYS-COSMO-SPATIAL-FLATNESS-001/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-COSMO-SPATIAL-FLATNESS-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(SPATIAL_FLATNESS_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-cosmo-spatial-flatness-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=SpatialFlatnessExternalValidator(root),
    )
