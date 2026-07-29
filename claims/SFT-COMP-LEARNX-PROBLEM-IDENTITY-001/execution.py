from pathlib import Path
from sft.computation.learnx_001_026_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, 'SFT-COMP-LEARNX-PROBLEM-IDENTITY-001', Path(__file__).resolve())
