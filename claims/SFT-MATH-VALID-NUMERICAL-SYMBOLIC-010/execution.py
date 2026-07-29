from pathlib import Path
from sft.mathematics.valid_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-VALID-NUMERICAL-SYMBOLIC-010', Path(__file__).resolve())
