"""Official execution binding for SFT-PHYS-HADRON-REGGE-TERMINAL-005."""

from pathlib import Path

from sft.physics.hadron_regge_successor_execution_v1 import build_hadron_regge_execution


def build_execution(root: Path):
    return build_hadron_regge_execution(root, Path(__file__))
