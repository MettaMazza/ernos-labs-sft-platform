from pathlib import Path
from sft.computation.secx_001_025_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-SECX-PSEUDORANDOM-GENERATOR-006', Path(__file__).resolve())
