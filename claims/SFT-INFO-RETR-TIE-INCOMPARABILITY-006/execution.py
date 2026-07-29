from pathlib import Path
from sft.information_science.retr_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-RETR-TIE-INCOMPARABILITY-006', Path(__file__).resolve())
