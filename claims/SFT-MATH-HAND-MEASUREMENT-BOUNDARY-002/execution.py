from pathlib import Path
from sft.mathematics.hand_001_006_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-HAND-MEASUREMENT-BOUNDARY-002', Path(__file__).resolve())
