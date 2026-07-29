from pathlib import Path
from sft.computation.distx_001_026_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-DISTX-MESSAGE-CUSTODY-004', Path(__file__).resolve())
