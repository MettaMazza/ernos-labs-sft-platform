from pathlib import Path
from sft.materials.class_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-CLASS-FIBRE-REINFORCED-006', Path(__file__).resolve())
