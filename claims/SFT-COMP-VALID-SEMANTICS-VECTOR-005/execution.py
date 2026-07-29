from pathlib import Path
from sft.computation.valid_001_012_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-VALID-SEMANTICS-VECTOR-005', Path(__file__).resolve())
