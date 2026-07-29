"""Official execution bindings for the complete Smithium return family."""

from pathlib import Path
import sys

from sft.chemistry.smithium_return_external_v1 import BlindSmithiumExternalValidator
from sft.chemistry.smithium_return_laws_v1 import EMPIRICAL_ID, SPECS, StructuralChemistryProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    fixed = (
        root / "sft/chemistry/smithium_return_laws_v1.py",
        root / "sft/chemistry/smithium_return_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    if claim_id == EMPIRICAL_ID:
        fixed = fixed + (root / "sft/chemistry/smithium_return_external_v1.py",)
    dependency_files: list[Path] = []
    for dependency in spec.dependencies:
        package = root / "claims" / dependency
        dependency_files.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(dependency_files)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/chemistry/smithium_return_validator_v1.py"
    external = ExternalCommandValidator(
        "sft-chemistry-smithium-return-independent-python/1",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
    )
    empirical = BlindSmithiumExternalValidator(root) if claim_id == EMPIRICAL_ID else None
    return ClaimExecution(
        program=StructuralChemistryProgram(spec, source_hash),
        independent_validator=external,
        source_files=files,
        empirical_validator=empirical,
    )


__all__ = ("build_execution",)
