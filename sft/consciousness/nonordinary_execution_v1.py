"""Execution binding for the Consciousness return family."""

from pathlib import Path
import sys

from sft.consciousness.nonordinary_laws_v1 import EMPIRICAL_ID, SPECS, StructuralConsciousnessProgram
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.verification import ClaimExecution


def build_execution(root: Path, claim_id: str, execution_file: Path) -> ClaimExecution:
    spec = SPECS[claim_id]
    fixed = (root / "sft/consciousness/nonordinary_laws_v1.py", root / "sft/consciousness/nonordinary_execution_v1.py", root / "sft/physics/structural_constants.py", execution_file)
    empirical = None
    if claim_id == EMPIRICAL_ID:
        from sft.consciousness.nonordinary_external_v1 import BlindConsciousnessReturnExternalValidator
        fixed += (root / "sft/consciousness/nonordinary_external_v1.py",)
        empirical = BlindConsciousnessReturnExternalValidator(root)
    dependency_files = tuple(path for dep in spec.dependencies for path in (root / "claims" / dep / "registration.json", root / "claims" / dep / "certificate.json"))
    files = tuple(dict.fromkeys(fixed + dependency_files))
    source_hash = build_source_manifest(root, files).manifest_hash
    validator = root / "generated/consciousness/nonordinary_validator_v1.py"
    independent = ExternalCommandValidator("sft-consciousness-nonordinary-independent-python/1", (sys.executable, str(validator), claim_id, str(root)), validator.parent, (validator,))
    return ClaimExecution(program=StructuralConsciousnessProgram(spec, source_hash), independent_validator=independent, source_files=files, empirical_validator=empirical)


__all__ = ("build_execution",)
