from pathlib import Path
from sft.mathematics.alg_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-ALG-COMPATIBLE-ALGEBRA-PRODUCT-011', Path(__file__).resolve())
