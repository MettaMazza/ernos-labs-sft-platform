from pathlib import Path
from sft.mathematics.num_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-NUM-TRUNCATION-DISCRETIZATION-ERROR-003', Path(__file__).resolve())
