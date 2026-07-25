"""Official execution binding for terminal scattering laws."""

from pathlib import Path

from sft.physics.scattering_rutherford_compton_terminal_execution_v1 import (
    build_scattering_rutherford_compton_execution,
)


def build_execution(root: Path):
    return build_scattering_rutherford_compton_execution(root, Path(__file__))
