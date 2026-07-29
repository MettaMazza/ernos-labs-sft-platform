from pathlib import Path
from sft.mathematics.arith_001_018_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ARITH-JUNCTION-ADDITION-002', Path(__file__).resolve())
