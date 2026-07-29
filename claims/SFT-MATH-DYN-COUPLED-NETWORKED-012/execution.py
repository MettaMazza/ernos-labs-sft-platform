from pathlib import Path
from sft.mathematics.dyn_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-DYN-COUPLED-NETWORKED-012', Path(__file__).resolve())
