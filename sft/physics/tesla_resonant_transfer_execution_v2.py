"""Exact execution for the dependency-identity-corrected 081 claim."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.tesla_resonant_transfer_law_v2 import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    fixed = (
        root / "sft/physics/tesla_resonance_family_law_v1.py",
        root / "sft/physics/tesla_resonant_transfer_law_v2.py",
        root / "sft/physics/tesla_resonant_transfer_execution_v2.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    evidence = []
    for dependency in SPEC.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/tesla_resonant_transfer_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-physics-tesla-resonant-transfer-independent-python/1",
            (sys.executable, str(validator), SPEC.claim_id, str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
