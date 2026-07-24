"""Official execution binding for SFT-PHYS-ATOMIC-SHELL-PERIODICITY-TERMINAL-005."""

from pathlib import Path

from sft.physics.atomic_shell_periodicity_successor_execution_v1 import build_atomic_shell_periodicity_execution


def build_execution(root: Path):
    return build_atomic_shell_periodicity_execution(root, Path(__file__))
