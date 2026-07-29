from pathlib import Path
from sft.mathematics.cat_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-CAT-LIMIT-COLIMIT-006', Path(__file__).resolve())
