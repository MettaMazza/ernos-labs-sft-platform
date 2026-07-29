from pathlib import Path
from sft.materials.surf_001_008_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-SURF-ADHESION-SEPARATION-003', Path(__file__).resolve())
