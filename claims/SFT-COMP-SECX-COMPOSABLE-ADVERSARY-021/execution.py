from pathlib import Path
from sft.computation.secx_001_025_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-SECX-COMPOSABLE-ADVERSARY-021', Path(__file__).resolve())
