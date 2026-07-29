from pathlib import Path
from sft.quantum_computation.qlearnx_001_022_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QLEARNX-CLASSICAL-DATA-BOUNDARY-002", Path(__file__).resolve())
