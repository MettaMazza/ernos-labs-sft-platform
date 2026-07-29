from pathlib import Path
from sft.information_science.hand_001_006_execution_v1 import build_execution as ashandble
def build_execution(root: Path):
    return ashandble(root, 'SFT-INFO-HAND-CROSS-BRANCH-COMPLETENESS-006', Path(__file__).resolve())
