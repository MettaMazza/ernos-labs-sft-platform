"""Official execution binding for SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.thermal_conductivity_batch_v1 import (
    IDENTITY_PATH, PRIMARY_PATH, SOURCE_FILES, SPEC_PATH, TARGET_PATH, THERMAL_CONDUCTIVITY_SPEC,
)
from sft.chemistry.thermal_conductivity_validation_v1 import ThermalConductivityValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/thermal_conductivity_law_v1.py",
        root / "sft/chemistry/thermal_conductivity_batch_v1.py",
        root / "sft/chemistry/thermal_conductivity_validation_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_thermal_conductivity_sources_v1.py",
        root / SPEC_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        *(root / path for path, _hash in SOURCE_FILES),
        root / "claims/SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-THERMAL-CONDUCTIVITY-RELATION-018/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(THERMAL_CONDUCTIVITY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-thermal-conductivity-018-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=ThermalConductivityValidator(root),
    )
