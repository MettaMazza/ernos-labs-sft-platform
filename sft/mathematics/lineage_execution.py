"""Official and implementation-distinct bindings for lineage Mathematics laws."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.mathematics.lineage_laws import BY_CLAIM_ID
from sft.verification import ClaimExecution


def build_lineage_execution(root: Path, claim_id: str, execution_file: Path, validator_file: Path) -> ClaimExecution:
    spec = BY_CLAIM_ID[claim_id]
    source_files = (
        root / "sft/mathematics/generated_law.py",
        root / "sft/mathematics/lineage_laws.py",
        root / "sft/mathematics/lineage_execution.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    generic_validator = root / "tools/validate_mathematics_lineage_claim.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(spec, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-mathematics-lineage-independent-python/1/" + claim_id,
            (sys.executable, str(generic_validator), claim_id),
            root,
            (generic_validator, validator_file),
        ),
        source_files=source_files,
    )
