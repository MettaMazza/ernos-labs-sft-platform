from pathlib import Path
from sft.physics.lineage_particle_execution_v1 import build_lineage_execution

def build_execution(root: Path):
    return build_lineage_execution(root, "SFT-PHYS-WEAK-PARITY-FIBRE-002", Path(__file__))
