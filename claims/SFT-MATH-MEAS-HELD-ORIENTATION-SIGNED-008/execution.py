from pathlib import Path
from sft.mathematics.meas_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-MEAS-HELD-ORIENTATION-SIGNED-008', Path(__file__).resolve())
