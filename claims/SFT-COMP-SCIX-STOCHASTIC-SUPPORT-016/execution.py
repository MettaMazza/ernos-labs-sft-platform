from pathlib import Path
from sft.computation.scix_001_025_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-SCIX-STOCHASTIC-SUPPORT-016', Path(__file__).resolve())
