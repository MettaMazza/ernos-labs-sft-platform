"""Official execution binding for SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.temperature_correspondence_batch_v1 import (
    TEMPERATURE_CORRESPONDENCE_SPEC, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
    PHYSICS_RECORD_PATH, SOURCE_FILES,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.temperature_correspondence_validation_v1 import TemperatureCorrespondenceValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/temperature_correspondence_law_v1.py",
        root / "sft/chemistry/temperature_correspondence_batch_v1.py",
        root / "sft/chemistry/temperature_correspondence_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_temperature_correspondence_sources_v1.py",
        root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH, root / PHYSICS_RECORD_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-TEMPERATURE-CORRESPONDENCE-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(TEMPERATURE_CORRESPONDENCE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-temperature-correspondence-002-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=TemperatureCorrespondenceValidator(root),
    )
