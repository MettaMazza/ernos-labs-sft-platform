from pathlib import Path
from sft.mathematics.prob_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-PROB-VARIANCE-DISPERSION-005', Path(__file__).resolve())
