from pathlib import Path
from sft.quantum_computation.revx_001_018_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-REVX-IRREVERSIBLE-SIMULATION-012", Path(__file__).resolve())
