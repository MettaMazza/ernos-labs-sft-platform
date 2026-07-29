from pathlib import Path
from sft.materials.comp_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-COMP-DATA-REPRESENTATION-001', Path(__file__).resolve())
