from pathlib import Path
from sft.mathematics.linear_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-LINEAR-OPERATOR-DECOMPOSITION-014', Path(__file__).resolve())
