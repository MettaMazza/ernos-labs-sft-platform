from pathlib import Path
from sft.mathematics.graph_001_014_execution_v1 import build_execution as assemble
def build_execution(root: Path):
    return assemble(root, 'SFT-MATH-GRAPH-TREE-FOREST-SPANNING-004', Path(__file__).resolve())
