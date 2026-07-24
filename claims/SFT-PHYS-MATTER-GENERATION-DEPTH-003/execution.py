"""Official execution binding for SFT-PHYS-MATTER-GENERATION-DEPTH-003."""

from pathlib import Path
from sft.physics.matter_flavour_completion_execution_v2 import build_completion_execution_v2


def build_execution(root: Path):
    return build_completion_execution_v2(root, 'SFT-PHYS-MATTER-GENERATION-DEPTH-003', Path(__file__))
