"""Official execution binding for odd-lattice all-region occupancy."""

from pathlib import Path

from sft.physics.odd_lattice_all_region_terminal_execution_v1 import build_odd_lattice_all_region_execution


def build_execution(root: Path):
    return build_odd_lattice_all_region_execution(root, Path(__file__))
