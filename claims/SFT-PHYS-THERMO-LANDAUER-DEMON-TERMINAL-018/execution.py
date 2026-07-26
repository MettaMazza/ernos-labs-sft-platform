"""Claim-local execution binding."""

from pathlib import Path

from sft.physics.landauer_demon_ledger_terminal_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__))
