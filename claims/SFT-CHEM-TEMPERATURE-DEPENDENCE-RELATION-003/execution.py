"""Official execution binding for SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.temperature_dependence_batch_v1 import (
    IDENTITY_PATH, PDF_PATH, PRIMARY_PATH, SPEC_PATH, TARGET_PATH, TEMPERATURE_DEPENDENCE_SPEC,
)
from sft.chemistry.temperature_dependence_validation_v1 import TemperatureDependenceValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/temperature_dependence_law_v1.py",
        root / "sft/chemistry/temperature_dependence_batch_v1.py",
        root / "sft/chemistry/temperature_dependence_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_temperature_dependence_sources_v1.py",
        root / SPEC_PATH, root / PDF_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-TEMPERATURE-DEPENDENCE-RELATION-003/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(TEMPERATURE_DEPENDENCE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-temperature-dependence-003-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=TemperatureDependenceValidator(root),
    )
