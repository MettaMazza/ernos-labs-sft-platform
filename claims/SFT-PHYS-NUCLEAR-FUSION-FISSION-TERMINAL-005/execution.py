"""Official execution binding for terminal fusion/fission forcing."""

from pathlib import Path

from sft.physics.fusion_fission_terminal_execution_v1 import (
    build_fusion_fission_terminal_execution,
)


def build_execution(root: Path):
    return build_fusion_fission_terminal_execution(root, Path(__file__))
