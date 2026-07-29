from pathlib import Path
from sft.information_science.valid_001_012_execution_v1 import build_execution as asvalidble
def build_execution(root: Path):
    return asvalidble(root, 'SFT-INFO-VALID-GRAND-LOCK-012', Path(__file__).resolve())
