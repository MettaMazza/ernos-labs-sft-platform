"""Official execution binding for SFT-PHYS-VALIDATION-OPTICAL-OPERATIONS-003."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.physics.relativistic_field_validation_v1 import VALIDATION_SPECS, VALIDATOR_BY_ID
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in VALIDATION_SPECS if item.claim_id == 'SFT-PHYS-VALIDATION-OPTICAL-OPERATIONS-003')
    source_files = (
        root / "sft/physics/structural_constants.py",
        root / "sft/physics/vacuum_lineage_laws_v1.py",
        root / "sft/physics/relativistic_field_laws_v1.py",
        root / "sft/physics/relativistic_field_validation_v1.py",
        root / "sft/physics/generated_empirical_law.py",
        root / "claims/SFT-PHYS-VALIDATION-OPTICAL-OPERATIONS-003/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-VALIDATION-OPTICAL-OPERATIONS-003/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-phys-validation-optical-operations-003' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=VALIDATOR_BY_ID[spec.claim_id](root),
    )
