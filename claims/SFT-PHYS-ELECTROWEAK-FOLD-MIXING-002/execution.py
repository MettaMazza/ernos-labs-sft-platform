from pathlib import Path
from sft.physics.lineage_particle_execution_v1 import build_lineage_execution

def build_execution(root: Path):
    return build_lineage_execution(root, "SFT-PHYS-ELECTROWEAK-FOLD-MIXING-002", Path(__file__))
