from pathlib import Path
from sft.quantum_computation.qcplxx_001_026_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QCPLXX-WITNESS-VERIFY-013", Path(__file__).resolve())
