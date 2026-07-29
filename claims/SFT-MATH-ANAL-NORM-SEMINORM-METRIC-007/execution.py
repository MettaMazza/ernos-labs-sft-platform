from pathlib import Path
from sft.mathematics.anal_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ANAL-NORM-SEMINORM-METRIC-007', Path(__file__).resolve())
