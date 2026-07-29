from pathlib import Path
from sft.information_science.priv_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-PRIV-COMPOSITION-006', Path(__file__).resolve())
