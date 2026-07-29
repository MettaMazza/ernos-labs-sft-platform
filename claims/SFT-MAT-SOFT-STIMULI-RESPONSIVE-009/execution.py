from pathlib import Path
from sft.materials.soft_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-SOFT-STIMULI-RESPONSIVE-009', Path(__file__).resolve())
