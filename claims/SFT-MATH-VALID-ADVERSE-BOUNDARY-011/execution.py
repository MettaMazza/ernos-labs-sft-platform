from pathlib import Path
from sft.mathematics.valid_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-VALID-ADVERSE-BOUNDARY-011', Path(__file__).resolve())
