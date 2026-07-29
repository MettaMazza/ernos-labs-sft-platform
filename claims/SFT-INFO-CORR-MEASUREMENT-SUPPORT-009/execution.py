from pathlib import Path
from sft.information_science.corr_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-CORR-MEASUREMENT-SUPPORT-009', Path(__file__).resolve())
