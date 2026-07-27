"""Official execution binding for SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014."""

from pathlib import Path
import sys

from sft.chemistry.colligative_response_batch_v1 import (
    COLLIGATIVE_RESPONSE_SPEC, IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.colligative_response_validation_v1 import ColligativeResponseValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/colligative_response_law_v1.py",
        root / "sft/chemistry/colligative_response_batch_v1.py",
        root / "sft/chemistry/colligative_response_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_colligative_response_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _hash in SOURCE_FILES),
        root / "claims/SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-COLLIGATIVE-COMPOSITION-RESPONSE-014/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(COLLIGATIVE_RESPONSE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-colligative-response-014-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=ColligativeResponseValidator(root),
    )
