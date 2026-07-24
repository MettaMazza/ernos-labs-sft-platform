"""Official execution binding for SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004."""

from pathlib import Path
from sft.physics.atomic_spectra_completion_execution_v1 import build_atomic_spectra_execution


def build_execution(root: Path):
    return build_atomic_spectra_execution(root, 'SFT-PHYS-ATOMIC-HYDROGEN-SPECTRUM-004', Path(__file__))
