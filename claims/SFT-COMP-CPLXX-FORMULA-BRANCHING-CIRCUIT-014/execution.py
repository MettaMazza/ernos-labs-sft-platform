from pathlib import Path
from sft.computation.cplxx_001_033_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-COMP-CPLXX-FORMULA-BRANCHING-CIRCUIT-014", Path(__file__).resolve())
