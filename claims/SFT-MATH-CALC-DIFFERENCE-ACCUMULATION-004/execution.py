from pathlib import Path
from sft.mathematics.calc_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-CALC-DIFFERENCE-ACCUMULATION-004', Path(__file__).resolve())
