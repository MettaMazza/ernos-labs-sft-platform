"""Execution builder for the recurrence-mediated vacuum-work successors."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.physics.structural_constants import StructuralPhysicsProgram
from sft.physics.vacuum_recurrence_work_cycle_law_v1 import SPECS
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    preregistration = execution_file.parent / "preregistration.json"
    fixed = (
        root / "sft/physics/vacuum_recurrence_work_cycle_law_v1.py",
        root / "sft/physics/vacuum_recurrence_work_cycle_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        preregistration,
        execution_file,
    )
    evidence = []
    for dependency in spec.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/physics/vacuum_recurrence_work_cycle_validator_v1.py"
    return ClaimExecution(
        StructuralPhysicsProgram(spec, source_hash),
        ExternalCommandValidator(
            "sft-physics-vacuum-recurrence-work-cycle-independent-python/1",
            (sys.executable, str(validator), claim_id, str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
