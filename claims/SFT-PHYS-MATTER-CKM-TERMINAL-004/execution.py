"""Official execution binding for SFT-PHYS-MATTER-CKM-TERMINAL-004."""

from pathlib import Path
from sft.physics.matter_flavour_terminal_ckm_execution_v1 import build_terminal_execution


def build_execution(root: Path):
    return build_terminal_execution(root, 'SFT-PHYS-MATTER-CKM-TERMINAL-004', Path(__file__))
