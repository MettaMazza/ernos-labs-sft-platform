from pathlib import Path
from sft.computation.semx_001_025_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-SEMX-BIG-STEP-006', Path(__file__).resolve())
