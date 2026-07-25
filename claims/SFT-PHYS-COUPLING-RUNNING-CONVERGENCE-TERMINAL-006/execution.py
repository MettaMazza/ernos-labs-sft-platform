"""Official execution binding for terminal coupling-running laws."""

from pathlib import Path

from sft.physics.coupling_running_convergence_terminal_execution_v1 import (
    build_coupling_running_convergence_execution,
)


def build_execution(root: Path):
    return build_coupling_running_convergence_execution(root, Path(__file__))
