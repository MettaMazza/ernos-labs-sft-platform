from pathlib import Path
from sft.quantum_computation.qalgx_001_030_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QALGX-RESOURCE-BOUNDS-029", Path(__file__).resolve())
