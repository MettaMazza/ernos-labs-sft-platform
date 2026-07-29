from pathlib import Path
from sft.mathematics.meas_001_010_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-MEAS-FINITE-SUPPORT-INTEGRATION-005', Path(__file__).resolve())
