from pathlib import Path
from sft.materials.valid_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-VALIDATION-OPTICAL-PHOTONIC-VECTOR-008', Path(__file__).resolve())
