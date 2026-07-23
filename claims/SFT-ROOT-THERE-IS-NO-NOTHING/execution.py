"""Official execution factory for the premise-free v3 root theorem."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.root_theorem import RootTheoremProgram
from sft.verification import ClaimExecution


def build_execution(repository_root: Path) -> ClaimExecution:
    source_files = (
        repository_root / "sft" / "foundation" / "root_theorem.py",
        repository_root / "claims" / "SFT-ROOT-THERE-IS-NO-NOTHING" / "execution.py",
    )
    source_hash = build_source_manifest(repository_root, source_files).manifest_hash
    validator_file = (
        repository_root
        / "claims"
        / "SFT-ROOT-THERE-IS-NO-NOTHING"
        / "independent_validator.py"
    )
    validator = ExternalCommandValidator(
        validator_id="sft-root-independent-python/1",
        command=(sys.executable, str(validator_file)),
        implementation_root=validator_file.parent,
        implementation_files=(validator_file,),
    )
    return ClaimExecution(
        program=RootTheoremProgram(source_hash),
        independent_validator=validator,
        source_files=source_files,
    )
