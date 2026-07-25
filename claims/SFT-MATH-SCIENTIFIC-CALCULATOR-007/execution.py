"""Claim-package binding for calculator browser claim 007."""

from pathlib import Path

from sft.mathematics.calculator_browser.execution import build_calculator_browser_execution


def build_execution(root: Path):
    return build_calculator_browser_execution(root, Path(__file__).resolve())
