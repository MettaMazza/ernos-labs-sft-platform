"""Official execution binding for SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002."""

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.computation.generated_law import GeneratedComputationProgram
from sft.computation.complexity.fold_p_np_equality.law import SPEC
from sft.verification import ClaimExecution


def build_execution(root: Path) -> ClaimExecution:
    source_files = (
        root / "sft/computation/generated_law.py",
        root / "sft/computation/lineage_laws.py",
        root / "sft/computation/complexity/fold_p_np_equality/law.py",
        root / "claims/SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002/execution.py",
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "claims/SFT-COMP-CPLX-FOLD-P-NP-EQUALITY-002/independent_validator.py"
    return ClaimExecution(
        program=GeneratedComputationProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-comp-cplx-fold-p-np-equality-002-independent-python/1",
            (sys.executable, str(validator)),
            validator.parent,
            (validator,),
        ),
        source_files=source_files,
    )
