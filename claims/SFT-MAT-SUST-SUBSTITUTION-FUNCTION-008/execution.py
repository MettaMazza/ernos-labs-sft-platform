from pathlib import Path
from sft.materials.sust_001_009_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-SUST-SUBSTITUTION-FUNCTION-008', Path(__file__).resolve())
