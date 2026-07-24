"""Official execution binding for SFT-PHYS-MOLECULAR-SPECTROSCOPY-TERMINAL-005."""

from pathlib import Path

from sft.physics.molecular_spectroscopy_successor_execution_v1 import (
    build_molecular_spectroscopy_execution,
)


def build_execution(root: Path):
    return build_molecular_spectroscopy_execution(root, Path(__file__))
