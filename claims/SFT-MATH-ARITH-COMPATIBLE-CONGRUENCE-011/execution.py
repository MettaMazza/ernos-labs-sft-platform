from pathlib import Path
from sft.mathematics.arith_001_018_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ARITH-COMPATIBLE-CONGRUENCE-011', Path(__file__).resolve())
