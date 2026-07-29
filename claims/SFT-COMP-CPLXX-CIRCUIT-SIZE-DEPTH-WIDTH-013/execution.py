from pathlib import Path
from sft.computation.cplxx_001_033_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-COMP-CPLXX-CIRCUIT-SIZE-DEPTH-WIDTH-013", Path(__file__).resolve())
