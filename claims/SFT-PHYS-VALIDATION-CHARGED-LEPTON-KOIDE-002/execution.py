"""Official execution binding for the versioned exact Koide measurement validation."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.charged_lepton_validation import KOIDE_VALIDATION_SPEC, KoideValidationExternalValidator
from sft.physics.generated_empirical_law import GeneratedEmpiricalPhysicsProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    claim_id = KOIDE_VALIDATION_SPEC.claim_id
    source_files = (
        root / "sft/physics/generated_empirical_law.py",
        root / "sft/physics/measured_value.py",
        root / "sft/physics/prior_value_laws.py",
        root / "sft/physics/terminal_lepton_law.py",
        root / "sft/physics/charged_lepton_validation.py",
        root / f"claims/{claim_id}/execution.py",
        root / "sft/claim_evidence/fold_language.py",
        root / "sft/claim_evidence/custody.py",
        root / "sft/claim_evidence/hostile.py",
        root / "sft/engine/isolation.py",
        root / "sft/engine/empirical.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / f"claims/{claim_id}/independent_validator.py"
    return ClaimExecution(
        program=GeneratedEmpiricalPhysicsProgram(KOIDE_VALIDATION_SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-phys-validation-charged-lepton-koide-002-independent-python/1",
            (sys.executable, str(validator)), validator.parent, (validator,),
        ),
        source_files=source_files,
        empirical_validator=KoideValidationExternalValidator(root),
    )
