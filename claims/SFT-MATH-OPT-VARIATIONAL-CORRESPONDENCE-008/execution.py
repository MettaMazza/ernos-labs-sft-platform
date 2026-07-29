from pathlib import Path
from sft.mathematics.opt_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-OPT-VARIATIONAL-CORRESPONDENCE-008', Path(__file__).resolve())
