from pathlib import Path
from sft.materials.elec_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-ELEC-ELECTROCHEMICAL-INSERTION-012', Path(__file__).resolve())
