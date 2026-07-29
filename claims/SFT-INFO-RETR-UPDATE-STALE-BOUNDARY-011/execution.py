from pathlib import Path
from sft.information_science.retr_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-RETR-UPDATE-STALE-BOUNDARY-011', Path(__file__).resolve())
