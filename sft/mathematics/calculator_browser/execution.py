"""Official frozen-engine binding for calculator browser claim 007."""

from __future__ import annotations

from pathlib import Path
import sys

from sft.engine import ExternalCommandValidator
from sft.engine.source import build_source_manifest
from sft.mathematics.generated_law import GeneratedMathematicsProgram
from sft.verification import ClaimExecution

from .law import SPEC


def build_calculator_browser_execution(root: Path, execution_file: Path) -> ClaimExecution:
    source_files = tuple(
        root / relative
        for relative in (
            "sft/mathematics/generated_law.py",
            "sft/mathematics/calculator_browser/__init__.py",
            "sft/mathematics/calculator_browser/__main__.py",
            "sft/mathematics/calculator_browser/app.py",
            "sft/mathematics/calculator_browser/native.py",
            "sft/mathematics/calculator_browser/page.py",
            "sft/mathematics/calculator_browser/law.py",
            "sft/mathematics/calculator_browser/execution.py",
            "tests/test_mathematics_calculator_browser.py",
            "generated/mathematics/scientific_calculator_browser_coverage_v1.json",
            "calculator_launchers/Launch Smithian Fold Calculator.command",
            "calculator_launchers/Launch Smithian Fold Calculator.bat",
            "calculator_launchers/launch-smithian-fold-calculator.sh",
        )
    ) + (execution_file,)
    source_hash = build_source_manifest(root, source_files).manifest_hash
    validator = root / "generated/mathematics/scientific_calculator_browser_validator_v1.py"
    return ClaimExecution(
        program=GeneratedMathematicsProgram(SPEC, source_hash),
        independent_validator=ExternalCommandValidator(
            "sft-math-scientific-calculator-browser-independent-python/1",
            (sys.executable, str(validator), SPEC.claim_id),
            root,
            (validator,),
        ),
        source_files=source_files,
    )


__all__ = ("build_calculator_browser_execution",)
