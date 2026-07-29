from pathlib import Path
from sft.information_science.signal_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-SIGNAL-SPATIAL-MULTIDIMENSIONAL-012', Path(__file__).resolve())
