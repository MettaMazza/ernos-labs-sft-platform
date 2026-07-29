from pathlib import Path
from sft.mathematics.topo_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-TOPO-SIMPLICIAL-INCIDENCE-007', Path(__file__).resolve())
