"""Official execution factory for cross-partition part equivalence."""
from pathlib import Path
import sys
from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.foundation.part_equivalence import PartEquivalenceProgram
from sft.verification import ClaimExecution

def build_execution(repository_root: Path) -> ClaimExecution:
    source_files = (repository_root / "sft/foundation/part_equivalence.py", repository_root / "claims/SFT-FOUNDATION-PART-EQUIVALENCE-001/execution.py")
    source_hash = build_source_manifest(repository_root, source_files).manifest_hash
    validator = repository_root / "claims/SFT-FOUNDATION-PART-EQUIVALENCE-001/independent_validator.py"
    return ClaimExecution(PartEquivalenceProgram(source_hash), ExternalCommandValidator(
        "sft-part-equivalence-independent-python/1", (sys.executable, str(validator)),
        validator.parent, (validator,)), source_files)
