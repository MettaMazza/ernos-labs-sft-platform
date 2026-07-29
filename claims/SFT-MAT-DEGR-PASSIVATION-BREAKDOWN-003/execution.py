from pathlib import Path
from sft.materials.degr_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-DEGR-PASSIVATION-BREAKDOWN-003', Path(__file__).resolve())
