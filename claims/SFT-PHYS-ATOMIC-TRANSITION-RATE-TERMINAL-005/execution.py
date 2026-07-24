"""Official execution binding for SFT-PHYS-ATOMIC-TRANSITION-RATE-TERMINAL-005."""

from pathlib import Path

from sft.physics.atomic_transition_rate_successor_execution_v1 import build_atomic_transition_rate_execution


def build_execution(root: Path):
    return build_atomic_transition_rate_execution(root, Path(__file__))
