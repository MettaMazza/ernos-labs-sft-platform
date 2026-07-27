"""Official execution binding for SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001."""

from pathlib import Path
import sys

from sft.chemistry.elementary_transition_rate_batch_v1 import (
    ELEMENTARY_TRANSITION_RATE_SPEC, IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.elementary_transition_rate_validation_v1 import ElementaryTransitionRateValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/elementary_transition_rate_law_v1.py",
        root / "sft/chemistry/elementary_transition_rate_batch_v1.py",
        root / "sft/chemistry/elementary_transition_rate_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_elementary_transition_rate_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _hash in SOURCE_FILES),
        root / "claims/SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ELEMENTARY-TRANSITION-RATE-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ELEMENTARY_TRANSITION_RATE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-elementary-transition-rate-001-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=ElementaryTransitionRateValidator(root),
    )
