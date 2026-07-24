"""Official execution binding for terminal proton/electron precision."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_proton_execution_v1 import build_terminal_proton_execution


def build_execution(root: Path):
    return build_terminal_proton_execution(root, Path(__file__))
