"""Official execution binding for SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006."""

from pathlib import Path
import sys

from sft.chemistry.competing_channel_batch_v1 import (
    COMPETING_CHANNEL_SPEC, IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.competing_channel_validation_v1 import CompetingChannelValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/competing_channel_law_v1.py",
        root / "sft/chemistry/competing_channel_batch_v1.py",
        root / "sft/chemistry/competing_channel_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_competing_channel_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-COMPETING-CHANNEL-BRANCHING-006/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(COMPETING_CHANNEL_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-competing-channel-006-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=CompetingChannelValidator(root),
    )
