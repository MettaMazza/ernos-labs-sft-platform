from pathlib import Path

from sft.physics.strong_field_nonlinear_fixed_point_terminal_execution_v1 import (
    build_strong_field_nonlinear_fixed_point_execution,
)


def build_execution(root: Path):
    return build_strong_field_nonlinear_fixed_point_execution(root, Path(__file__))
