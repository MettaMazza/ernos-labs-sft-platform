"""Claim-package binding for complete calculator 006."""

from pathlib import Path

from sft.mathematics.calculator_complete.execution import build_calculator_execution


def build_execution(root: Path):
    return build_calculator_execution(root, Path(__file__).resolve())
