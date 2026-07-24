"""Official execution binding for SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003."""

from pathlib import Path
from sft.physics.vacuum_lineage_execution_v1 import build_vacuum_lineage_execution


def build_execution(root: Path):
    return build_vacuum_lineage_execution(root, 'SFT-PHYS-VACUUM-POLARIZATION-RUNNING-003', Path(__file__))
