"""Official execution binding for SFT-PHYS-MATTER-BARYON-PHOTON-003."""

from pathlib import Path
from sft.physics.matter_flavour_completion_execution_v1 import build_completion_execution


def build_execution(root: Path):
    return build_completion_execution(root, 'SFT-PHYS-MATTER-BARYON-PHOTON-003', Path(__file__))
