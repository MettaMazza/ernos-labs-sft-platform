"""Official execution binding for SFT-PHYS-SPACETIME-CLOSED-TIMELIKE-ADMISSIBILITY-003."""

from pathlib import Path
from sft.physics.gravity_spacetime_execution_v1 import build_gravity_spacetime_execution


def build_execution(root: Path):
    return build_gravity_spacetime_execution(root, 'SFT-PHYS-SPACETIME-CLOSED-TIMELIKE-ADMISSIBILITY-003', Path(__file__))
