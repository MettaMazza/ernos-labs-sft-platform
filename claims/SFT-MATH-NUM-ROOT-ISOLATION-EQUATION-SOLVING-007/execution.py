from pathlib import Path
from sft.mathematics.num_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-NUM-ROOT-ISOLATION-EQUATION-SOLVING-007', Path(__file__).resolve())
