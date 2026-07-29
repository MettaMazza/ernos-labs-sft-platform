from pathlib import Path
from sft.quantum_computation.qcommx_001_024_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QCOMMX-DEVICE-INDEPENDENT-021", Path(__file__).resolve())
