from pathlib import Path
from sft.materials.phase_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-PHASE-ORDER-DISORDER-008', Path(__file__).resolve())
