from pathlib import Path
from sft.mathematics.symb_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-SYMB-CONSTRUCTIVE-CERTIFICATE-010', Path(__file__).resolve())
