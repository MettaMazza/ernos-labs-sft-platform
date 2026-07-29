from pathlib import Path
from sft.computation.algx_001_031_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-COMP-ALGX-GREEDY-BOUNDARY-021", Path(__file__).resolve())
