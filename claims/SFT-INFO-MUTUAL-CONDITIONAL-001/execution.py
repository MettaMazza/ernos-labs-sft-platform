"""Official execution binding for SFT-INFO-MUTUAL-CONDITIONAL-001."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.information_science.mutual_conditional_information.law import SPEC
from sft.information_science.generated_law import GeneratedInformationProgram
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/information_science/generated_law.py",
        root / "sft/information_science/mutual_conditional_information/law.py",
        root / "claims/SFT-INFO-MUTUAL-CONDITIONAL-001/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-INFO-MUTUAL-CONDITIONAL-001/independent_validator.py"
    return ClaimExecution(
        program=GeneratedInformationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-info-mutual-conditional-001-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
