"""Official execution binding for SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013."""

from pathlib import Path
import sys

from sft.chemistry.generated_observational_law import GeneratedObservationalChemistryProgram
from sft.chemistry.multicomponent_phase_diagram_batch_v1 import (
    IDENTITY_PATH, LANDING_PATH, MULTICOMPONENT_PHASE_DIAGRAM_SPEC, PRIMARY_PATH, RAW_PATH,
    SPEC_PATH, TARGET_PATH,
)
from sft.chemistry.multicomponent_phase_diagram_validation_v1 import MulticomponentPhaseDiagramValidator
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/chemistry/multicomponent_phase_diagram_law_v1.py",
        root / "sft/chemistry/multicomponent_phase_diagram_batch_v1.py",
        root / "sft/chemistry/multicomponent_phase_diagram_validation_v1.py",
        root / "sft/chemistry/phase_rule_law_v1.py",
        root / "sft/chemistry/generated_law.py",
        root / "sft/chemistry/generated_observational_law.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "tools/capture_chemistry_multicomponent_phase_diagram_sources_v1.py",
        root / SPEC_PATH, root / RAW_PATH, root / LANDING_PATH, root / PRIMARY_PATH,
        root / IDENTITY_PATH, root / TARGET_PATH,
        root / "claims/SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-CHEM-MULTICOMPONENT-PHASE-DIAGRAM-013/independent_validator.py"
    return ClaimExecution(
        program=GeneratedObservationalChemistryProgram(MULTICOMPONENT_PHASE_DIAGRAM_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-chem-multicomponent-phase-diagram-013-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=MulticomponentPhaseDiagramValidator(root),
    )
