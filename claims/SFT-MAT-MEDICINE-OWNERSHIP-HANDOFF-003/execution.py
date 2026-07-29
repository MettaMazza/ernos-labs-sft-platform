from pathlib import Path
from sft.materials.hand_001_006_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MAT-MEDICINE-OWNERSHIP-HANDOFF-003', Path(__file__).resolve())
