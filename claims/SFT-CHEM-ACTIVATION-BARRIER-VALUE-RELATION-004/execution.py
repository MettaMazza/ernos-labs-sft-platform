"""Official execution binding for SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004."""

from pathlib import Path
import sys

from sft.chemistry.activation_barrier_batch_v1 import (
    ACTIVATION_BARRIER_SPEC, IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.activation_barrier_validation_v1 import ActivationBarrierValidator
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/activation_barrier_law_v1.py",
        root / "sft/chemistry/activation_barrier_batch_v1.py",
        root / "sft/chemistry/activation_barrier_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_activation_barrier_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _ in SOURCE_FILES),
        root / "claims/SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ACTIVATION-BARRIER-VALUE-RELATION-004/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ACTIVATION_BARRIER_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-activation-barrier-004-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=ActivationBarrierValidator(root),
    )
