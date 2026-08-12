"""Execution builder for the recurrence-cycle engineering protocol."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.engineering.novel_translation_laws_v1 import EngineeringProtocolProgram
from sft.engineering.vacuum_recurrence_cycle_protocol_v1 import CLAIM_ID, SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path, execution_file: Path) -> ClaimExecution:
    preregistration = execution_file.parent / "preregistration.json"
    fixed = (
        root / "sft/engineering/vacuum_recurrence_cycle_protocol_v1.py",
        root / "sft/engineering/vacuum_recurrence_cycle_execution_v1.py",
        root / "sft/engineering/novel_translation_laws_v1.py",
        root / "sft/physics/structural_constants.py",
        preregistration,
        execution_file,
    )
    evidence = []
    for dependency in SPEC.dependencies:
        package = root / "claims" / dependency
        evidence.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(evidence)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/engineering/vacuum_recurrence_cycle_protocol_validator_v1.py"
    return ClaimExecution(
        EngineeringProtocolProgram(SPEC, source_hash),
        ExternalCommandValidator(
            "sft-engineering-vacuum-recurrence-cycle-protocol-independent-python/1",
            (sys.executable, str(validator), CLAIM_ID, str(root)),
            validator.parent,
            (validator,),
        ),
        files,
    )


__all__ = ("build_execution",)
