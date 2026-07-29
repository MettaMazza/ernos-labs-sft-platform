"""Versioned execution builder after the preserved V1 validator-interface halt."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.tesla_resonance_family_law_v1 import SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    fixed = (
        root / "sft/physics/tesla_resonance_family_law_v1.py",
        root / "sft/physics/tesla_resonance_family_execution_v2.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    evidence = []
    for dependency in spec.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/tesla_resonance_family_validator_v2.py"
    return ClaimExecution(
        StructuralPhysicsProgram(spec, source_hash),
        ExternalCommandValidator(
            "sft-physics-tesla-resonance-family-independent-python/2",
            (sys.executable, str(validator), claim_id, str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
