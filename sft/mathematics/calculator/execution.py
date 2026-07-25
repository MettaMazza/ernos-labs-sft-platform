"""Official frozen-engine binding for the SFT scientific calculator law."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution

from .law import SPEC


def build_calculator_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = (
        root / "sft/mathematics/generated_law.py",
        root / "sft/mathematics/calculator/values.py",
        root / "sft/mathematics/calculator/operations.py",
        root / "sft/mathematics/calculator/machine.py",
        root / "sft/mathematics/calculator/law.py",
        root / "sft/mathematics/calculator/execution.py",
        execution_file,
    )
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/mathematics/scientific_calculator_validator_v1.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-math-scientific-calculator-independent-python/1",
            (sys.executable, str(validator), SPEC.claim_id),
            root,
            (validator,),
        ),
        source_files=source_files,
    )
