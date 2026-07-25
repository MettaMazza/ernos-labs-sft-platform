"""Official execution binding for terminal decay-width laws."""

from pathlib import Path

from sft.physics.decay_width_branching_lifetime_terminal_execution_v1 import (
    build_decay_width_branching_lifetime_execution,
)


def build_execution(root: Path):
    return build_decay_width_branching_lifetime_execution(root, Path(__file__))
