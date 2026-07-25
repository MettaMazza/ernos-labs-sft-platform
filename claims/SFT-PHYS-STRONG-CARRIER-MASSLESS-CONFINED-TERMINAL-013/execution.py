from pathlib import Path

from sft.physics.strong_carrier_massless_confined_terminal_execution_v1 import (
    build_strong_carrier_massless_confined_execution,
)


def build_execution(root: Path):
    return build_strong_carrier_massless_confined_execution(root, Path(__file__))
