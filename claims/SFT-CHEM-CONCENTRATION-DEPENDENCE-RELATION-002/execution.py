"""Official execution binding for SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002."""

from pathlib import Path
import sys

from sft.chemistry.concentration_dependence_batch_v1 import (
    CONCENTRATION_DEPENDENCE_SPEC, IDENTITY_PATH, PDF_PATH, PRIMARY_PATH, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.concentration_dependence_validation_v1 import ConcentrationDependenceValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/concentration_dependence_law_v1.py",
        root / "sft/chemistry/concentration_dependence_batch_v1.py",
        root / "sft/chemistry/concentration_dependence_validation_v1.py",
        root / "sft/chemistry/generated_law.py", root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py", root / "tools/capture_chemistry_concentration_dependence_sources_v1.py",
        root / SPEC_PATH, root / PDF_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-CONCENTRATION-DEPENDENCE-RELATION-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(CONCENTRATION_DEPENDENCE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator("sft-chem-concentration-dependence-002-independent-python/1", (sys.executable, str(validator)), validator.parent, (validator,)),
        source_files=source_files, empirical_validator=ConcentrationDependenceValidator(root),
    )
