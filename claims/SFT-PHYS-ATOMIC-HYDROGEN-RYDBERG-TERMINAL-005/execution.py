"""Official execution binding for SFT-PHYS-ATOMIC-HYDROGEN-RYDBERG-TERMINAL-005."""

from pathlib import Path

from sft.physics.hydrogen_rydberg_successor_execution_v1 import build_hydrogen_rydberg_execution


def build_execution(root: Path):
    return build_hydrogen_rydberg_execution(root, Path(__file__))
