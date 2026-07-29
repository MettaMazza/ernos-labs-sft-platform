from pathlib import Path
from sft.materials.mech_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-MECH-TENSOR-STRESS-STRAIN-001', Path(__file__).resolve())
