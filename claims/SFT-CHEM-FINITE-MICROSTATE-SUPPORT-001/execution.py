"""Official execution binding for SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.chemistry.finite_microstate_batch_v1 import (
    FINITE_MICROSTATE_SPEC, WATER_PATH, PRIMARY_PATH, IDENTITY_PATH, TARGET_PATH,
    POP_IDENTITY_PATH, POP_TARGET_PATH, STATE_SNAPSHOT_PATHS,
)
from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.finite_microstate_validation_v1 import FiniteMicrostateValidator
from sft.verification import ClaimExecution

def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/finite_microstate_law_v1.py",
        root / "sft/chemistry/finite_microstate_batch_v1.py",
        root / "sft/chemistry/finite_microstate_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_finite_microstate_sources_v1.py",
        root / WATER_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / POP_IDENTITY_PATH, root / POP_TARGET_PATH,
        *(root / path for path in STATE_SNAPSHOT_PATHS),
        root / "claims/SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-FINITE-MICROSTATE-SUPPORT-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(FINITE_MICROSTATE_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-finite-microstate-001-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=FiniteMicrostateValidator(root),
    )
