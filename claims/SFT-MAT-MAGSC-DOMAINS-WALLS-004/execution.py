from pathlib import Path
from sft.materials.magsc_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-MAGSC-DOMAINS-WALLS-004', Path(__file__).resolve())
