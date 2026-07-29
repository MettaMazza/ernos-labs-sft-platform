from pathlib import Path
from sft.mathematics.graph_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-GRAPH-IDENTITY-ISOMORPHISM-001', Path(__file__).resolve())
