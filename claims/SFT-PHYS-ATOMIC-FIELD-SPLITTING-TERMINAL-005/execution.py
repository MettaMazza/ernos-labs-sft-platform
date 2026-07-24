"""Official execution binding for SFT-PHYS-ATOMIC-FIELD-SPLITTING-TERMINAL-005."""

from pathlib import Path

from sft.physics.atomic_field_splitting_successor_execution_v1 import build_atomic_field_splitting_execution


def build_execution(root: Path):
    return build_atomic_field_splitting_execution(root, Path(__file__))
