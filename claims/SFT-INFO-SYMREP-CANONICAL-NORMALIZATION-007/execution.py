from pathlib import Path
from sft.information_science.symrep_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-SYMREP-CANONICAL-NORMALIZATION-007', Path(__file__).resolve())
