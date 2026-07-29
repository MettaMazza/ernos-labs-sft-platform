from pathlib import Path
from sft.materials.crys_001_008_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-CRYS-PAIR-DISTRIBUTION-008', Path(__file__).resolve())
