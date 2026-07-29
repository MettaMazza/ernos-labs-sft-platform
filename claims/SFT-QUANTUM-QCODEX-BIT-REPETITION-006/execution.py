from pathlib import Path
from sft.quantum_computation.qcodex_001_032_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QCODEX-BIT-REPETITION-006", Path(__file__).resolve())
