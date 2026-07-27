"""Official execution binding for SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.transition_boundary_batch_v1 import (
    IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH, TRANSITION_BOUNDARY_SPEC,
)
from sft.chemistry.transition_boundary_validation_v1 import TransitionBoundaryValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/transition_boundary_law_v1.py",
        root / "sft/chemistry/transition_boundary_batch_v1.py",
        root / "sft/chemistry/transition_boundary_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_transition_boundary_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-TRANSITION-STATE-EQUIVALENT-BOUNDARY-005/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(TRANSITION_BOUNDARY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-transition-boundary-005-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=TransitionBoundaryValidator(root),
    )
