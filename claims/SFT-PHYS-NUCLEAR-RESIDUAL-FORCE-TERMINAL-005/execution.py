"""Official execution binding for SFT-PHYS-NUCLEAR-RESIDUAL-FORCE-TERMINAL-005."""

from pathlib import Path

from sft.physics.nuclear_residual_force_successor_execution_v1 import build_nuclear_residual_force_execution


def build_execution(root: Path):
    return build_nuclear_residual_force_execution(root, Path(__file__))
