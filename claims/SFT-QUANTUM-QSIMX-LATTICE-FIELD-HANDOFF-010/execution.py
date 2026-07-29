from pathlib import Path
from sft.quantum_computation.qsimx_001_024_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QSIMX-LATTICE-FIELD-HANDOFF-010", Path(__file__).resolve())
