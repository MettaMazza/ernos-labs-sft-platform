from pathlib import Path
from sft.information_science.symrep_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-SYMREP-PRODUCT-ALPHABET-009', Path(__file__).resolve())
