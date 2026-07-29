from pathlib import Path
from sft.information_science.valid_001_012_execution_v1 import build_execution as asvalidble
def build_execution(root: Path):
    return asvalidble(root, 'SFT-INFO-VALID-NOISE-CODING-007', Path(__file__).resolve())
