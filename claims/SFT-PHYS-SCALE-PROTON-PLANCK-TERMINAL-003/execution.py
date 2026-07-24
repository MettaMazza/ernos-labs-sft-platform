"""Official execution binding for SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003."""

from pathlib import Path
from sft.physics.precision_value_execution_v1 import build_precision_execution


def build_execution(root: Path):
    return build_precision_execution(root, 'SFT-PHYS-SCALE-PROTON-PLANCK-TERMINAL-003', Path(__file__))
