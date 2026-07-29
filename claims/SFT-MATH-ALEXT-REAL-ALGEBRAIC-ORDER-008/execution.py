from pathlib import Path
from sft.mathematics.alext_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ALEXT-REAL-ALGEBRAIC-ORDER-008', Path(__file__).resolve())
