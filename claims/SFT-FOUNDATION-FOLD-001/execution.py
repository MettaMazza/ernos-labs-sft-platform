"""Official execution factory for the minimal structural Fold."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.fold import FoldProgram
from sft.verification import ClaimExecution


def build_execution(repository_root: Path) -> ClaimExecution:
    source_files = (
        repository_root / "sft" / "foundation" / "fold.py",
        repository_root / "claims" / "SFT-FOUNDATION-FOLD-001" / "execution.py",
    )
    source_hash = build_source_manifest(repository_root, source_files).manifest_hash
    validator_file = (
        repository_root
        / "claims"
        / "SFT-FOUNDATION-FOLD-001"
        / "independent_validator.py"
    )
    return ClaimExecution(
        program=FoldProgram(source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-minimal-fold-independent-python/1",
            (sys.executable, str(validator_file)),
            validator_file.parent,
            (validator_file,),
        ),
        source_files=source_files,
    )
