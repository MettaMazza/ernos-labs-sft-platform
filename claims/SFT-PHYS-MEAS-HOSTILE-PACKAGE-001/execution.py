"""Official execution binding for SFT-PHYS-MEAS-HOSTILE-PACKAGE-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.formal_law import FormalPrerequisiteProgram
from sft.physics.measurement_prerequisites import PREREQUISITE_SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in PREREQUISITE_SPECS if item.claim_id == 'SFT-PHYS-MEAS-HOSTILE-PACKAGE-001')
    source_files = (
        root / "sft/physics/formal_law.py",
        root / "sft/physics/measurement_prerequisites.py",
        root / "claims/SFT-PHYS-MEAS-HOSTILE-PACKAGE-001/execution.py",
        root / 'sft/engine/hostile.py',
        root / 'sft/engine/fold_language.py',
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-MEAS-HOSTILE-PACKAGE-001/independent_validator.py"
    return ClaimExecution(
        program=FormalPrerequisiteProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-phys-meas-hostile-package-001-independent-python/1',
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
