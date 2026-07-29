from pathlib import Path
from sft.mathematics.geom_001_016_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-GEOM-DISCRETE-LATTICE-POLYTOPE-006', Path(__file__).resolve())
