"""Official frozen-engine binding for expanded calculator claim 005."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution

from .law_v3 import SPEC


def build_calculator_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = tuple(
        root / relative
        for relative in (
            "sft/mathematics/generated_law.py",
            "sft/mathematics/calculator/values.py",
            "sft/mathematics/calculator/operations.py",
            "sft/mathematics/calculator/machine.py",
            "sft/mathematics/calculator/law.py",
            "sft/mathematics/calculator/operations_v2.py",
            "sft/mathematics/calculator/machine_v2.py",
            "sft/mathematics/calculator/law_v2.py",
            "sft/mathematics/calculator/operations_v3.py",
            "sft/mathematics/calculator/machine_v3.py",
            "sft/mathematics/calculator/session.py",
            "sft/mathematics/calculator/gui.py",
            "sft/mathematics/calculator/law_v3.py",
            "sft/mathematics/calculator/execution_v3.py",
            "sft/mathematics/calculator/__init__.py",
            "sft/mathematics/calculator/__main__.py",
            "sft/mathematics/calculator/README.md",
        )
    ) + (execution_file,)
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/mathematics/scientific_calculator_validator_v3.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-math-scientific-calculator-independent-python/3",
            (sys.executable, str(validator), SPEC.claim_id),
            root,
            (validator,),
        ),
        source_files=source_files,
    )
