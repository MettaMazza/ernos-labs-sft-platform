from pathlib import Path
from sft.materials.valid_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-VALIDATION-MAGNETIC-SUPERCONDUCTING-TOPOLOGICAL-VECTOR-007', Path(__file__).resolve())
