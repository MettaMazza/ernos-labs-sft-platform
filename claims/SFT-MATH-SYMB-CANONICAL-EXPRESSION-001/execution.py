from pathlib import Path
from sft.mathematics.symb_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-SYMB-CANONICAL-EXPRESSION-001', Path(__file__).resolve())
