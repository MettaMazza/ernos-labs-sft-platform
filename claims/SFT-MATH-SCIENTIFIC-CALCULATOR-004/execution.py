"""Claim-local corrected calculator execution binding."""

from pathlib import Path

from sft.mathematics.calculator.execution_v2 import build_calculator_execution


def build_execution(root: Path):
    return build_calculator_execution(root, Path(__file__))
