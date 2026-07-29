from pathlib import Path
from sft.information_science.chan_001_018_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-CHAN-DETERMINISTIC-TRANSPORT-002', Path(__file__).resolve())
