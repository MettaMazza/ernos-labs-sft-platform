"""Official execution binding for SFT-PHYS-MATTER-CKM-FIBRE-003."""

from pathlib import Path
from sft.physics.matter_flavour_execution_v1 import build_matter_flavour_execution


def build_execution(root: Path):
    return build_matter_flavour_execution(root, 'SFT-PHYS-MATTER-CKM-FIBRE-003', Path(__file__))
