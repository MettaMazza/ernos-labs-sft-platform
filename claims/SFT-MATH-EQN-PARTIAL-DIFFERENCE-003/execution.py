from pathlib import Path
from sft.mathematics.eqn_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-EQN-PARTIAL-DIFFERENCE-003', Path(__file__).resolve())
