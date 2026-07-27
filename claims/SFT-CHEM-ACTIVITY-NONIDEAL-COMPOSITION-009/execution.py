"""Official execution binding for SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.solution_activity_batch_v1 import (
    IDENTITY_PATH,
    LANDING_PATH,
    PRIMARY_PATH,
    RAW_PATH,
    SOLUTION_ACTIVITY_SPEC,
    SPEC_PATH,
    TARGET_PATH,
)
from sft.chemistry.solution_activity_validation_v1 import SolutionActivityValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/solution_activity_law_v1.py",
        root / "sft/chemistry/solution_activity_batch_v1.py",
        root / "sft/chemistry/solution_activity_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_solution_activity_sources_v1.py",
        root / SPEC_PATH,
        root / RAW_PATH,
        root / LANDING_PATH,
        root / PRIMARY_PATH,
        root / IDENTITY_PATH,
        root / TARGET_PATH,
        root / "claims/SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ACTIVITY-NONIDEAL-COMPOSITION-009/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(SOLUTION_ACTIVITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-solution-activity-009-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=SolutionActivityValidator(root),
    )
