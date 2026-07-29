from pathlib import Path
from sft.mathematics.anal_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ANAL-ORTHOGONAL-BASIS-EXPANSION-012', Path(__file__).resolve())
