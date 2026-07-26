"""Claim-local execution binding."""

from pathlib import Path

from sft.physics.yang_mills_singlet_gap_empirical_execution_v1 import build_execution as _build


def build_execution(root: Path):
    return _build(root, Path(__file__))
