from pathlib import Path
from sft.computation.hand_001_006_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-HAND-OPEN-EXTENSION-005', Path(__file__).resolve())
