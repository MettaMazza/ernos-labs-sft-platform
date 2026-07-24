"""Official execution binding for SFT-PHYS-ATOMIC-HYPERFINE-TERMINAL-005."""

from pathlib import Path

from sft.physics.atomic_precision_successor_execution_v1 import build_atomic_precision_execution


def build_execution(root: Path):
    return build_atomic_precision_execution(root, "SFT-PHYS-ATOMIC-HYPERFINE-TERMINAL-005", Path(__file__))
