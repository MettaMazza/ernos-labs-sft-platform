"""Official joint execution for the dark/baryon value law."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.cosmology_prior_value_laws import DARK_BARYON_SPEC
from sft.physics.cosmology_prior_value_validation import DarkBaryonExternalValidator
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/cosmology_prior_value_laws.py",
        root / "sft/physics/cosmology_prior_value_validation.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "claims/SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001/execution.py",
        root / "sft/engine/fold_language.py",
        root / "sft/engine/custody.py",
        root / "sft/engine/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-COSMO-DARK-BARYON-FRACTION-001/independent_validator.py"
    return ClaimExecution(
        program=StructuralPhysicsProgram(DARK_BARYON_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-cosmo-dark-baryon-fraction-001-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=DarkBaryonExternalValidator(root),
    )
