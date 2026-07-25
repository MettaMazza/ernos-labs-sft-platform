from pathlib import Path

from sft.physics.quadrupole_radiated_power_terminal_execution_v1 import (
    build_quadrupole_radiated_power_execution,
)


def build_execution(root: Path):
    return build_quadrupole_radiated_power_execution(root, Path(__file__))
