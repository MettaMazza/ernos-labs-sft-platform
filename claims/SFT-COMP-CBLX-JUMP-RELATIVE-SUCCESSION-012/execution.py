from pathlib import Path
from sft.computation.cblx_001_021_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-COMP-CBLX-JUMP-RELATIVE-SUCCESSION-012", Path(__file__).resolve())
