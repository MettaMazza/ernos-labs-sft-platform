from pathlib import Path
from sft.information_science.coarse_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-COARSE-LOSS-LEDGER-006', Path(__file__).resolve())
