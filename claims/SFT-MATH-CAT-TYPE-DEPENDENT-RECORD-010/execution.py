from pathlib import Path
from sft.mathematics.cat_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-CAT-TYPE-DEPENDENT-RECORD-010', Path(__file__).resolve())
