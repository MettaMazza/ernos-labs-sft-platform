"""Official execution binding for SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.one_component_phase_boundary_batch_v1 import (
    IDENTITY_PATH, ONE_COMPONENT_PHASE_BOUNDARY_SPEC, PRIMARY_PATH, RAW_PATH, SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.one_component_phase_boundary_validation_v1 import OneComponentPhaseBoundaryValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/one_component_phase_boundary_law_v1.py",
        root / "sft/chemistry/one_component_phase_boundary_batch_v1.py",
        root / "sft/chemistry/one_component_phase_boundary_validation_v1.py",
        root / "sft/chemistry/phase_rule_law_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_one_component_phase_boundary_sources_v1.py",
        root / SPEC_PATH, root / RAW_PATH, root / PRIMARY_PATH, root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-ONE-COMPONENT-PHASE-BOUNDARY-012/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(ONE_COMPONENT_PHASE_BOUNDARY_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-one-component-phase-boundary-012-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=OneComponentPhaseBoundaryValidator(root),
    )
