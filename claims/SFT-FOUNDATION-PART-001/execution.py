"""Official execution factory for the exact positive part coordinate."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.part import PartProgram
from sft.verification import ClaimExecution


def build_execution(repository_root: Path) -> ClaimExecution:
    source_files = (
        repository_root / "sft" / "foundation" / "part.py",
        repository_root / "claims" / "SFT-FOUNDATION-PART-001" / "execution.py",
    )
    source_hash = build_source_manifest(repository_root, source_files).manifest_hash
    validator_file = (
        repository_root
        / "claims"
        / "SFT-FOUNDATION-PART-001"
        / "independent_validator.py"
    )
    return ClaimExecution(
        program=PartProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-positive-part-coordinate-independent-python/1",
            (sys.executable, str(validator_file)),
            validator_file.parent,
            (validator_file,),
        ),
        source_files=source_files,
    )
