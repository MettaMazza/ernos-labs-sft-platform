"""Official execution bindings for the complete Biology return family."""

from pathlib import Path
import sys

from sft.biology.prior_mechanisms_external_v1 import BlindPriorMechanismsExternalValidator
from sft.biology.prior_mechanisms_laws_v1 import EMPIRICAL_ID, SPECS, StructuralBiologyProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    fixed = (
        root / "sft/biology/prior_mechanisms_laws_v1.py",
        root / "sft/biology/prior_mechanisms_execution_v1.py",
        root / "sft/physics/structural_constants.py",
        execution_file,
    )
    if claim_id == EMPIRICAL_ID:
        fixed += (
            root / "sft/biology/prior_mechanisms_external_v1.py",
            root / "sft/biology/sources.py",
        )
    dependency_files: list[Path] = []
    for dependency in spec.dependencies:
        package = root / "claims" / dependency
        dependency_files.extend((package / "registration.json", package / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + tuple(dependency_files)))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/biology/prior_mechanisms_validator_v1.py"
    external = ExternalCommandValidator(
        "sft-biology-prior-mechanisms-independent-python/1",
        (sys.executable, str(validator), claim_id, str(root)),
        validator.parent,
        (validator,),
    )
    empirical = BlindPriorMechanismsExternalValidator(root) if claim_id == EMPIRICAL_ID else None
    return ClaimExecution(
        program=StructuralBiologyProgram(spec, source_hash),
        independent_validator=external,
        source_files=files,
        empirical_validator=empirical,
    )


__all__ = ("build_execution",)
