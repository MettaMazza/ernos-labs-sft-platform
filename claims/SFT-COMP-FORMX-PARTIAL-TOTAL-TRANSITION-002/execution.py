from pathlib import Path
from sft.computation.formx_001_022_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-COMP-FORMX-PARTIAL-TOTAL-TRANSITION-002", Path(__file__).resolve())
