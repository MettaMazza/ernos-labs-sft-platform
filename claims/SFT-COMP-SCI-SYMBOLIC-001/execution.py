"""Official execution binding for SFT-COMP-SCI-SYMBOLIC-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.computation.generated_law import GeneratedComputationProgram
from sft.computation.scientific_computation.symbolic.law import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/computation/generated_law.py",
        root / "sft/computation/operations.py",
        root / "sft/computation/spec_data.py",
        root / "sft/computation/catalog.py",
        root / "sft/computation/scientific_computation/symbolic/law.py",
        root / "claims/SFT-COMP-SCI-SYMBOLIC-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-COMP-SCI-SYMBOLIC-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-comp-sci-symbolic-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
