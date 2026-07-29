from pathlib import Path
from sft.materials.micro_001_009_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-MICRO-DISLOCATION-REACTION-003', Path(__file__).resolve())
