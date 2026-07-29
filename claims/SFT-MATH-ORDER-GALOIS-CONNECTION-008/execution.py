from pathlib import Path
from sft.mathematics.order_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ORDER-GALOIS-CONNECTION-008', Path(__file__).resolve())
