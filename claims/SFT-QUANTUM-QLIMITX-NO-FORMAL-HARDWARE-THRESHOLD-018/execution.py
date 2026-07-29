from pathlib import Path
from sft.quantum_computation.qlimitx_001_022_execution_v1 import build_execution as assemble
def build_execution(root: Path): return assemble(root, "SFT-QUANTUM-QLIMITX-NO-FORMAL-HARDWARE-THRESHOLD-018", Path(__file__).resolve())
