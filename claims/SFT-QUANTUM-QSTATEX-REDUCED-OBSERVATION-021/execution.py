from pathlib import Path
from sft.quantum_computation.qstatex_001_028_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QSTATEX-REDUCED-OBSERVATION-021", Path(__file__).resolve())
