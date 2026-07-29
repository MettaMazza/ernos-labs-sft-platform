from pathlib import Path
from sft.information_science.therm_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-INFO-THERM-MEMORY-RESET-006', Path(__file__).resolve())
