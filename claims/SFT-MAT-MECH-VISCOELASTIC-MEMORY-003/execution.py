from pathlib import Path
from sft.materials.mech_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-MECH-VISCOELASTIC-MEMORY-003', Path(__file__).resolve())
