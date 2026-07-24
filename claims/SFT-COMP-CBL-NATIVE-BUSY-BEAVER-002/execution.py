"""Official execution binding for SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.computation.generated_law import GeneratedComputationProgram
from sft.computation.computability.native_busy_beaver.law import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/computation/generated_law.py",
        root / "sft/computation/lineage_laws.py",
        root / "sft/computation/computability/native_busy_beaver/law.py",
        root / "claims/SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-COMP-CBL-NATIVE-BUSY-BEAVER-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-comp-cbl-native-busy-beaver-002-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
