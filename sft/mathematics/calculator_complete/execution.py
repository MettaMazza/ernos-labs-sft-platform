"""Official frozen-engine binding for complete calculator claim 006."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution

from .law import SPEC


def build_calculator_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = tuple(
        root / relative
        for relative in (
            "sft/mathematics/generated_law.py",
            "sft/mathematics/catalog.py",
            "sft/mathematics/calculator/values.py",
            "sft/mathematics/calculator/operations.py",
            "sft/mathematics/calculator/operations_v2.py",
            "sft/mathematics/calculator/operations_v3.py",
            "sft/mathematics/calculator/machine.py",
            "sft/mathematics/calculator/machine_v2.py",
            "sft/mathematics/calculator/machine_v3.py",
            "sft/mathematics/calculator_complete/__init__.py",
            "sft/mathematics/calculator_complete/__main__.py",
            "sft/mathematics/calculator_complete/controller.py",
            "sft/mathematics/calculator_complete/evidence.py",
            "sft/mathematics/calculator_complete/explorer.py",
            "sft/mathematics/calculator_complete/expression_census.py",
            "sft/mathematics/calculator_complete/gui.py",
            "sft/mathematics/calculator_complete/law.py",
            "sft/mathematics/calculator_complete/machine.py",
            "sft/mathematics/calculator_complete/operations.py",
            "sft/mathematics/calculator_complete/presentation.py",
            "sft/mathematics/calculator_complete/session.py",
            "sft/mathematics/calculator_complete/execution.py",
            "sft/mathematics/calculator_complete/README.md",
            "tests/test_mathematics_scientific_calculator.py",
            "tests/test_mathematics_scientific_calculator_app.py",
            "tests/test_mathematics_calculator_complete.py",
            "tests/test_mathematics_calculator_complete_edges.py",
            "tests/test_mathematics_calculator_kernel_exhaustive.py",
            "tools/validate_mathematics_calculator.py",
            "generated/mathematics/scientific_calculator_coverage_v4.json",
            "launchers/Launch Smithian Calculator.command",
            "launchers/Launch Smithian Calculator.bat",
            "launchers/launch-smithian-calculator.sh",
            "pyproject.toml",
        )
    ) + (execution_file,)
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/mathematics/scientific_calculator_validator_v4.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-math-scientific-calculator-independent-python/4",
            (sys.executable, str(validator), SPEC.claim_id),
            root,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_calculator_execution",)
