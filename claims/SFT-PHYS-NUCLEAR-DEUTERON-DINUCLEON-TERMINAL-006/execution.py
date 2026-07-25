"""Official execution binding for terminal deuteron and dinucleon closure."""

from pathlib import Path

from sft.physics.deuteron_dinucleon_terminal_execution_v1 import (
    build_deuteron_dinucleon_execution,
)


def build_execution(root: Path):
    return build_deuteron_dinucleon_execution(root, Path(__file__))
