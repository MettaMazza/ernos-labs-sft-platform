"""Official execution binding for SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.atomic_constants_validation import VALIDATION_SPECS, VALIDATOR_BY_ID
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    spec = next(item for item in VALIDATION_SPECS if item.claim_id == 'SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001')
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/atomic_constants.py",
        root / "sft/physics/atomic_constants_validation.py",
        root / "claims/SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-PHYS-VALIDATION-NUCLEAR-CLOSURES-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            'sft-phys-validation-nuclear-closures-001' + "-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
        empirical_validator=VALIDATOR_BY_ID[spec.claim_id](root),
    )
